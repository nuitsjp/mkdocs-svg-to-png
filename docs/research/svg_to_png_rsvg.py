#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SVG to PNG Converter using rsvg-convert

This script converts all SVG files in the source folder to PNG format
and saves them in the destination folder using rsvg-convert.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple


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
    """Convert a single SVG file to PNG format using rsvg-convert."""
    try:
        # Use rsvg-convert with specific options to preserve text spacing
        cmd = [
            "rsvg-convert",
            "--format=png",
            "--dpi-x=300",
            "--dpi-y=300",
            "--background-color=white",
            f"--output={png_path}",
            str(svg_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return True
        else:
            print(f"Error converting {svg_path.name}: {result.stderr}")
            return False
            
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
    
    print(f"Found {total_files} SVG files to convert using rsvg-convert...")
    print("-" * 50)
    
    for i, svg_file in enumerate(svg_files, 1):
        # Create PNG filename
        png_filename = svg_file.stem + ".png"
        png_path = destination_dir / png_filename
        
        print(f"[{i}/{total_files}] Converting {svg_file.name} -> {png_filename}")
        
        # Convert the file
        if convert_svg_to_png(svg_file, png_path):
            successful_conversions += 1
            print(f"  ✓ Success")
        else:
            failed_conversions += 1
            print(f"  ✗ Failed")
    
    # Print summary
    print("-" * 50)
    print(f"Conversion complete!")
    print(f"  Successful: {successful_conversions}")
    print(f"  Failed: {failed_conversions}")
    print(f"  Total: {total_files}")
    
    if failed_conversions > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()