#!/usr/bin/env python3
"""
SVG to PNG Converter using Headless Browser

This script converts SVG files to PNG format using Playwright's headless browser
for the highest quality rendering that preserves all text spacing and visual elements.
Features dynamic viewport sizing and configurable scaling.
"""

import argparse
import asyncio
import re
import sys
from pathlib import Path
from typing import List, NamedTuple

from playwright.async_api import async_playwright


class SVGDimensions(NamedTuple):
    """SVG dimensions container."""

    width: float
    height: float


def parse_svg_dimensions(svg_content: str) -> SVGDimensions:
    """Extract SVG dimensions from viewBox attribute."""
    # Try to find viewBox first
    viewbox_match = re.search(r'viewBox="([^"]*)"', svg_content)
    if viewbox_match:
        try:
            viewbox_values = viewbox_match.group(1).split()
            if len(viewbox_values) >= 4:
                width = float(viewbox_values[2])
                height = float(viewbox_values[3])
                return SVGDimensions(width, height)
        except (ValueError, IndexError):
            pass

    # Fallback: try to extract width and height attributes
    width_match = re.search(r'width="([^"]*)"', svg_content)
    height_match = re.search(r'height="([^"]*)"', svg_content)

    if width_match and height_match:
        try:
            width_str = width_match.group(1)
            height_str = height_match.group(1)

            # Remove units like px, em, etc.
            width = float(re.sub(r"[^\d.]", "", width_str))
            height = float(re.sub(r"[^\d.]", "", height_str))

            if width > 0 and height > 0:
                return SVGDimensions(width, height)
        except (ValueError, IndexError):
            pass

    # Default fallback dimensions
    return SVGDimensions(800, 600)


def get_svg_files(source_dir: Path) -> List[Path]:
    """Get all SVG files from the source directory."""
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    svg_files = list(source_dir.glob("*.svg"))
    if not svg_files:
        print(f"No SVG files found in {source_dir}")
        return []

    return svg_files


async def convert_svg_to_png_browser(
    svg_path: Path, png_path: Path, page, scale: float = 1.0
) -> bool:
    """Convert a single SVG file to PNG format using headless browser with dynamic sizing."""
    try:
        # Read SVG content
        with open(svg_path, encoding="utf-8") as f:
            svg_content = f.read()

        # Parse SVG dimensions
        svg_dims = parse_svg_dimensions(svg_content)

        # Calculate viewport size based on SVG dimensions and scale
        viewport_width = int(svg_dims.width * scale)
        viewport_height = int(svg_dims.height * scale)

        # Set viewport size to match SVG dimensions
        await page.set_viewport_size(
            {
                "width": max(viewport_width, 100),  # Minimum 100px
                "height": max(viewport_height, 100),
            }
        )

        # Create HTML wrapper for proper SVG rendering
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background: white;
                    font-family: "trebuchet ms", verdana, arial, sans-serif;
                    overflow: hidden;
                }}
                svg {{
                    display: block;
                    width: 100%;
                    height: 100vh;
                    object-fit: contain;
                }}
            </style>
        </head>
        <body>
            {svg_content}
        </body>
        </html>
        """

        # Set content and wait for fonts to load properly
        await page.set_content(html_content)
        await page.wait_for_load_state("networkidle")

        # Get SVG element and take screenshot
        svg_element = await page.query_selector("svg")
        if not svg_element:
            print(f"Error: No SVG element found in {svg_path.name}")
            return False

        # Take high-quality screenshot
        await svg_element.screenshot(path=str(png_path))
        return True

    except Exception as e:
        print(f"Error converting {svg_path.name}: {e}")
        return False


async def convert_all_svgs(
    svg_files: List[Path],
    destination_dir: Path,
    scale: float = 1.0,
    device_scale_factor: float = 1.0,
):
    """Convert all SVG files to PNG format with configurable scaling."""
    total_files = len(svg_files)
    successful_conversions = 0
    failed_conversions = 0

    print(f"Found {total_files} SVG files to convert using headless browser...")
    print(f"Scale: {scale * 100:.0f}%, Device Scale Factor: {device_scale_factor}")
    print("-" * 50)

    async with async_playwright() as p:
        # Launch browser with device scale factor for font consistency
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            device_scale_factor=device_scale_factor,
            viewport={
                "width": 1280,
                "height": 720,
            },  # Default, will be overridden per SVG
        )
        page = await context.new_page()

        for i, svg_file in enumerate(svg_files, 1):
            # Create PNG filename
            png_filename = svg_file.stem + ".png"
            png_path = destination_dir / png_filename

            print(f"[{i}/{total_files}] Converting {svg_file.name} -> {png_filename}")

            # Convert the file
            if await convert_svg_to_png_browser(svg_file, png_path, page, scale):
                successful_conversions += 1
                print("  ✓ Success")
            else:
                failed_conversions += 1
                print("  ✗ Failed")

        await browser.close()

    # Print summary
    print("-" * 50)
    print("Conversion complete!")
    print(f"  Successful: {successful_conversions}")
    print(f"  Failed: {failed_conversions}")
    print(f"  Total: {total_files}")

    return failed_conversions == 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert SVG files to PNG with dynamic sizing and configurable scaling"
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="Output scale factor (default: 1.0 = 100%%)",
    )
    parser.add_argument(
        "--device-scale",
        type=float,
        default=1.0,
        help="Device scale factor for font consistency (default: 1.0)",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="source",
        help="Source directory containing SVG files (default: source)",
    )
    parser.add_argument(
        "--destination",
        type=str,
        default="destination",
        help="Destination directory for PNG files (default: destination)",
    )
    return parser.parse_args()


async def main():
    """Main conversion function."""
    args = parse_args()

    # Define source and destination directories
    source_dir = Path(args.source)
    destination_dir = Path(args.destination)

    # Create destination directory if it doesn't exist
    destination_dir.mkdir(exist_ok=True)

    # Get all SVG files
    try:
        svg_files = get_svg_files(source_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if not svg_files:
        sys.exit(0)

    # Convert all files with specified scaling
    success = await convert_all_svgs(
        svg_files,
        destination_dir,
        scale=args.scale,
        device_scale_factor=args.device_scale,
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
