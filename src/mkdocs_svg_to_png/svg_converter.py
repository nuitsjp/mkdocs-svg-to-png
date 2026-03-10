"""Playwright を用いて SVG を PNG に変換するコンポーネント群。"""

from __future__ import annotations

import asyncio
import queue
import re
import threading
from pathlib import Path
from typing import Any, Callable

try:
    import defusedxml.ElementTree as ET
except ImportError:
    # defusedxml が利用できない場合は標準ライブラリで代替する（安全性は低下）
    import xml.etree.ElementTree as ET  # nosec B405

from .exceptions import SvgConfigError, SvgConversionError, SvgFileError
from .logging_config import get_logger
from .utils import ensure_directory


class _PlaywrightWorkerThread:
    """Playwright 操作を専用スレッドで実行するワーカー。

    Playwright sync API はスレッドに紐づくため、asyncio ループ内で使用する場合は
    起動からブラウザ操作・終了まで全操作を同一の専用スレッドで実行する必要がある。
    """

    def __init__(self) -> None:
        self._task_queue: queue.Queue[Callable[[], Any] | None] = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def submit(self, fn: Callable[[], Any]) -> Any:
        """fn を専用スレッドで実行し結果を返す。エラーは再送出する。"""
        result_event = threading.Event()
        container: dict[str, Any] = {}

        def wrapper() -> None:
            try:
                container["result"] = fn()
            except Exception as e:
                container["error"] = e
            result_event.set()

        self._task_queue.put(wrapper)
        result_event.wait()

        if "error" in container:
            raise container["error"]
        return container.get("result")

    def stop(self) -> None:
        """ワーカースレッドを停止する。"""
        self._task_queue.put(None)
        self._thread.join(timeout=10)

    def _run(self) -> None:
        """ワーカースレッドのメインループ。"""
        while True:
            task = self._task_queue.get()
            if task is None:
                break
            task()


class SvgToPngConverter:
    """Playwright を経由して SVG コンテンツを PNG へ変換するユーティリティ。

    ブラウザインスタンスを再利用し、複数画像の変換時のオーバーヘッドを削減する。
    """

    def __init__(
        self,
        config: dict[str, Any],
        runner: Callable[[str, str], bool] | None = None,
    ) -> None:
        """変換に関する設定を受け取り、ロガーと Playwright 実行環境を準備する。

        引数:
            config: 変換動作を制御する設定ディクショナリ
            runner: SVG→PNG 変換を実行する呼び出し可能オブジェクト
                （テスト用に差し替え可）
        """
        self.config = config
        self.logger = get_logger(__name__)
        self._playwright: Any | None = None
        self._browser: Any | None = None
        self._worker: _PlaywrightWorkerThread | None = None
        self._conversion_runner: Callable[[str, str], bool] = (
            runner or self._run_playwright_conversion
        )

    def convert_svg_content(self, svg_content: str, output_path: str) -> bool:
        """SVG 文字列を受け取り PNG ファイルとして出力する。

        引数:
            svg_content: SVG マークアップを含む文字列
            output_path: PNG を保存するパス

        戻り値:
            変換が成功した場合は True、失敗時は False

        例外:
            SvgConversionError: エラー時に error_on_fail が True の場合
        """
        try:
            self._validate_svg_content(svg_content)

            # 出力先ディレクトリを事前に作成する
            ensure_directory(str(Path(output_path).parent))

            # Playwright を介した実変換（テストでは差し替え可能）
            success = self._conversion_runner(svg_content, output_path)

            if success:
                self.logger.debug(f"Generated PNG image: {output_path}")
                return True
            else:
                return False

        except SvgConfigError:
            raise
        except Exception as e:
            return self._handle_conversion_error(e, output_path, svg_content)

    def convert_svg_file(self, svg_path: str, output_path: str) -> bool:
        """SVG ファイルを読み込み PNG に変換する。

        引数:
            svg_path: 入力となる SVG ファイルパス
            output_path: 出力する PNG の保存先

        戻り値:
            変換が成功した場合は True、失敗時は False

        例外:
            SvgFileError: SVG ファイルが見つからない場合
            SvgConversionError: 変換失敗時に error_on_fail が True の場合
        """
        svg_file = Path(svg_path)

        if not svg_file.exists():
            error_msg = f"SVG file not found: {svg_path}"
            self.logger.error(error_msg)
            if self.config.get("error_on_fail", True):
                raise SvgFileError(
                    "SVG file not found",
                    file_path=svg_path,
                    operation="read",
                    suggestion="Check file path exists",
                )
            return False

        try:
            svg_content = svg_file.read_text(encoding="utf-8")
        except Exception as error:
            return self._handle_conversion_error(error, output_path, "", svg_path)

        try:
            return self.convert_svg_content(svg_content, output_path)
        except SvgConfigError:
            raise
        except Exception as error:
            return self._handle_conversion_error(
                error, output_path, svg_content, svg_path
            )

    def _validate_svg_content(self, svg_content: str) -> None:
        """内容が正当な SVG かどうかを検証する。

        引数:
            svg_content: SVG マークアップを含む文字列

        例外:
            SvgConversionError: 非正当な SVG と判断された場合
        """
        try:
            # defusedxml（またはフォールバック）で XML としてパースを試みる
            ET.fromstring(svg_content)  # nosec B314

            # XML 宣言を許容しつつ <svg> タグの有無を確認する
            content_stripped = svg_content.strip()
            if not (
                content_stripped.startswith("<svg")
                or (content_stripped.startswith("<?xml") and "<svg" in content_stripped)
            ):
                raise SvgConversionError(
                    "Invalid SVG content: Must contain <svg> tag",
                    svg_content=svg_content,
                )

        except ET.ParseError as e:
            raise SvgConversionError(
                "Invalid SVG content: XML parsing failed",
                svg_content=svg_content,
                cairo_error=str(e),
            ) from e

    @staticmethod
    def _import_sync_playwright() -> Any:
        """Playwright の sync API を遅延インポートする。"""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as error:
            raise ImportError(
                "Playwright is required for SVG to PNG conversion. "
                "Install it with: pip install playwright && "
                "playwright install chromium"
            ) from error
        return sync_playwright

    @staticmethod
    def _is_inside_asyncio_loop() -> bool:
        """現在 asyncio イベントループ内で実行中かどうかを判定する。"""
        try:
            loop = asyncio.get_running_loop()
            return loop is not None and loop.is_running()
        except RuntimeError:
            return False

    def _ensure_browser(self) -> Any:
        """ブラウザインスタンスを遅延起動し、以降は再利用する。

        asyncio ループ内の場合は専用ワーカースレッドを起動し、
        Playwright の全操作をそのスレッド上で実行する。

        戻り値:
            起動済みの Playwright Browser オブジェクト
        """
        if self._browser is not None:
            return self._browser

        sync_playwright_fn = self._import_sync_playwright()

        if self._is_inside_asyncio_loop():
            # asyncio ループ内: 専用ワーカースレッドで Playwright を所有する
            self._worker = _PlaywrightWorkerThread()

            def launch() -> tuple[Any, Any]:
                pw = sync_playwright_fn().start()
                browser = pw.chromium.launch(headless=True)
                return pw, browser

            self._playwright, self._browser = self._worker.submit(launch)
        else:
            # 通常: メインスレッドで直接起動
            self._playwright = sync_playwright_fn().start()
            self._browser = self._playwright.chromium.launch(headless=True)

        self.logger.debug("Playwright ブラウザを起動しました")
        return self._browser

    def shutdown(self) -> None:
        """ブラウザと Playwright インスタンスを終了する。"""
        if self._browser is not None:
            if self._worker:
                self._worker.submit(lambda: self._browser.close())  # type: ignore[union-attr]
            else:
                self._browser.close()
            self._browser = None
        if self._playwright is not None:
            if self._worker:
                self._worker.submit(lambda: self._playwright.stop())  # type: ignore[union-attr]
            else:
                self._playwright.stop()
            self._playwright = None
            self.logger.debug("Playwright ブラウザを終了しました")
        if self._worker is not None:
            self._worker.stop()
            self._worker = None

    def _convert_svg_with_playwright(self, svg_content: str, output_path: str) -> bool:
        """Playwright を利用して SVG を PNG に描画する。

        ブラウザインスタンスを再利用し、ページの作成・破棄のみで変換する。
        ワーカースレッドが存在する場合は、全操作をそのスレッド上で実行する。

        引数:
            svg_content: SVG マークアップを含む文字列
            output_path: PNG を保存するパス

        戻り値:
            変換が成功した場合は True、それ以外は False
        """
        browser = self._ensure_browser()

        if self._worker:
            result: bool = self._worker.submit(
                lambda: self._do_convert(browser, svg_content, output_path)
            )
            return result
        return self._do_convert(browser, svg_content, output_path)

    def _do_convert(self, browser: Any, svg_content: str, output_path: str) -> bool:
        """実際の変換処理を行う。ブラウザ操作はこのメソッド内で完結する。"""
        context = browser.new_context(
            device_scale_factor=self.config.get("device_scale_factor", 1.0)
        )
        page = context.new_page()

        try:
            # SVG の描画サイズを解析する
            width, height = self._extract_svg_dimensions(svg_content)

            # 設定されたスケールを掛け合わせる
            scale = self.config.get("scale", 1.0)
            scaled_width = int(width * scale)
            scaled_height = int(height * scale)

            # ビューポートを SVG サイズに合わせる
            page.set_viewport_size({"width": scaled_width, "height": scaled_height})

            # SVG を埋め込んだ HTML を生成する
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        margin: 0;
                        padding: 0;
                        width: {scaled_width}px;
                        height: {scaled_height}px;
                    }}
                    svg {{
                        width: 100%;
                        height: 100%;
                    }}
                </style>
            </head>
            <body>
                {svg_content}
            </body>
            </html>
            """

            # HTML をページに読み込む
            page.set_content(html_content)

            # SVG の描画完了を待機する
            page.wait_for_load_state("networkidle")

            # 背景透過のスクリーンショットとして PNG を取得する
            page.screenshot(path=output_path, full_page=True, omit_background=True)

            return True

        finally:
            context.close()

    def _extract_svg_dimensions(self, svg_content: str) -> tuple[int, int]:
        """SVG コンテンツから幅と高さを抽出する。

        引数:
            svg_content: SVG マークアップを含む文字列

        戻り値:
            ピクセル単位の (width, height) タプル
        """
        # 設定で上書き可能なデフォルト寸法
        default_width = self.config.get("default_width", 800)
        default_height = self.config.get("default_height", 600)

        try:
            # SVG コンテンツをパースする
            root = ET.fromstring(svg_content)

            # width / height 属性を優先的に参照する
            width_attr = root.get("width")
            height_attr = root.get("height")

            if width_attr and height_attr:
                # 数値部分を抽出して正規化する
                width = self._parse_dimension(width_attr, default_width)
                height = self._parse_dimension(height_attr, default_height)
                return width, height

            # viewBox が存在する場合は右下座標を寸法として採用する
            viewbox = root.get("viewBox")
            if viewbox:
                parts = viewbox.split()
                if len(parts) == 4:
                    width = int(float(parts[2]))
                    height = int(float(parts[3]))
                    return width, height

        except Exception as e:
            self.logger.warning(f"Failed to extract SVG dimensions: {e}")

        return default_width, default_height

    def _parse_dimension(self, dimension_str: str, default: int) -> int:
        """寸法を表す文字列を整数ピクセル値へ変換する。

        引数:
            dimension_str: 寸法文字列（例: "100px", "100", "10em"）
            default: 解析に失敗した場合に用いる既定値

        戻り値:
            ピクセル単位の整数値
        """
        try:
            # 単位を取り除いて数値部分のみ抽出する
            numeric_match = re.match(r"([0-9.]+)", dimension_str)
            if numeric_match:
                return int(float(numeric_match.group(1)))
        except (ValueError, AttributeError):
            pass

        return default

    def _run_playwright_conversion(self, svg_content: str, output_path: str) -> bool:
        """Playwright 変換を実行する。

        引数:
            svg_content: SVG マークアップを含む文字列
            output_path: PNG を保存するパス

        戻り値:
            変換が成功した場合は True、失敗時は False
        """
        try:
            return self._convert_svg_with_playwright(svg_content, output_path)
        except Exception as e:
            if self._is_playwright_browser_missing_error(e):
                raise SvgConfigError(
                    "Playwright browser is not installed",
                    suggestion="Run: playwright install chromium",
                ) from e
            self.logger.error(f"Playwright conversion failed: {e}")
            return False

    @staticmethod
    def _is_playwright_browser_missing_error(error: Exception) -> bool:
        message = str(error).lower()
        needles = (
            "executable doesn't exist",
            "playwright install",
            "headless_shell.exe",
            "chromium_headless_shell",
        )
        return any(needle in message for needle in needles)

    def _handle_conversion_error(
        self,
        error: Exception,
        output_path: str,
        svg_content: str,
        svg_path: str | None = None,
    ) -> bool:
        """変換時に発生した例外を設定方針に従って処理する。

        引数:
            error: 発生した例外オブジェクト
            output_path: 変換先の出力パス
            svg_content: 変換に失敗した SVG 内容
            svg_path: 元となる SVG ファイルパス（ファイル変換時のみ）

        戻り値:
            error_on_fail が False の場合は False を返す

        例外:
            SvgConversionError: error_on_fail が True の場合
        """
        if isinstance(
            error, SvgConfigError
        ) or self._is_playwright_browser_missing_error(error):
            raise SvgConfigError(
                "Playwright browser is not installed",
                suggestion="Run: playwright install chromium",
            ) from error

        error_msg = f"Playwright conversion failed: {error}"
        self.logger.error(error_msg)

        if self.config.get("error_on_fail", True):
            raise SvgConversionError(
                "Playwright conversion failed",
                svg_path=svg_path,
                output_path=output_path,
                svg_content=svg_content,
                cairo_error=str(error),
            ) from error

        return False
