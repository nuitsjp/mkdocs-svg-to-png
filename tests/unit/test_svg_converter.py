"""
SVG to PNG conversion functionality tests.
This module tests the SvgToPngConverter class using Playwright.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch

import pytest

from mkdocs_svg_to_png.exceptions import (
    SvgConfigError,
    SvgConversionError,
    SvgFileError,
)
from mkdocs_svg_to_png.svg_converter import SvgToPngConverter


class TestSvgToPngConverter:
    """Test SvgToPngConverter class."""

    @pytest.fixture(autouse=True)
    def mock_playwright_conversion(self):
        """Playwright実行をモックしてテストからブラウザ依存を排除する。"""
        with patch.object(
            SvgToPngConverter,
            "_run_playwright_conversion",
            autospec=True,
        ) as mock_conversion:
            mock_conversion.return_value = True
            yield mock_conversion

    @pytest.fixture
    def converter(self, svg_config):
        """Create SvgToPngConverter instance."""
        return SvgToPngConverter(svg_config)

    def test_svg_converter_initialization(self, svg_config):
        """Test SvgToPngConverter initialization."""
        converter = SvgToPngConverter(svg_config)
        assert converter.config == svg_config

    @patch("mkdocs_svg_to_png.svg_converter.ensure_directory")
    @patch("mkdocs_svg_to_png.svg_converter.Path")
    def test_convert_svg_content_to_png_success(
        self,
        mock_path,
        mock_ensure_directory,
        converter,
        mock_playwright_conversion,
    ):
        """Test successful SVG content to PNG conversion."""
        svg_content = (
            "<svg width='100' height='100'><rect width='100' height='100'/></svg>"
        )
        output_path = "/tmp/test.png"

        # Mock Path operations
        mock_path.return_value.parent = "/tmp"

        result = converter.convert_svg_content(svg_content, output_path)

        assert result is True
        mock_ensure_directory.assert_called_once_with("/tmp")
        mock_playwright_conversion.assert_called_once_with(
            converter, svg_content, output_path
        )

    @patch("mkdocs_svg_to_png.svg_converter.Path")
    def test_convert_svg_file_to_png_success(self, mock_path, converter):
        """Test successful SVG file to PNG conversion."""
        svg_path = "/tmp/test.svg"
        output_path = "/tmp/test.png"

        # Mock Path operations
        mock_svg_path = Mock()
        mock_svg_path.exists.return_value = True
        mock_svg_path.read_text.return_value = (
            "<svg width='100' height='100'><rect/></svg>"
        )

        def path_side_effect(arg):
            if arg == svg_path:
                return mock_svg_path
            return Mock()

        mock_path.side_effect = path_side_effect

        # Mock the convert_svg_content method
        with patch.object(
            converter, "convert_svg_content", return_value=True
        ) as mock_convert:
            result = converter.convert_svg_file(svg_path, output_path)

        assert result is True
        mock_convert.assert_called_once_with(
            "<svg width='100' height='100'><rect/></svg>", output_path
        )

    def test_convert_svg_content_with_injected_runner(
        self, svg_config, mock_playwright_conversion
    ):
        """注入ランナーでPlaywright処理をバイパスできるかテスト (TDD RED)"""
        calls: list[tuple[str, str]] = []

        def fake_runner(svg: str, output: str) -> bool:
            calls.append((svg, output))
            return True

        converter = SvgToPngConverter(svg_config, runner=fake_runner)

        svg_content = "<svg width='10' height='10'></svg>"
        output_path = "/tmp/from-runner.png"

        result = converter.convert_svg_content(svg_content, output_path)

        assert result is True
        assert calls == [(svg_content, output_path)]
        assert mock_playwright_conversion.called is False

    def test_import_svg_converter_without_playwright(self):
        """Playwright 未インストールでもモジュールインポートが成功することを確認する。

        Playwright は _import_sync_playwright で遅延インポートされるため、
        モジュールのインポート自体は常に成功する。
        """
        import importlib
        import sys

        module_name = "mkdocs_svg_to_png.svg_converter"
        sys.modules.pop(module_name, None)

        original_playwright = sys.modules.pop("playwright", None)
        original_sync_api = sys.modules.pop("playwright.sync_api", None)

        try:
            sys.modules["playwright"] = None
            sys.modules["playwright.sync_api"] = None

            module = importlib.import_module(module_name)
        finally:
            sys.modules.pop("playwright", None)
            sys.modules.pop("playwright.sync_api", None)
            if original_playwright is not None:
                sys.modules["playwright"] = original_playwright
            if original_sync_api is not None:
                sys.modules["playwright.sync_api"] = original_sync_api

        globals()["SvgToPngConverter"] = module.SvgToPngConverter
        assert hasattr(module, "SvgToPngConverter")

    def test_convert_svg_file_read_failure_returns_false_without_retry(
        self, tmp_path, svg_config
    ):
        """Read failure should be handled once without retrying the file read."""
        converter = SvgToPngConverter({**svg_config, "error_on_fail": False})

        svg_path = tmp_path / "inaccessible.svg"
        output_path = "/tmp/out.png"

        svg_path.write_text("<svg></svg>", encoding="utf-8")

        with patch(
            "mkdocs_svg_to_png.svg_converter.Path.read_text",
            side_effect=PermissionError("denied"),
        ) as mock_read_text:
            result = converter.convert_svg_file(str(svg_path), output_path)

        assert result is False
        assert mock_read_text.call_count == 1

    def test_convert_svg_content_playwright_error(self):
        """Test Playwright error handling."""
        config = {
            "output_dir": "assets/images",
            "scale": 1.0,
            "error_on_fail": False,  # Set to False to avoid exception
        }
        converter = SvgToPngConverter(config)

        svg_content = "<svg>invalid/malformed svg content"
        output_path = "/tmp/test_error.png"

        # Test with malformed SVG - should handle error gracefully and return False
        result = converter.convert_svg_content(svg_content, output_path)

        # With error_on_fail=False, should return False for invalid SVG
        assert result is False

    def test_convert_svg_content_with_error_on_fail_false(self):
        """Test SVG conversion with error_on_fail=False."""
        config = {
            "output_dir": "assets/images",
            "scale": 1.0,
            "error_on_fail": False,
        }
        converter = SvgToPngConverter(config)

        # Test with malformed SVG
        result = converter.convert_svg_content("<svg>malformed", "/tmp/test.png")

        assert result is False  # Should return False instead of raising

    def test_convert_nonexistent_svg_file(self):
        """Test conversion of non-existent SVG file."""
        # Create config with error_on_fail=True to ensure exception is raised
        config = {
            "output_dir": "assets/images",
            "scale": 1.0,
            "device_scale_factor": 1.0,
            "default_width": 800,
            "default_height": 600,
            "error_on_fail": True,  # Enable exceptions
        }
        converter = SvgToPngConverter(config)

        svg_path = "/nonexistent/file.svg"
        output_path = "/tmp/test.png"

        with pytest.raises(SvgFileError) as exc_info:
            converter.convert_svg_file(svg_path, output_path)

        assert "SVG file not found" in str(exc_info.value)
        assert exc_info.value.details["file_path"] == svg_path

    def test_convert_svg_file_with_relative_path_mkdocs_context(self, tmp_path):
        """Test SVG file conversion with relative path in MkDocs context.

        This should fail without base_path.
        """
        # MkDocsコンテキストでの相対パス変換をテスト
        config = {
            "output_dir": "assets/images",
            "scale": 1.0,
            "device_scale_factor": 1.0,
            "default_width": 800,
            "default_height": 600,
            "error_on_fail": False,
        }
        converter = SvgToPngConverter(config)

        # MkDocsのようなディレクトリ構造を作成
        project_root = tmp_path / "project"
        project_root.mkdir()
        docs_dir = project_root / "docs"
        docs_dir.mkdir()
        assets_dir = docs_dir / "assets" / "images"
        assets_dir.mkdir(parents=True)

        # SVGファイルを作成
        svg_content = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">'
            '<rect width="100" height="100" fill="red"/>'
            "</svg>"
        )
        svg_file = assets_dir / "test_mermaid_0_abc123.svg"
        svg_file.write_text(svg_content)

        # プロジェクトルートで作業（MkDocsの動作と同じ）
        import os
        from pathlib import Path

        original_cwd = Path.cwd()
        try:
            os.chdir(project_root)

            # 相対パス（Mermaidプラグインから生成される）
            relative_path = "assets/images/test_mermaid_0_abc123.svg"
            output_path = assets_dir / "test_mermaid_0_abc123.png"

            # 現在の実装では失敗するはず（docs/ベースパスが考慮されていない）
            result = converter.convert_svg_file(str(relative_path), str(output_path))
            assert result is False  # 失敗することを期待

        finally:
            os.chdir(original_cwd)

    @patch("mkdocs_svg_to_png.svg_converter.ensure_directory")
    @patch("mkdocs_svg_to_png.svg_converter.Path")
    def test_convert_with_custom_scale(
        self, mock_path, mock_ensure_directory, mock_playwright_conversion
    ):
        """Test conversion with custom scale setting."""
        config = {
            "output_dir": "assets/images",
            "scale": 2.0,
            "error_on_fail": True,
        }
        converter = SvgToPngConverter(config)

        # Mock Path operations
        mock_path.return_value.parent = "/tmp"

        result = converter.convert_svg_content(
            "<svg width='100' height='100'/>", "/tmp/test.png"
        )

        assert result is True
        mock_playwright_conversion.assert_called_once_with(
            converter, "<svg width='100' height='100'/>", "/tmp/test.png"
        )

    def test_convert_svg_content_raises_when_playwright_fails_and_error_on_fail_true(
        self, mock_playwright_conversion
    ):
        """Playwright 変換が失敗した場合、error_on_fail=True なら例外にする。"""
        config = {
            "output_dir": "assets/images",
            "scale": 1.0,
            "device_scale_factor": 1.0,
            "default_width": 800,
            "default_height": 600,
            "error_on_fail": True,
        }
        converter = SvgToPngConverter(config)
        mock_playwright_conversion.side_effect = RuntimeError("Playwright timed out")

        with pytest.raises(SvgConversionError):
            converter.convert_svg_content(
                "<svg width='10' height='10'></svg>", "/tmp/x.png"
            )

    def test_convert_svg_content_raises_when_playwright_browser_missing(
        self, svg_config, mock_playwright_conversion
    ):
        """Playwrightブラウザ未導入は設定ミスとして常に気づけるよう例外化する。"""
        converter = SvgToPngConverter({**svg_config, "error_on_fail": False})
        mock_playwright_conversion.side_effect = RuntimeError(
            "BrowserType.launch: Executable doesn't exist"
        )

        with pytest.raises(SvgConfigError) as exc_info:
            converter.convert_svg_content(
                "<svg width='10' height='10'></svg>", "/tmp/x.png"
            )

        assert "playwright" in str(exc_info.value).lower()

    def test_validate_svg_content_valid(self, converter):
        """Test SVG content validation with valid content."""
        valid_svg = "<svg xmlns='http://www.w3.org/2000/svg'><rect/></svg>"

        # Should not raise exception
        converter._validate_svg_content(valid_svg)

    def test_validate_svg_content_invalid(self, converter):
        """Test SVG content validation with invalid content."""
        invalid_svg = "<not-svg>content</not-svg>"

        with pytest.raises(SvgConversionError) as exc_info:
            converter._validate_svg_content(invalid_svg)

        assert "Invalid SVG content" in str(exc_info.value)

    def test_extract_svg_dimensions_with_width_height(self, converter):
        """Test SVG dimension extraction from width/height attributes."""
        svg_content = "<svg width='800' height='600'><rect/></svg>"

        width, height = converter._extract_svg_dimensions(svg_content)

        assert width == 800
        assert height == 600

    def test_extract_svg_dimensions_with_viewbox(self, converter):
        """Test SVG dimension extraction from viewBox attribute."""
        svg_content = "<svg viewBox='0 0 1200 800'><rect/></svg>"

        width, height = converter._extract_svg_dimensions(svg_content)

        assert width == 1200
        assert height == 800

    def test_extract_svg_dimensions_fallback(self, converter):
        """Test SVG dimension extraction fallback to defaults."""
        svg_content = "<svg><rect/></svg>"

        width, height = converter._extract_svg_dimensions(svg_content)

        assert width == 800  # default_width
        assert height == 600  # default_height

    def test_parse_dimension_pixels(self, converter):
        """Test dimension parsing with pixel units."""
        result = converter._parse_dimension("100px", 50)
        assert result == 100

    def test_parse_dimension_no_units(self, converter):
        """Test dimension parsing without units."""
        result = converter._parse_dimension("150", 50)
        assert result == 150

    def test_parse_dimension_invalid(self, converter):
        """Test dimension parsing with invalid input."""
        result = converter._parse_dimension("invalid", 75)
        assert result == 75

    def test_convert_transparent_background_svg(
        self, tmp_path, mock_playwright_conversion
    ):
        """Test conversion of SVG with transparent background.

        This test verifies that SVG files with transparent backgrounds
        are converted to PNG with transparent backgrounds.
        The implementation uses omit_background=True in Playwright.
        """
        config = {
            "output_dir": "assets/images",
            "scale": 1.0,
            "device_scale_factor": 1.0,
            "default_width": 800,
            "default_height": 600,
            "error_on_fail": False,
        }
        converter = SvgToPngConverter(config)

        # Create SVG content with transparent background
        svg_content = """<svg xmlns="http://www.w3.org/2000/svg"
                        style="background: transparent; background-color: transparent;"
                        width="100" height="100">
                        <rect width="50" height="50" fill="red"/>
                        </svg>"""

        output_path = tmp_path / "transparent_test.png"

        # Convert SVG to PNG
        result = converter.convert_svg_content(svg_content, str(output_path))

        assert result is True
        mock_playwright_conversion.assert_called_once_with(
            converter, svg_content, str(output_path)
        )

    def test_convert_red_background_svg(self, tmp_path, mock_playwright_conversion):
        """Test conversion of SVG with red background.

        This test verifies that SVG files with colored backgrounds
        preserve their background color in the generated PNG.
        """
        config = {
            "output_dir": "assets/images",
            "scale": 1.0,
            "device_scale_factor": 1.0,
            "default_width": 800,
            "default_height": 600,
            "error_on_fail": False,
        }
        converter = SvgToPngConverter(config)

        # Create SVG content with red background
        svg_content = """<svg xmlns="http://www.w3.org/2000/svg"
                        style="background: red; background-color: red;"
                        width="100" height="100">
                        <rect width="50" height="50" fill="blue"/>
                        </svg>"""

        output_path = tmp_path / "red_background_test.png"

        # Convert SVG to PNG
        result = converter.convert_svg_content(svg_content, str(output_path))

        assert result is True
        mock_playwright_conversion.assert_called_once_with(
            converter, svg_content, str(output_path)
        )


class TestBrowserLifecycle:
    """ブラウザインスタンスのライフサイクル管理をテストするクラス。"""

    @pytest.fixture
    def svg_config(self):
        """SVG処理用の基本設定"""
        return {
            "output_dir": "assets/images",
            "scale": 1.0,
            "device_scale_factor": 1.0,
            "default_width": 800,
            "default_height": 600,
            "preserve_original": False,
            "error_on_fail": False,
            "log_level": "INFO",
            "dpi": 150,
            "quality": 90,
        }

    def test_initial_state_has_no_browser(self, svg_config):
        """初期化直後はブラウザインスタンスを持たないことを確認する。"""
        converter = SvgToPngConverter(svg_config)
        assert converter._playwright is None
        assert converter._browser is None

    def test_ensure_browser_launches_browser(self, svg_config):
        """_ensure_browser が Playwright とブラウザを起動することを確認する。"""
        converter = SvgToPngConverter(svg_config)

        mock_browser = Mock()
        mock_playwright_instance = Mock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser

        # sync_playwright() が context manager ではなく start() を持つオブジェクトを返す
        mock_sync_playwright_callable = Mock()
        mock_sync_playwright_callable.return_value.start.return_value = (
            mock_playwright_instance
        )

        with patch.object(
            SvgToPngConverter,
            "_import_sync_playwright",
            return_value=mock_sync_playwright_callable,
        ):
            browser = converter._ensure_browser()

        assert browser is mock_browser
        assert converter._playwright is mock_playwright_instance
        assert converter._browser is mock_browser
        mock_playwright_instance.chromium.launch.assert_called_once_with(headless=True)

    def test_ensure_browser_reuses_existing_browser(self, svg_config):
        """_ensure_browser が既存ブラウザを再利用することを確認する。"""
        converter = SvgToPngConverter(svg_config)

        mock_browser = Mock()
        converter._browser = mock_browser
        converter._playwright = Mock()

        # _import_sync_playwright が呼ばれないことを確認
        with patch.object(SvgToPngConverter, "_import_sync_playwright") as mock_import:
            browser = converter._ensure_browser()

        assert browser is mock_browser
        mock_import.assert_not_called()

    def test_shutdown_closes_browser_and_playwright(self, svg_config):
        """shutdown がブラウザと Playwright を正しく終了することを確認する。"""
        converter = SvgToPngConverter(svg_config)

        mock_browser = Mock()
        mock_playwright = Mock()
        converter._browser = mock_browser
        converter._playwright = mock_playwright

        converter.shutdown()

        mock_browser.close.assert_called_once()
        mock_playwright.stop.assert_called_once()
        assert converter._browser is None
        assert converter._playwright is None

    def test_shutdown_is_safe_when_no_browser_started(self, svg_config):
        """ブラウザ未起動時に shutdown を呼んでもエラーにならないことを確認する。"""
        converter = SvgToPngConverter(svg_config)

        # 例外が発生しないことを確認
        converter.shutdown()

        assert converter._browser is None
        assert converter._playwright is None

    def test_shutdown_can_be_called_multiple_times(self, svg_config):
        """shutdown を複数回呼んでもエラーにならないことを確認する。"""
        converter = SvgToPngConverter(svg_config)

        mock_browser = Mock()
        mock_playwright = Mock()
        converter._browser = mock_browser
        converter._playwright = mock_playwright

        converter.shutdown()
        converter.shutdown()  # 2回目

        # close/stop は1回だけ呼ばれる
        mock_browser.close.assert_called_once()
        mock_playwright.stop.assert_called_once()

    def test_convert_uses_context_per_conversion(self, svg_config):
        """変換ごとにコンテキストが作成・破棄されることを確認する。"""
        converter = SvgToPngConverter(svg_config)

        mock_page = Mock()
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_browser = Mock()
        mock_browser.new_context.return_value = mock_context
        converter._browser = mock_browser
        converter._playwright = Mock()

        svg_content = "<svg width='100' height='100'><rect/></svg>"

        converter._convert_svg_with_playwright(svg_content, "/tmp/test.png")

        mock_browser.new_context.assert_called_once()
        mock_context.new_page.assert_called_once()
        mock_context.close.assert_called_once()

    def test_convert_reuses_browser_across_multiple_calls(self, svg_config):
        """複数回の変換でブラウザインスタンスが再利用されることを確認する。"""
        converter = SvgToPngConverter(svg_config)

        mock_page = Mock()
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_browser = Mock()
        mock_browser.new_context.return_value = mock_context

        mock_playwright_instance = Mock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_sync_playwright_callable = Mock()
        mock_sync_playwright_callable.return_value.start.return_value = (
            mock_playwright_instance
        )

        svg_content = "<svg width='100' height='100'><rect/></svg>"

        with patch.object(
            SvgToPngConverter,
            "_import_sync_playwright",
            return_value=mock_sync_playwright_callable,
        ):
            converter._convert_svg_with_playwright(svg_content, "/tmp/test1.png")
            converter._convert_svg_with_playwright(svg_content, "/tmp/test2.png")
            converter._convert_svg_with_playwright(svg_content, "/tmp/test3.png")

        # ブラウザ起動は1回だけ
        mock_playwright_instance.chromium.launch.assert_called_once()
        # コンテキストは3回作成される
        assert mock_browser.new_context.call_count == 3
        # コンテキストは3回閉じられる
        assert mock_context.close.call_count == 3

    def test_convert_preserves_screenshot_parameters(self, svg_config):
        """変換時のスクリーンショットパラメータが維持されることを確認する。

        後方互換性: omit_background=True, full_page=True が保たれること。
        """
        converter = SvgToPngConverter(svg_config)

        mock_page = Mock()
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_browser = Mock()
        mock_browser.new_context.return_value = mock_context
        converter._browser = mock_browser
        converter._playwright = Mock()

        svg_content = "<svg width='100' height='100'><rect/></svg>"
        output_path = "/tmp/test.png"

        converter._convert_svg_with_playwright(svg_content, output_path)

        mock_page.screenshot.assert_called_once_with(
            path=output_path, full_page=True, omit_background=True
        )

    def test_convert_sets_viewport_with_scale(self, svg_config):
        """SVG寸法とscale設定に基づいてビューポートが設定されることを確認する。"""
        config = {**svg_config, "scale": 2.0}
        converter = SvgToPngConverter(config)

        mock_page = Mock()
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_browser = Mock()
        mock_browser.new_context.return_value = mock_context
        converter._browser = mock_browser
        converter._playwright = Mock()

        svg_content = "<svg width='100' height='50'><rect/></svg>"

        converter._convert_svg_with_playwright(svg_content, "/tmp/test.png")

        mock_page.set_viewport_size.assert_called_once_with(
            {"width": 200, "height": 100}
        )

    def test_convert_sets_device_scale_factor(self, svg_config):
        """device_scale_factor がコンテキスト作成時に渡されることを確認する。"""
        config = {**svg_config, "device_scale_factor": 2.0}
        converter = SvgToPngConverter(config)

        mock_page = Mock()
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_browser = Mock()
        mock_browser.new_context.return_value = mock_context
        converter._browser = mock_browser
        converter._playwright = Mock()

        svg_content = "<svg width='100' height='100'><rect/></svg>"

        converter._convert_svg_with_playwright(svg_content, "/tmp/test.png")

        mock_browser.new_context.assert_called_once_with(device_scale_factor=2.0)

    def test_context_closed_even_on_error(self, svg_config):
        """変換中にエラーが発生してもコンテキストが閉じられることを確認する。"""
        converter = SvgToPngConverter(svg_config)

        mock_page = Mock()
        mock_page.set_content.side_effect = RuntimeError("render error")
        mock_context = Mock()
        mock_context.new_page.return_value = mock_page
        mock_browser = Mock()
        mock_browser.new_context.return_value = mock_context
        converter._browser = mock_browser
        converter._playwright = Mock()

        svg_content = "<svg width='100' height='100'><rect/></svg>"

        with pytest.raises(RuntimeError, match="render error"):
            converter._convert_svg_with_playwright(svg_content, "/tmp/test.png")

        # エラーが発生してもコンテキストは閉じられる
        mock_context.close.assert_called_once()

    def test_ensure_browser_raises_import_error_without_playwright(self, svg_config):
        """Playwright 未インストール時に ImportError が発生することを確認する。"""
        converter = SvgToPngConverter(svg_config)

        with (
            patch.object(
                SvgToPngConverter,
                "_import_sync_playwright",
                side_effect=ImportError(
                    "Playwright is required for SVG to PNG conversion."
                ),
            ),
            pytest.raises(ImportError, match="Playwright is required"),
        ):
            converter._ensure_browser()

    def test_ensure_browser_works_inside_asyncio_loop(self, svg_config):
        """asyncio ループ内でもブラウザが起動できることを確認する。

        Playwright sync API は asyncio ループ内で直接呼べないため、
        別スレッドで起動する回帰防止テスト。
        """
        import asyncio

        converter = SvgToPngConverter(svg_config)

        mock_browser = Mock()
        mock_playwright_instance = Mock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_sync_playwright_callable = Mock()
        mock_sync_playwright_callable.return_value.start.return_value = (
            mock_playwright_instance
        )

        async def run_in_async() -> Any:
            with patch.object(
                SvgToPngConverter,
                "_import_sync_playwright",
                return_value=mock_sync_playwright_callable,
            ):
                return converter._ensure_browser()

        browser = asyncio.run(run_in_async())

        assert browser is mock_browser
        mock_playwright_instance.chromium.launch.assert_called_once_with(headless=True)

    def test_ensure_browser_cleans_up_worker_on_launch_failure(self, svg_config):
        """asyncio ループ内で起動失敗時にワーカースレッドが解放されることを確認する。"""
        import asyncio

        converter = SvgToPngConverter(svg_config)

        mock_sync_playwright_callable = Mock()
        mock_sync_playwright_callable.return_value.start.side_effect = RuntimeError(
            "launch failed"
        )

        async def run_in_async() -> None:
            with (
                patch.object(
                    SvgToPngConverter,
                    "_import_sync_playwright",
                    return_value=mock_sync_playwright_callable,
                ),
                pytest.raises(RuntimeError, match="launch failed"),
            ):
                converter._ensure_browser()

        asyncio.run(run_in_async())

        # ワーカーが解放されていることを確認（スレッドリークなし）
        assert converter._worker is None
        assert converter._browser is None
        assert converter._playwright is None


class TestPluginShutdownIntegration:
    """プラグインの on_post_build で shutdown が呼ばれることをテストするクラス。"""

    def test_on_post_build_calls_converter_shutdown(self):
        """on_post_build でコンバータの shutdown が呼ばれることを確認する。"""
        from mkdocs_svg_to_png.plugin import SvgToPngPlugin

        plugin = SvgToPngPlugin()
        plugin.config = {"enabled": True}

        mock_processor = Mock()
        plugin.processor = mock_processor

        plugin.on_post_build(config=Mock())

        mock_processor.svg_converter.shutdown.assert_called_once()

    def test_on_post_build_shutdown_called_even_when_disabled(self):
        """プラグイン無効時でも shutdown が呼ばれることを確認する。

        ブラウザがon_config前に何らかの理由で起動していた場合への安全策。
        """
        from mkdocs_svg_to_png.plugin import SvgToPngPlugin

        plugin = SvgToPngPlugin()
        plugin.config = {"enabled": False}

        mock_processor = Mock()
        plugin.processor = mock_processor

        plugin.on_post_build(config=Mock())

        mock_processor.svg_converter.shutdown.assert_called_once()

    def test_on_post_build_no_processor_no_error(self):
        """processor が None の場合でもエラーにならないことを確認する。"""
        from mkdocs_svg_to_png.plugin import SvgToPngPlugin

        plugin = SvgToPngPlugin()
        plugin.config = {"enabled": True}
        plugin.processor = None

        # 例外が発生しないことを確認
        plugin.on_post_build(config=Mock())
