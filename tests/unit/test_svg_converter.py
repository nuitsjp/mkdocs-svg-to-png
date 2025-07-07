"""
SVG to PNG conversion functionality tests.
This module tests the SvgToPngConverter class using Playwright.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from mkdocs_svg_to_png.exceptions import SvgConversionError, SvgFileError
from mkdocs_svg_to_png.svg_converter import SvgToPngConverter


class TestSvgToPngConverter:
    """Test SvgToPngConverter class."""

    @pytest.fixture
    def basic_config(self):
        """Basic configuration for testing."""
        return {
            "output_dir": "assets/images",
            "scale": 1.0,
            "device_scale_factor": 1.0,
            "default_width": 800,
            "default_height": 600,
            "error_on_fail": True,
        }

    @pytest.fixture
    def converter(self, basic_config):
        """Create SvgToPngConverter instance."""
        return SvgToPngConverter(basic_config)

    def test_svg_converter_initialization(self, basic_config):
        """Test SvgToPngConverter initialization."""
        converter = SvgToPngConverter(basic_config)
        assert converter.config == basic_config

    @patch("mkdocs_svg_to_png.svg_converter.ensure_directory")
    @patch("mkdocs_svg_to_png.svg_converter.Path")
    def test_convert_svg_content_to_png_success(
        self, mock_path, mock_ensure_directory, converter
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

    def test_convert_nonexistent_svg_file(self, converter):
        """Test conversion of non-existent SVG file."""
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
    def test_convert_with_custom_scale(self, mock_path, mock_ensure_directory):
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
