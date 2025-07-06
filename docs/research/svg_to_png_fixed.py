#!/usr/bin/env python3
"""
SVG to PNG Converter with Text Spacing Fix

This script fixes the text spacing issue in SVG files before converting
them to PNG format using rsvg-convert.
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import List


def get_svg_files(source_dir: Path) -> List[Path]:
    """Get all SVG files from the source directory."""
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    svg_files = list(source_dir.glob("*.svg"))
    if not svg_files:
        print(f"No SVG files found in {source_dir}")
        return []

    return svg_files


def fix_svg_text_spacing(svg_content: str) -> str:
    """Fix text spacing issues in SVG by consolidating tspan elements."""
    # Pattern to match multiple tspan elements that should be combined
    # This handles cases like: <tspan>Gateway</tspan><tspan> Service</tspan>
    pattern = r"<tspan([^>]*?)>([^<]*?)</tspan><tspan([^>]*?)>(\s+)([^<]*?)</tspan>"

    def replace_tspan(match):
        # Combine the text content with proper spacing
        attr1 = match.group(1)
        text1 = match.group(2)
        attr2 = match.group(3)
        space = match.group(4)
        text2 = match.group(5)

        # Combine into a single tspan with the space preserved
        return f"<tspan{attr1}>{text1}{space}{text2}</tspan>"

    # Apply the fix
    fixed_content = re.sub(pattern, replace_tspan, svg_content)

    return fixed_content


def convert_svg_to_png(svg_path: Path, png_path: Path) -> bool:
    """Convert a single SVG file to PNG format using rsvg-convert with text fixes."""
    try:
        # Read and fix the SVG content
        with open(svg_path, encoding="utf-8") as f:
            svg_content = f.read()

        # Fix text spacing issues
        fixed_svg_content = fix_svg_text_spacing(svg_content)

        # Create a temporary file with the fixed content
        temp_svg_path = svg_path.parent / f"temp_{svg_path.name}"
        with open(temp_svg_path, "w", encoding="utf-8") as f:
            f.write(fixed_svg_content)

        try:
            # Use rsvg-convert with the fixed SVG
            cmd = [
                "rsvg-convert",
                "--format=png",
                "--dpi-x=300",
                "--dpi-y=300",
                "--background-color=white",
                f"--output={png_path}",
                str(temp_svg_path),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                return True
            else:
                print(f"Error converting {svg_path.name}: {result.stderr}")
                return False
        finally:
            # Clean up temporary file
            if temp_svg_path.exists():
                temp_svg_path.unlink()

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

    print(f"Found {total_files} SVG files to convert with text spacing fixes...")
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
