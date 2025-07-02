"""Tests for exception classes."""

from __future__ import annotations

import pytest

from mkdocs_svg_to_png.exceptions import (
    SvgConfigError,
    SvgConversionError,
    SvgFileError,
    SvgImageError,
    SvgParsingError,
    SvgPreprocessorError,
    SvgValidationError,
)


class TestSvgPreprocessorError:
    """Test SvgPreprocessorError exception."""

    def test_svg_preprocessor_error_creation(self) -> None:
        """Test SvgPreprocessorError creation."""
        error = SvgPreprocessorError("SVG preprocessing failed")
        assert str(error) == "SVG preprocessing failed"
        assert error.details == {}

    def test_svg_preprocessor_error_with_context(self) -> None:
        """Test SvgPreprocessorError with context parameters."""
        error = SvgPreprocessorError(
            "SVG processing failed",
            svg_file="test.svg",
            operation="convert",
        )
        assert str(error) == "SVG processing failed"
        assert error.details["svg_file"] == "test.svg"
        assert error.details["operation"] == "convert"

    def test_svg_preprocessor_error_with_long_svg_content(self) -> None:
        """Test SvgPreprocessorError with long SVG content truncation."""
        long_svg = "<svg>" + "A" * 200 + "</svg>"  # Over 200 chars
        error = SvgPreprocessorError(
            "SVG processing failed",
            svg_content=long_svg,
        )
        assert error.details["svg_content"].endswith("...")
        assert len(error.details["svg_content"]) == 203


class TestSvgSpecificExceptions:
    """Test SVG-specific exception classes."""

    def test_svg_config_error(self) -> None:
        """Test SvgConfigError creation."""
        error = SvgConfigError(
            "Invalid DPI setting",
            config_key="dpi",
            config_value=0,
            suggestion="Use positive integer value",
        )
        assert str(error) == "Invalid DPI setting"
        assert error.details["config_key"] == "dpi"
        assert error.details["config_value"] == 0
        assert error.details["suggestion"] == "Use positive integer value"

    def test_svg_conversion_error(self) -> None:
        """Test SvgConversionError creation."""
        error = SvgConversionError(
            "Failed to convert SVG to PNG",
            svg_path="test.svg",
            output_path="test.png",
            cairo_error="Invalid SVG syntax",
        )
        assert str(error) == "Failed to convert SVG to PNG"
        assert error.details["svg_path"] == "test.svg"
        assert error.details["output_path"] == "test.png"
        assert error.details["cairo_error"] == "Invalid SVG syntax"

    def test_svg_file_error(self) -> None:
        """Test SvgFileError creation."""
        error = SvgFileError(
            "SVG file not found",
            file_path="missing.svg",
            operation="read",
            suggestion="Check file path exists",
        )
        assert str(error) == "SVG file not found"
        assert error.details["file_path"] == "missing.svg"
        assert error.details["operation"] == "read"
        assert error.details["suggestion"] == "Check file path exists"

    def test_svg_parsing_error(self) -> None:
        """Test SvgParsingError creation."""
        error = SvgParsingError(
            "Invalid SVG block format",
            source_file="doc.md",
            line_number=15,
            svg_content="<invalid>svg</invalid>",
        )
        assert str(error) == "Invalid SVG block format"
        assert error.details["source_file"] == "doc.md"
        assert error.details["line_number"] == 15
        assert error.details["svg_content"] == "<invalid>svg</invalid>"

    def test_svg_validation_error(self) -> None:
        """Test SvgValidationError creation."""
        error = SvgValidationError(
            "SVG validation failed",
            validation_type="format",
            invalid_value="not-an-svg",
            expected_format="Valid SVG markup",
        )
        assert str(error) == "SVG validation failed"
        assert error.details["validation_type"] == "format"
        assert error.details["invalid_value"] == "not-an-svg"
        assert error.details["expected_format"] == "Valid SVG markup"

    def test_svg_image_error(self) -> None:
        """Test SvgImageError creation."""
        error = SvgImageError(
            "Failed to generate image",
            image_format="png",
            image_path="test.png",
            svg_content="<svg></svg>",
            suggestion="Check SVG content",
        )
        assert str(error) == "Failed to generate image"
        assert error.details["image_format"] == "png"
        assert error.details["image_path"] == "test.png"
        assert error.details["svg_content"] == "<svg></svg>"
        assert error.details["suggestion"] == "Check SVG content"

    def test_svg_exception_inheritance(self) -> None:
        """Test that all SVG exceptions inherit from SvgPreprocessorError."""
        assert issubclass(SvgParsingError, SvgPreprocessorError)
        assert issubclass(SvgConfigError, SvgPreprocessorError)
        assert issubclass(SvgConversionError, SvgPreprocessorError)
        assert issubclass(SvgFileError, SvgPreprocessorError)
        assert issubclass(SvgValidationError, SvgPreprocessorError)
        assert issubclass(SvgImageError, SvgPreprocessorError)

        # Test that they can be caught as base exception
        try:
            raise SvgParsingError("test", "file.md", 1, "<svg/>")
        except SvgPreprocessorError:
            pass  # Should be caught
        else:
            pytest.fail("SvgParsingError should be caught as SvgPreprocessorError")
