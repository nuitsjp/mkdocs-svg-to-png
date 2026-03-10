import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Optional

from mkdocs.plugins import BasePlugin

if TYPE_CHECKING:
    from mkdocs.structure.files import Files

from .config import SvgConfigManager
from .exceptions import (
    SvgConfigError,
    SvgConversionError,
    SvgFileError,
    SvgValidationError,
)
from .logging_config import get_logger, setup_plugin_logging
from .processor import SvgProcessor
from .utils import clean_generated_images


class SvgToPngPlugin(BasePlugin):  # type: ignore[type-arg,no-untyped-call]
    """Markdown 内の SVG を PNG へ変換する MkDocs プラグイン本体。"""

    config_scheme = SvgConfigManager.get_config_scheme()

    def __init__(self) -> None:
        """処理器や生成物のトラッキング状態を初期化する。"""
        super().__init__()
        self.processor: Optional[SvgProcessor] = None
        self.generated_images: list[str] = []
        self.files: Optional[Files] = None
        self.logger = get_logger(__name__)

        self.enabled: bool | None = None

        self.is_serve_mode: bool = False

    def _determine_enabled(self, config: dict[str, Any]) -> bool:
        """設定と環境変数から有効化可否を決定する。"""
        enabled_if_env = self._config_lookup(config, "enabled_if_env")

        if enabled_if_env is not None:
            env_value = os.environ.get(enabled_if_env)
            return env_value is not None and env_value.strip() != ""

        return True

    def _should_be_enabled(self, config: dict[str, Any]) -> bool:
        """一度算出した有効化状態をキャッシュして返す。"""
        if self.enabled is None:
            self.enabled = self._determine_enabled(config)

        return self.enabled

    def on_startup(
        self, *, command: Literal["build", "gh-deploy", "serve"], dirty: bool
    ) -> None:
        """MkDocs起動時のコマンドに応じて配信モードを設定する。"""
        del dirty
        self.is_serve_mode = command == "serve"

    def on_config(self, config: Any) -> Any:
        """設定読み込み時にログや処理器を初期化し、動作可否を判断する。"""
        try:
            config_dict = dict(self.config)
            SvgConfigManager().validate(config_dict)

            # ルートロガーが DEBUG の場合は詳細ログを優先する
            if self._root_logger_requests_debug():
                config_dict["log_level"] = "DEBUG"
            # else: config_dictのlog_levelをそのまま使用

            # ログフォーマットの設定を適用（常にSimpleFormatter使用）
            setup_plugin_logging(level=config_dict.get("log_level", "INFO"), force=True)

            self.enabled = self._should_be_enabled(config_dict)

            if not self.enabled:
                self.logger.info("svg-to-png plugin is disabled")
                self.processor = None
                return config

            self.processor = SvgProcessor(config_dict)

            self.logger.info("svg-to-png plugin initialized")

        except (SvgConfigError, SvgFileError) as e:
            self.logger.error(f"Configuration error: {e!s}")
            raise
        except FileNotFoundError as e:
            self.logger.error(f"Required file not found: {e!s}")
            raise SvgFileError(
                f"Required file not found during plugin initialization: {e!s}",
                operation="read",
                suggestion="Ensure all required files exist",
            ) from e
        except (OSError, PermissionError) as e:
            self.logger.error(f"File system error: {e!s}")
            raise SvgFileError(
                f"File system error during plugin initialization: {e!s}",
                operation="access",
                suggestion="Check file permissions and disk space",
            ) from e
        except Exception as e:
            self.logger.error(f"Unexpected error during plugin initialization: {e!s}")
            raise SvgConfigError(f"Plugin configuration error: {e!s}") from e

        return config

    def on_files(self, files: Any, *, config: Any) -> Any:
        """ビルド対象ファイル一覧を受け取り、生成物を追加できるよう保持する。"""
        if not self._should_be_enabled(self.config) or not self.processor:
            return files

        # Filesオブジェクトを保存
        self.files = files
        self.generated_images = []

        return files

    def _register_generated_images_to_files(
        self, image_paths: list[str], docs_dir: Path, config: Any
    ) -> None:
        """生成された画像を Files オブジェクトに追加する。"""
        if not (image_paths and self.files):
            return

        from mkdocs.structure.files import File

        for image_path in image_paths:
            image_file_path = Path(image_path)
            if not image_file_path.exists():
                self.logger.warning(
                    f"Generated image file does not exist: {image_path}"
                )
                continue

            try:
                # docs_dirからの相対パスを計算
                rel_path = image_file_path.relative_to(docs_dir)
                rel_path_str = str(rel_path)

                # 既存のファイルを効率的に検索して削除（重複回避）
                self._remove_existing_file_by_path(rel_path_str)

                # 新しいファイルオブジェクトを作成してFilesに追加
                file_obj = File(
                    rel_path_str,
                    str(docs_dir),
                    str(config["site_dir"]),
                    use_directory_urls=config.get("use_directory_urls", True),
                )
                self.files.append(file_obj)

            except ValueError as e:
                self.logger.error(f"Error processing image path {image_path}: {e}")
                continue

    def _remove_existing_file_by_path(self, src_path: str) -> bool:
        """指定された src_path を持つ既存エントリを削除する。

        引数:
            src_path: 削除対象の src_path

        戻り値:
            削除された場合は True、見つからなければ False
        """
        if self.files is None:
            return False

        for file_obj in self.files:
            if file_obj.src_path == src_path:
                self.files.remove(file_obj)
                return True
        return False

    def _process_svg_diagrams(
        self, markdown: str, page: Any, config: Any
    ) -> Optional[str]:
        """単一ページの SVG ブロック検出から PNG 生成・差し替えを行う。"""
        if not self.processor:
            return markdown

        try:
            # ソース側のdocsディレクトリ内に画像を生成
            docs_dir = Path(config["docs_dir"])
            output_dir = docs_dir / self.config["output_dir"]

            modified_content, image_paths = self.processor.process_page(
                page.file.src_path,
                markdown,
                output_dir,
                docs_dir=docs_dir,
            )

            self.generated_images.extend(image_paths)

            # 生成された画像をFilesオブジェクトに追加
            self._register_generated_images_to_files(image_paths, docs_dir, config)

            # 画像を生成した場合、常にINFOレベルでログを出力
            if image_paths:
                self.logger.info(
                    f"Generated {len(image_paths)} images from SVG for "
                    f"{page.file.src_path}"
                )

            return modified_content

        except SvgConversionError as e:
            self.logger.error(f"Error processing {page.file.src_path}: {e!s}")
            if self.config["error_on_fail"]:
                raise
            return markdown

        except (FileNotFoundError, OSError, PermissionError) as e:
            self.logger.error(
                f"File system error processing {page.file.src_path}: {e!s}"
            )
            if self.config["error_on_fail"]:
                raise SvgFileError(
                    f"File system error processing {page.file.src_path}: {e!s}",
                    file_path=page.file.src_path,
                    operation="process",
                    suggestion="Check file permissions and ensure output "
                    "directory exists",
                ) from e
            return markdown
        except ValueError as e:
            self.logger.error(
                f"Validation error processing {page.file.src_path}: {e!s}"
            )
            if self.config["error_on_fail"]:
                raise SvgValidationError(
                    f"Validation error processing {page.file.src_path}: {e!s}",
                    validation_type="page_processing",
                    invalid_value=page.file.src_path,
                ) from e
            return markdown
        except Exception as e:
            self.logger.error(
                f"Unexpected error processing {page.file.src_path}: {e!s}"
            )
            if self.config["error_on_fail"]:
                raise SvgConversionError(f"Unexpected error: {e!s}") from e
            return markdown

    def on_page_markdown(
        self, markdown: str, *, page: Any, config: Any, files: Any
    ) -> Optional[str]:
        """ページ単位で Markdown を処理し、SVG を PNG 参照に置き換える。"""
        if not self._should_be_enabled(self.config):
            return markdown

        if self.is_serve_mode:
            return markdown

        return self._process_svg_diagrams(markdown, page, config)

    def on_post_build(self, *, config: Any) -> None:
        """ビルド後にブラウザ終了・生成画像の集計・クリーンアップを行う。"""
        # ブラウザインスタンスを確実に終了する
        if self.processor:
            self.processor.svg_converter.shutdown()

        if not self._should_be_enabled(self.config):
            return

        # 生成した画像の総数をINFOレベルで出力
        if self.generated_images:
            self.logger.info(
                f"Generated {len(self.generated_images)} images from SVG total"
            )

        # 生成画像のクリーンアップ
        if self.config.get("cleanup_generated_images", False) and self.generated_images:
            clean_generated_images(self.generated_images, self.logger)

    def on_serve(self, server: Any, *, config: Any, builder: Any) -> Any:
        """`mkdocs serve` 時に特別な処理は行わず、サーバーをそのまま返す。"""
        self.is_serve_mode = True
        if not self._should_be_enabled(self.config):
            return server

        return server

    def _root_logger_requests_debug(self) -> bool:
        """ルートロガーの設定からデバッグログ要求を検出する。"""
        root_logger = logging.getLogger()
        effective_level = root_logger.getEffectiveLevel()
        if effective_level == logging.NOTSET:
            # NOTSET は親ロガー依存のため明示的な要求とみなさない
            return False
        return effective_level <= logging.DEBUG

    def _config_lookup(self, config: Any, key: str, default: Any = None) -> Any:
        """MkDocsConfig 互換オブジェクトから値を取得するヘルパー。"""
        if isinstance(config, dict):
            return config.get(key, default)

        try:
            return config[key]
        except Exception:  # pragma: no cover - フォールバック
            getter = getattr(config, "get", None)
            if callable(getter):
                try:
                    return getter(key, default)
                except TypeError:
                    try:
                        return getter(key)
                    except Exception:  # pragma: no cover - フォールバック
                        return default
            return default
