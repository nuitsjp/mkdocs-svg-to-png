"""SVG to PNG conversion functionality using CairoSVG."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

try:
    import cairosvg
except ImportError:
    raise ImportError(
        "CairoSVG is required for SVG to PNG conversion. "
        "Install it with: pip install cairosvg"
    ) from None

from .exceptions import SvgConversionError, SvgFileError
from .logging_config import get_logger
from .utils import ensure_directory


class SvgToPngConverter:
    """Convert SVG content or files to PNG using CairoSVG."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialize the SVG to PNG converter.

        Args:
            config: Configuration dictionary containing conversion settings
        """
        self.config = config
        self.logger = get_logger(__name__)

    def convert_svg_content(self, svg_content: str, output_path: str) -> bool:
        """Convert SVG content string to PNG file.

        Args:
            svg_content: String containing SVG markup
            output_path: Path where PNG file should be saved

        Returns:
            True if conversion was successful, False otherwise

        Raises:
            SvgConversionError: If conversion fails and error_on_fail is True
        """
        try:
            self._validate_svg_content(svg_content)

            # Ensure output directory exists
            ensure_directory(str(Path(output_path).parent))

            # Convert SVG to PNG using CairoSVG
            png_data = cairosvg.svg2png(
                bytestring=svg_content.encode("utf-8"),
                dpi=self.config.get("dpi", 300),
            )

            # Write PNG data to file
            with Path(output_path).open("wb") as f:
                f.write(png_data)

            self.logger.info(f"Generated PNG image: {output_path}")
            return True

        except Exception as e:
            return self._handle_conversion_error(e, output_path, svg_content)

    def convert_svg_file(self, svg_path: str, output_path: str) -> bool:
        """Convert SVG file to PNG file.

        Args:
            svg_path: Path to input SVG file
            output_path: Path where PNG file should be saved

        Returns:
            True if conversion was successful, False otherwise

        Raises:
            SvgFileError: If SVG file not found
            SvgConversionError: If conversion fails and error_on_fail is True
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
            # Ensure output directory exists
            ensure_directory(str(Path(output_path).parent))

            # Convert SVG file to PNG using CairoSVG
            png_data = cairosvg.svg2png(
                url=svg_path,
                dpi=self.config.get("dpi", 300),
            )

            # Write PNG data to file
            with Path(output_path).open("wb") as f:
                f.write(png_data)

            self.logger.info(f"Generated PNG image: {output_path}")
            return True

        except Exception as e:
            svg_content = svg_file.read_text(encoding="utf-8")
            return self._handle_conversion_error(e, output_path, svg_content, svg_path)

    def _validate_svg_content(self, svg_content: str) -> None:
        """Validate that content is valid SVG.

        Args:
            svg_content: String containing SVG markup

        Raises:
            SvgConversionError: If SVG content is invalid
        """
        try:
            # Try to parse as XML
            ET.fromstring(svg_content)

            # Check if it's actually SVG
            if not svg_content.strip().startswith("<svg"):
                raise SvgConversionError(
                    "Invalid SVG content: Must start with <svg> tag",
                    svg_content=svg_content,
                )

        except ET.ParseError as e:
            raise SvgConversionError(
                "Invalid SVG content: XML parsing failed",
                svg_content=svg_content,
                cairo_error=str(e),
            ) from e

    def _handle_conversion_error(
        self,
        error: Exception,
        output_path: str,
        svg_content: str,
        svg_path: str | None = None,
    ) -> bool:
        """Handle conversion errors based on configuration.

        Args:
            error: The exception that occurred
            output_path: Target output path
            svg_content: SVG content that failed to convert
            svg_path: Source SVG file path (if applicable)

        Returns:
            False if error_on_fail is False

        Raises:
            SvgConversionError: If error_on_fail is True
        """
        error_msg = f"CairoSVG conversion failed: {error}"
        self.logger.error(error_msg)

        if self.config.get("error_on_fail", True):
            raise SvgConversionError(
                "CairoSVG conversion failed",
                svg_path=svg_path,
                output_path=output_path,
                svg_content=svg_content,
                cairo_error=str(error),
            ) from error

        return False
