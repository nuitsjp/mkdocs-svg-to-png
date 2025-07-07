"""SVG to PNG conversion functionality using Playwright."""

from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Any

try:
    from playwright.async_api import async_playwright
except ImportError:
    raise ImportError(
        "Playwright is required for SVG to PNG conversion. "
        "Install it with: pip install playwright && playwright install chromium"
    ) from None

try:
    import defusedxml.ElementTree as ET
except ImportError:
    # Fallback to standard library (less secure but available)
    import xml.etree.ElementTree as ET  # nosec B405

from .exceptions import SvgConversionError, SvgFileError
from .logging_config import get_logger
from .utils import ensure_directory


class SvgToPngConverter:
    """Convert SVG content or files to PNG using Playwright."""

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

            # Convert SVG to PNG using Playwright
            success = self._run_playwright_conversion(svg_content, output_path)

            if success:
                self.logger.info(f"Generated PNG image: {output_path}")
                return True
            else:
                return False

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
            # Read SVG content and convert
            svg_content = svg_file.read_text(encoding="utf-8")
            return self.convert_svg_content(svg_content, output_path)

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
            # Try to parse as XML using defusedxml (secure) or fallback
            ET.fromstring(svg_content)  # nosec B314

            # Check if it's actually SVG (allow XML declaration)
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
        """Convert SVG content to PNG using Playwright browser engine.

        Args:
            svg_content: String containing SVG markup
            output_path: Path where PNG file should be saved

        Returns:
            True if conversion was successful, False otherwise
        """
        async with async_playwright() as p:
            # Launch Chromium browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                device_scale_factor=self.config.get("device_scale_factor", 1.0)
            )
            page = await context.new_page()

            try:
                # Extract SVG dimensions
                width, height = self._extract_svg_dimensions(svg_content)

                # Calculate scaled dimensions
                scale = self.config.get("scale", 1.0)
                scaled_width = int(width * scale)
                scaled_height = int(height * scale)

                # Set viewport to match SVG dimensions
                await page.set_viewport_size(
                    {"width": scaled_width, "height": scaled_height}
                )

                # Create HTML content with embedded SVG
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{
                            margin: 0;
                            padding: 0;
                            background: white;
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

                # Load HTML content
                await page.set_content(html_content)

                # Wait for SVG to render
                await page.wait_for_load_state("networkidle")

                # Take screenshot
                await page.screenshot(path=output_path, full_page=True)

                return True

            finally:
                await browser.close()

    def _extract_svg_dimensions(self, svg_content: str) -> tuple[int, int]:
        """Extract width and height from SVG content.

        Args:
            svg_content: String containing SVG markup

        Returns:
            Tuple of (width, height) in pixels
        """
        # Default dimensions
        default_width = self.config.get("default_width", 800)
        default_height = self.config.get("default_height", 600)

        try:
            # Parse SVG content
            root = ET.fromstring(svg_content)

            # Try to get width and height attributes
            width_attr = root.get("width")
            height_attr = root.get("height")

            if width_attr and height_attr:
                # Extract numeric values
                width = self._parse_dimension(width_attr, default_width)
                height = self._parse_dimension(height_attr, default_height)
                return width, height

            # Try to get dimensions from viewBox
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
        """Parse dimension string to integer pixel value.

        Args:
            dimension_str: Dimension string (e.g., "100px", "100", "10em")
            default: Default value if parsing fails

        Returns:
            Integer pixel value
        """
        try:
            # Remove units and convert to int
            numeric_match = re.match(r"([0-9.]+)", dimension_str)
            if numeric_match:
                return int(float(numeric_match.group(1)))
        except (ValueError, AttributeError):
            pass

        return default

    def _run_playwright_conversion(self, svg_content: str, output_path: str) -> bool:
        """Run Playwright conversion handling asyncio event loop properly.

        Args:
            svg_content: String containing SVG markup
            output_path: Path where PNG file should be saved

        Returns:
            True if conversion was successful, False otherwise
        """
        try:
            # Check if we're in an existing event loop
            try:
                loop = asyncio.get_running_loop()
                if loop and loop.is_running():
                    # We're in an event loop, run in a new thread
                    import threading

                    result_container = {}
                    exception_container = {}

                    def run_in_new_loop() -> None:
                        try:
                            # Create a new event loop for this thread
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
                    # Event loop exists but not running
                    return asyncio.run(
                        self._convert_svg_with_playwright(svg_content, output_path)
                    )
            except RuntimeError:
                # No event loop running, safe to use asyncio.run
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
