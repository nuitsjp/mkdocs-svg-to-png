"""Tests for exception classes."""

from __future__ import annotations

import pytest

from mkdocs_svg_to_png.exceptions import (
    MermaidCLIError,
    MermaidConfigError,
    MermaidParsingError,
    MermaidPreprocessorError,
    SvgConfigError,
    SvgConversionError,
    SvgFileError,
    SvgParsingError,
    SvgPreprocessorError,
    SvgValidationError,
)


class TestMermaidParsingError:
    """Test MermaidParsingError exception."""

    def test_mermaid_parsing_error_with_all_details(self) -> None:
        """Test MermaidParsingError with all detail parameters."""
        source_file = "test.md"
        line_number = 10
        mermaid_code = "graph TD\n    A --> B"

        error = MermaidParsingError(
            "Parse error occurred",
            source_file=source_file,
            line_number=line_number,
            mermaid_code=mermaid_code,
        )

        assert str(error) == "Parse error occurred"
        assert error.details["source_file"] == source_file
        assert error.details["line_number"] == line_number
        assert error.details["mermaid_code"] == mermaid_code

    def test_mermaid_parsing_error_with_long_code(self) -> None:
        """Test MermaidParsingError with code longer than 200 characters."""
        source_file = "test.md"
        line_number = 5
        # Create a long mermaid code string (over 200 chars)
        mermaid_code = "graph TD\n" + "    A --> B\n" * 20  # Much longer than 200 chars

        error = MermaidParsingError(
            "Parse error occurred",
            source_file=source_file,
            line_number=line_number,
            mermaid_code=mermaid_code,
        )

        # Should be truncated with "..." appended
        assert error.details["mermaid_code"].endswith("...")
        assert len(error.details["mermaid_code"]) == 203  # 200 + "..."

    def test_mermaid_parsing_error_with_empty_code(self) -> None:
        """Test MermaidParsingError with empty mermaid code."""
        error = MermaidParsingError(
            "Parse error occurred",
            source_file="test.md",
            line_number=1,
            mermaid_code="",
        )

        assert error.details["mermaid_code"] == ""

    def test_mermaid_parsing_error_with_none_code(self) -> None:
        """Test MermaidParsingError with None mermaid code."""
        error = MermaidParsingError(
            "Parse error occurred",
            source_file="test.md",
            line_number=1,
            mermaid_code=None,
        )

        # None values are now filtered out
        assert "mermaid_code" not in error.details
        assert error.details["source_file"] == "test.md"
        assert error.details["line_number"] == 1

    def test_mermaid_parsing_error_with_exactly_200_chars(self) -> None:
        """Test MermaidParsingError with exactly 200 character code."""
        mermaid_code = "A" * 200  # Exactly 200 characters

        error = MermaidParsingError(
            "Parse error occurred",
            source_file="test.md",
            line_number=1,
            mermaid_code=mermaid_code,
        )

        # Should not be truncated
        assert error.details["mermaid_code"] == mermaid_code
        assert not error.details["mermaid_code"].endswith("...")


class TestOtherExceptions:
    """Test other exception classes."""

    def test_mermaid_preprocessor_error(self) -> None:
        """Test MermaidPreprocessorError creation."""
        error = MermaidPreprocessorError("Preprocessor failed")
        assert str(error) == "Preprocessor failed"
        assert error.details == {}

    def test_mermaid_cli_error(self) -> None:
        """Test MermaidCLIError creation."""
        error = MermaidCLIError("CLI command failed")
        assert str(error) == "CLI command failed"
        # None values are now filtered out
        assert error.details == {}

    def test_mermaid_config_error(self) -> None:
        """Test MermaidConfigError creation."""
        error = MermaidConfigError("Configuration invalid")
        assert str(error) == "Configuration invalid"
        # None values are now filtered out
        assert error.details == {}

    def test_exception_inheritance(self) -> None:
        """Test that all exceptions inherit from MermaidPreprocessorError."""
        assert issubclass(MermaidParsingError, MermaidPreprocessorError)
        assert issubclass(MermaidCLIError, MermaidPreprocessorError)
        assert issubclass(MermaidConfigError, MermaidPreprocessorError)

        # Test that they can be caught as base exception
        try:
            raise MermaidParsingError("test", "file.md", 1, "code")
        except MermaidPreprocessorError:
            pass  # Should be caught
        else:
            pytest.fail(
                "MermaidParsingError should be caught as MermaidPreprocessorError"
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

    def test_svg_exception_inheritance(self) -> None:
        """Test that all SVG exceptions inherit from SvgPreprocessorError."""
        assert issubclass(SvgParsingError, SvgPreprocessorError)
        assert issubclass(SvgConfigError, SvgPreprocessorError)
        assert issubclass(SvgConversionError, SvgPreprocessorError)
        assert issubclass(SvgFileError, SvgPreprocessorError)
        assert issubclass(SvgValidationError, SvgPreprocessorError)

        # Test that they can be caught as base exception
        try:
            raise SvgParsingError("test", "file.md", 1, "<svg/>")
        except SvgPreprocessorError:
            pass  # Should be caught
        else:
            pytest.fail("SvgParsingError should be caught as SvgPreprocessorError")
