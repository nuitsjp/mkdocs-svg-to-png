"""Playwright を用いて SVG を PNG に変換するコンポーネント群。"""

from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Any

try:
    import defusedxml.ElementTree as ET
except ImportError:
    # defusedxml が利用できない場合は標準ライブラリで代替する（安全性は低下）
    import xml.etree.ElementTree as ET  # nosec B405

from .exceptions import SvgConversionError, SvgFileError
from .logging_config import get_logger
from .utils import ensure_directory


class SvgToPngConverter:
    """Playwright を経由して SVG コンテンツを PNG へ変換するユーティリティ。"""

    def __init__(self, config: dict[str, Any]) -> None:
        """変換に関する設定を受け取り、ロガーと Playwright 実行環境を準備する。

        引数:
            config: 変換動作を制御する設定ディクショナリ
        """
        self.config = config
        self.logger = get_logger(__name__)
        self._async_playwright: Any | None = None

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

            # Playwright を介して SVG→PNG へ変換する
            success = self._run_playwright_conversion(svg_content, output_path)

            if success:
                self.logger.debug(f"Generated PNG image: {output_path}")
                return True
            else:
                return False

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

    async def _convert_svg_with_playwright(
        self, svg_content: str, output_path: str
    ) -> bool:
        """Playwright を利用して SVG を PNG に描画する非同期処理を実行する。

        背景設定は下記の方針で保持される:
        - SVG が透過背景を明示していれば PNG も透過のまま出力する
        - SVG が背景色を指定していれば同じ色を反映する
        - 背景指定がない場合は PNG を透過背景で出力する

        引数:
            svg_content: SVG マークアップを含む文字列
            output_path: PNG を保存するパス

        戻り値:
            変換が成功した場合は True、それ以外は False
        """
        async_playwright = self._get_async_playwright()

        async with async_playwright() as p:
            # Chromium ブラウザを起動する
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                device_scale_factor=self.config.get("device_scale_factor", 1.0)
            )
            page = await context.new_page()

            try:
                # SVG の描画サイズを解析する
                width, height = self._extract_svg_dimensions(svg_content)

                # 設定されたスケールを掛け合わせる
                scale = self.config.get("scale", 1.0)
                scaled_width = int(width * scale)
                scaled_height = int(height * scale)

                # ビューポートを SVG サイズに合わせる
                await page.set_viewport_size(
                    {"width": scaled_width, "height": scaled_height}
                )

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
                await page.set_content(html_content)

                # SVG の描画完了を待機する
                await page.wait_for_load_state("networkidle")

                # 背景透過のスクリーンショットとして PNG を取得する
                await page.screenshot(
                    path=output_path, full_page=True, omit_background=True
                )

                return True

            finally:
                await browser.close()

    def _get_async_playwright(self) -> Any:
        """Playwright の非同期 API を遅延インポートし、
        モジュール不在時の例外を避ける。"""
        if self._async_playwright is None:
            try:
                from playwright.async_api import async_playwright as playwright_loader
            except ImportError as error:
                raise ImportError(
                    "Playwright is required for SVG to PNG conversion. "
                    "Install it with: pip install playwright && "
                    "playwright install chromium"
                ) from error
            self._async_playwright = playwright_loader
        return self._async_playwright

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
        """Playwright 変換を実行し、非同期イベントループの状態を調停する。

        引数:
            svg_content: SVG マークアップを含む文字列
            output_path: PNG を保存するパス

        戻り値:
            変換が成功した場合は True、失敗時は False
        """
        try:
            # 既存イベントループ上で動作しているかを確認する
            try:
                loop = asyncio.get_running_loop()
                if loop and loop.is_running():
                    # 現行ループ内であれば別スレッドに専用ループを立ち上げる
                    import threading

                    result_container = {}
                    exception_container = {}

                    def run_in_new_loop() -> None:
                        try:
                            # スレッド専用のイベントループを生成して処理する
                            new_loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(new_loop)
                            try:
                                result = new_loop.run_until_complete(
                                    self._convert_svg_with_playwright(
                                        svg_content, output_path
                                    )
                                )
                                result_container["success"] = result
                            finally:
                                new_loop.close()
                        except Exception as e:
                            exception_container["error"] = e

                    thread = threading.Thread(target=run_in_new_loop)
                    thread.start()
                    thread.join()

                    if "error" in exception_container:
                        raise exception_container["error"]

                    return result_container.get("success", False)
                else:
                    # イベントループ自体は存在するが未稼働の場合
                    return asyncio.run(
                        self._convert_svg_with_playwright(svg_content, output_path)
                    )
            except RuntimeError:
                # イベントループが存在しないため asyncio.run を直接利用する
                return asyncio.run(
                    self._convert_svg_with_playwright(svg_content, output_path)
                )
        except Exception as e:
            self.logger.error(f"Playwright conversion failed: {e}")
            return False

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
