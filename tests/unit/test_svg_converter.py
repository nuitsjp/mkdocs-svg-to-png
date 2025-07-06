"""
SVG to PNG conversion functionality tests.
This module tests the SvgToPngConverter class that replaces MermaidImageGenerator.
"""

from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

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
            "dpi": 300,
            "output_format": "png",
            "quality": 95,
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
    @patch("mkdocs_svg_to_png.svg_converter.cairosvg")
    @patch("mkdocs_svg_to_png.svg_converter.Path")
    def test_convert_svg_content_to_png_success(
        self, mock_path, mock_cairosvg, mock_ensure_directory, converter
    ):
        """Test successful SVG content to PNG conversion."""
        svg_content = "<svg><rect width='100' height='100'/></svg>"
        output_path = "/tmp/test.png"

        # Mock successful conversion
        mock_cairosvg.svg2png.return_value = b"fake_png_data"

        # Mock Path operations
        mock_file = Mock()
        mock_path.return_value.open.return_value.__enter__.return_value = mock_file
        mock_path.return_value.parent = "/tmp"

        result = converter.convert_svg_content(svg_content, output_path)

        assert result is True
        mock_cairosvg.svg2png.assert_called_once_with(
            bytestring=svg_content.encode("utf-8"),
            dpi=300,
        )
        mock_file.write.assert_called_once_with(b"fake_png_data")

    @patch("mkdocs_svg_to_png.svg_converter.ensure_directory")
    @patch("mkdocs_svg_to_png.svg_converter.cairosvg")
    @patch("mkdocs_svg_to_png.svg_converter.Path")
    def test_convert_svg_file_to_png_success(self, mock_path, mock_cairosvg, mock_ensure_directory, converter):
        """Test successful SVG file to PNG conversion."""
        svg_path = "/tmp/test.svg"
        output_path = "/tmp/test.png"

        # Mock successful conversion
        mock_cairosvg.svg2png.return_value = b"fake_png_data"

        # Mock Path operations
        mock_file = Mock()
        mock_svg_path = Mock()
        mock_svg_path.exists.return_value = True
        mock_svg_path.read_text.return_value = "<svg/>"
        mock_output_path = Mock()
        mock_context_manager = MagicMock()
        mock_context_manager.__enter__.return_value = mock_file
        mock_context_manager.__exit__.return_value = None
        mock_output_path.open.return_value = mock_context_manager
        mock_output_path.parent = "/tmp"

        def path_side_effect(arg):
            if arg == svg_path:
                return mock_svg_path
            elif arg == output_path:
                return mock_output_path
            return Mock()

        mock_path.side_effect = path_side_effect

        result = converter.convert_svg_file(svg_path, output_path)

        assert result is True
        mock_cairosvg.svg2png.assert_called_once_with(
            url=svg_path,
            dpi=300,
        )
        mock_file.write.assert_called_once_with(b"fake_png_data")

    @patch("mkdocs_svg_to_png.svg_converter.ensure_directory")
    @patch("mkdocs_svg_to_png.svg_converter.cairosvg")
    @patch("mkdocs_svg_to_png.svg_converter.Path")
    def test_convert_svg_content_cairo_error(self, mock_path, mock_cairosvg, mock_ensure_directory, converter):
        """Test CairoSVG error handling."""
        svg_content = "<svg>valid svg content</svg>"
        output_path = "/tmp/test.png"

        # Mock CairoSVG error
        mock_cairosvg.svg2png.side_effect = Exception("Invalid SVG")

        # Mock Path operations
        mock_path.return_value.parent = "/tmp"

        with pytest.raises(SvgConversionError) as exc_info:
            converter.convert_svg_content(svg_content, output_path)

        assert "CairoSVG conversion failed" in str(exc_info.value)
        assert exc_info.value.details["cairo_error"] == "Invalid SVG"

    def test_convert_svg_content_with_error_on_fail_false(self):
        """Test SVG conversion with error_on_fail=False."""
        config = {
            "output_dir": "assets/images",
            "dpi": 300,
            "error_on_fail": False,
        }
        converter = SvgToPngConverter(config)

        with patch("mkdocs_svg_to_png.svg_converter.cairosvg") as mock_cairosvg:
            mock_cairosvg.svg2png.side_effect = Exception("Invalid SVG")

            result = converter.convert_svg_content("<invalid/>", "/tmp/test.png")

            assert result is False  # Should return False instead of raising

    def test_convert_nonexistent_svg_file(self, converter):
        """Test conversion of non-existent SVG file."""
        svg_path = "/nonexistent/file.svg"
        output_path = "/tmp/test.png"

        with pytest.raises(SvgFileError) as exc_info:
            converter.convert_svg_file(svg_path, output_path)

        assert "SVG file not found" in str(exc_info.value)
        assert exc_info.value.details["file_path"] == svg_path

    @patch("mkdocs_svg_to_png.svg_converter.ensure_directory")
    @patch("mkdocs_svg_to_png.svg_converter.cairosvg")
    @patch("mkdocs_svg_to_png.svg_converter.Path")
    def test_convert_with_custom_dpi(self, mock_path, mock_cairosvg, mock_ensure_directory):
        """Test conversion with custom DPI setting."""
        config = {
            "output_dir": "assets/images",
            "dpi": 150,
            "error_on_fail": True,
        }
        converter = SvgToPngConverter(config)

        mock_cairosvg.svg2png.return_value = b"fake_png_data"

        # Mock Path operations
        mock_file = Mock()
        mock_path.return_value.open.return_value.__enter__.return_value = mock_file
        mock_path.return_value.parent = "/tmp"

        converter.convert_svg_content("<svg/>", "/tmp/test.png")

        mock_cairosvg.svg2png.assert_called_once_with(
            bytestring=b"<svg/>",
            dpi=150,
        )

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
