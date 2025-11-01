from __future__ import annotations

import contextlib
import logging
import os
import platform
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from collections.abc import MutableMapping

from .types import LogContext


class StructuredFormatter(logging.Formatter):
    """構造化されたキー=値形式でログを出力するフォーマッタ。"""

    def __init__(self, include_caller: bool = True) -> None:
        super().__init__()
        self.include_caller = include_caller

    def format(self, record: logging.LogRecord) -> str:
        import time

        # 基本的なログエントリを構築
        parts = []

        # タイムスタンプ
        parts.append(f"timestamp={time.time()}")

        # ログレベル
        parts.append(f"level={record.levelname}")

        # ロガー名
        parts.append(f"logger={record.name}")

        # メッセージ
        parts.append(f"message={record.getMessage()}")

        # 呼び出し元情報
        if self.include_caller and hasattr(record, "pathname"):
            filename = Path(record.pathname).name if record.pathname else "unknown"
            func_name = getattr(record, "funcName", getattr(record, "func", "unknown"))
            line_no = getattr(record, "lineno", 0)
            parts.append(f"caller={filename}:{func_name}:{line_no}")

        # 例外情報
        if record.exc_info:
            exc_type = (
                record.exc_info[0].__name__ if record.exc_info[0] else "Exception"
            )
            parts.append(f"exception={exc_type}")

        # コンテキスト情報
        if hasattr(record, "context"):
            context = getattr(record, "context", None)
            if context and isinstance(context, dict):
                for key, value in context.items():
                    parts.append(f"{key}={value}")

        return " ".join(parts)


class SimpleFormatter(logging.Formatter):
    """MkDocs に合わせたシンプルな整形を行うフォーマッタ。"""

    # レベル表記の桁揃えを統一するマッピング
    LEVEL_FORMAT_MAP: ClassVar[dict[str, str]] = {
        "INFO": "INFO    ",
        "WARNING": "WARNING ",
        "ERROR": "ERROR   ",
        "DEBUG": "DEBUG   ",
        "CRITICAL": "CRITICAL",
    }

    def format(self, record: logging.LogRecord) -> str:
        """MkDocs 風の整形でログメッセージを構築する。

        引数:
            record: 整形対象のログレコード

        戻り値:
            整形済みのログ文字列
        """
        level = record.levelname
        message = record.getMessage()

        # 既定の整形か、存在しないレベル名は桁揃えで補正する
        level_str = self.LEVEL_FORMAT_MAP.get(level, f"{level:<8}")

        return f"{level_str}-  {message}"


def setup_plugin_logging(
    *,
    level: str = "INFO",
    log_file: str | Path | None = None,
    force: bool = False,
) -> None:
    """プラグイン用のロガーをシンプルな整形で初期化する。

    引数:
        level: ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        log_file: ログを出力するファイルパス（省略可）
        force: 既存ハンドラがあっても再初期化するかどうか
    """
    env_level = os.environ.get("MKDOCS_SVG_TO_PNG_LOG_LEVEL", "").upper()
    if env_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        level = env_level

    logger = logging.getLogger("mkdocs_svg_to_png")

    if logger.handlers and not force:
        return

    if force:
        logger.handlers.clear()

    logger.setLevel(getattr(logging, level.upper()))

    # 常に SimpleFormatter を使用し、普段使いの出力を統一する
    formatter = SimpleFormatter()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    class EphemeralFileHandler(logging.FileHandler):
        """Emit毎にファイルを開閉して Windows の一時ディレクトリロック問題を軽減"""

        def emit(self, record: logging.LogRecord) -> None:
            stream = self._open()
            self.stream = stream
            try:
                super().emit(record)
            finally:
                if stream:
                    with contextlib.suppress(Exception):
                        stream.close()
                # Note: logging.FileHandlerの基底クラスが期待する通り、
                # streamをNoneにする必要があるが、型チェッカーを満足させるため
                # 以下の行は型チェックを無効にする
                self.stream = None  # type: ignore[assignment]

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        use_ephemeral = platform.system().lower().startswith("win")
        handler_cls: type[logging.FileHandler] = (
            EphemeralFileHandler if use_ephemeral else logging.FileHandler
        )

        file_handler = handler_cls(log_path, encoding="utf-8")
        file_handler.setLevel(getattr(logging, level.upper()))
        # ファイル出力もコンソールと同じ整形に揃える
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.log(getattr(logging, level.upper()), "Log file initialized")

    logger.propagate = False


def get_plugin_logger(
    name: str, **context: Any
) -> logging.Logger | logging.LoggerAdapter[logging.Logger]:
    """プラグイン固有のコンテキスト情報を付加するロガーを取得する。"""
    logger = logging.getLogger(name)

    if context:

        class ContextAdapter(logging.LoggerAdapter[logging.Logger]):
            """追加コンテキストを `extra` に統合するアダプタ。"""

            def process(
                self, msg: str, kwargs: MutableMapping[str, Any]
            ) -> tuple[str, MutableMapping[str, Any]]:
                if "extra" not in kwargs:
                    kwargs["extra"] = {}
                if "context" not in kwargs["extra"]:
                    kwargs["extra"]["context"] = {}
                kwargs["extra"]["context"].update(self.extra)
                return msg, kwargs

        return ContextAdapter(logger, context)

    return logger


def log_with_context(
    logger: logging.Logger, level: str, message: str, **context: Any
) -> None:
    """レベルを文字列で指定し、追加コンテキスト付きでログ出力する。"""
    log_method = getattr(logger, level.lower())
    log_method(message, extra={"context": context})


def create_processing_context(
    page_file: str | None = None,
    block_index: int | None = None,
) -> LogContext:
    """Markdown ページ処理時の位置情報を含むコンテキストを生成する。"""
    return LogContext(page_file=page_file, block_index=block_index)


def create_error_context(
    error_type: str | None = None,
    processing_step: str | None = None,
) -> LogContext:
    """エラー種別とステップ名を含むログコンテキストを生成する。"""
    return LogContext(error_type=error_type, processing_step=processing_step)


def create_performance_context(
    execution_time_ms: float | None = None,
    image_format: str | None = None,
) -> LogContext:
    """処理時間などの性能指標を記録するコンテキストを生成する。"""
    context: LogContext = {"execution_time_ms": execution_time_ms}
    if image_format is not None and image_format in ("png", "svg"):
        context["image_format"] = image_format  # type: ignore[typeddict-item]
    return context


# setup_plugin_logging()を削除して自動初期化を無効化


def get_logger(name: str) -> logging.Logger:
    """全モジュール共通で利用するロガーを取得するファクトリ関数。

    引数:
        name: ロガー名（通常は __name__ を渡す）

    戻り値:
        設定済みロガーのインスタンス
    """
    # プラグインロギングがセットアップされていない場合は初期化
    root_logger = logging.getLogger("mkdocs_svg_to_png")
    if not root_logger.handlers:
        setup_plugin_logging()

    return logging.getLogger(name)


def shutdown_logging() -> None:
    """全ハンドラを flush/close し、特に Windows テスト時のロックを避ける。"""
    root_logger = logging.getLogger("mkdocs_svg_to_png")
    for h in list(
        root_logger.handlers
    ):  # リストをコピーしてイテレーション中の変更を防ぐ
        with contextlib.suppress(Exception):
            h.flush()
        with contextlib.suppress(Exception):
            h.close()
