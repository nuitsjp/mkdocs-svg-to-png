#!/usr/bin/env python3
"""
Generate expected PNG files from SVG fixtures for testing.
This script converts SVG files in tests/fixtures/input/ to PNG files in tests/fixtures/expected/.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mkdocs_svg_to_png.svg_converter import SvgToPngConverter


def main():
    """Generate expected PNG files from SVG fixtures."""
    # Get project root and fixture directories
    project_root = Path(__file__).parent.parent
    input_dir = project_root / "tests" / "fixtures" / "input"
    expected_dir = project_root / "tests" / "fixtures" / "expected"
    
    # Ensure expected directory exists
    expected_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure converter for high-quality output
    config = {
        "scale": 1.0,
        "device_scale_factor": 1.0,
        "default_width": 800,
        "default_height": 600,
        "error_on_fail": False,
    }
    
    converter = SvgToPngConverter(config)
    
    # Get all SVG files (excluding the basic test SVGs we already have)
    svg_files = list(input_dir.glob("*.svg"))
    
    # Get all SVG files from input directory
    all_svg_files = [f.name for f in input_dir.glob("*.svg")]
    
    # Get existing PNG files in expected directory
    existing_pngs = {f.name.replace('.png', '.svg') for f in expected_dir.glob("*.png")}
    
    # Find SVG files that don't have corresponding PNGs
    target_files = [svg for svg in all_svg_files if svg not in existing_pngs]
    
    print(f"Found {len(all_svg_files)} SVG files total")
    print(f"Found {len(existing_pngs)} existing PNG files")
    print(f"Will generate {len(target_files)} new PNG files")
    
    successful_conversions = 0
    failed_conversions = 0
    
    print("Generating expected PNG files from SVG fixtures...")
    print("=" * 60)
    
    for svg_filename in target_files:
        svg_file = input_dir / svg_filename
        if not svg_file.exists():
            print(f"⚠️  Skipping {svg_filename} (file not found)")
            continue
            
        # Create PNG filename
        png_filename = svg_filename.replace('.svg', '.png')
        png_file = expected_dir / png_filename
        
        print(f"Converting {svg_filename}...")
        
        try:
            # Use the actual converter (not mocked)
            result = converter.convert_svg_file(str(svg_file), str(png_file))
            
            if result and png_file.exists():
                file_size = png_file.stat().st_size
                print(f"✅ Generated {png_filename} ({file_size:,} bytes)")
                successful_conversions += 1
            else:
                print(f"❌ Failed to generate {png_filename}")
                failed_conversions += 1
                
        except Exception as e:
            print(f"❌ Error converting {svg_filename}: {e}")
            failed_conversions += 1
    
    print("=" * 60)
    print(f"Conversion complete:")
    print(f"  ✅ Successful: {successful_conversions}")
    print(f"  ❌ Failed: {failed_conversions}")
    print(f"  📁 Expected directory: {expected_dir}")
    
    if successful_conversions > 0:
        print("\n🎉 Expected PNG files have been generated!")
        print("You can now run visual comparison tests.")
    else:
        print("\n⚠️  No PNG files were generated. Check your Playwright installation:")
        print("  uv run playwright install chromium")


if __name__ == "__main__":
    main()