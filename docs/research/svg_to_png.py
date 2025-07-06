#!/usr/bin/env python3
"""
SVG to PNG Converter

This script converts all SVG files in the source folder to PNG format
and saves them in the destination folder using cairosvg.
"""

import sys
from pathlib import Path
from typing import List

try:
    import cairosvg
except ImportError:
    print("Error: cairosvg is not installed. Please run: uv sync")
    sys.exit(1)


def get_svg_files(source_dir: Path) -> List[Path]:
    """Get all SVG files from the source directory."""
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    svg_files = list(source_dir.glob("*.svg"))
    if not svg_files:
        print(f"No SVG files found in {source_dir}")
        return []

    return svg_files


def convert_svg_to_png(svg_path: Path, png_path: Path) -> bool:
    """Convert a single SVG file to PNG format."""
    try:
        # Read SVG file with UTF-8 encoding
        with open(svg_path, encoding="utf-8") as f:
            svg_content = f.read()

        # Fix font rendering by preprocessing the SVG content
        # Replace problematic font stack with system fonts
        svg_content = svg_content.replace(
            'font-family:"trebuchet ms",verdana,arial,sans-serif',
            'font-family:"DejaVu Sans",Arial,sans-serif',
        )

        # Fix font rendering issues by setting specific parameters
        cairosvg.svg2png(
            bytestring=svg_content.encode("utf-8"),
            write_to=str(png_path),
            dpi=300,  # Higher DPI for better text rendering
            output_width=None,  # Let SVG determine dimensions
            output_height=None,
            unsafe=True,  # Allow loading external resources if needed
        )
        return True
    except Exception as e:
        print(f"Error converting {svg_path.name}: {e}")
        return False


def main():
    """Main conversion function."""
    # Define source and destination directories
    source_dir = Path("source")
    destination_dir = Path("destination")

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

    # Convert each SVG file
    total_files = len(svg_files)
    successful_conversions = 0
    failed_conversions = 0

    print(f"Found {total_files} SVG files to convert...")
    print("-" * 50)

    for i, svg_file in enumerate(svg_files, 1):
        # Create PNG filename
        png_filename = svg_file.stem + ".png"
        png_path = destination_dir / png_filename

        print(f"[{i}/{total_files}] Converting {svg_file.name} -> {png_filename}")

        # Convert the file
        if convert_svg_to_png(svg_file, png_path):
            successful_conversions += 1
            print("  ✓ Success")
        else:
            failed_conversions += 1
            print("  ✗ Failed")

    # Print summary
    print("-" * 50)
    print("Conversion complete!")
    print(f"  Successful: {successful_conversions}")
    print(f"  Failed: {failed_conversions}")
    print(f"  Total: {total_files}")

    if failed_conversions > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
