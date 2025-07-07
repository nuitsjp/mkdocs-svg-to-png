"""
SVG fixtures integration tests.
Tests SVG to PNG conversion using real SVG files from fixtures/input/.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from mkdocs_svg_to_png.svg_converter import SvgToPngConverter


class TestSvgFixturesIntegration:
    """Integration tests using real SVG files from fixtures."""

    @pytest.fixture
    def fixtures_input_dir(self):
        """Path to fixtures input directory."""
        return Path(__file__).parent.parent.parent / "fixtures" / "input"

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def converter_config(self):
        """Basic converter configuration."""
        return {
            "scale": 1.0,
            "device_scale_factor": 1.0,
            "default_width": 800,
            "default_height": 600,
            "error_on_fail": False,
        }

    @pytest.fixture
    def converter(self, converter_config):
        """SvgToPngConverter instance."""
        return SvgToPngConverter(converter_config)

    def test_detailed_diagram_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of detailed diagram (main SVG conversion test)."""
        svg_file = fixtures_input_dir / "detailed-diagram.drawio.svg"
        output_file = temp_output_dir / "detailed_diagram_test.png"

        if not svg_file.exists():
            pytest.skip(f"SVG file not found: {svg_file}")

        # Test actual conversion (this is our main real conversion test)
        result = converter.convert_svg_file(str(svg_file), str(output_file))

        assert result is True, f"Conversion failed for {svg_file}"
        assert output_file.exists()
        assert output_file.stat().st_size > 1000  # Basic size check

    def test_svg_dimension_extraction_from_fixtures(
        self, converter, fixtures_input_dir
    ):
        """Test SVG dimension extraction from detailed diagram fixture."""
        test_cases = [
            {
                "file": "detailed-diagram.drawio.svg",
                "expected_min_width": 600,  # Draw.io diagram
                "expected_min_height": 600,
            },
        ]

        for case in test_cases:
            svg_file = fixtures_input_dir / case["file"]
            if not svg_file.exists():
                continue

            svg_content = svg_file.read_text(encoding="utf-8")
            width, height = converter._extract_svg_dimensions(svg_content)

            # Test that extracted dimensions are reasonable
            assert (
                width >= case["expected_min_width"]
            ), f"Width too small for {case['file']}: {width}"
            assert (
                height >= case["expected_min_height"]
            ), f"Height too small for {case['file']}: {height}"

    def test_svg_content_validation_with_fixtures(self, converter, fixtures_input_dir):
        """Test SVG content validation using fixture files."""
        svg_files = list(fixtures_input_dir.glob("*.svg"))

        for svg_file in svg_files:  # Test all remaining SVG files
            svg_content = svg_file.read_text(encoding="utf-8")

            # Should not raise exception for valid SVG files
            converter._validate_svg_content(svg_content)

    def test_error_handling_with_corrupted_svg(self, converter, temp_output_dir):
        """Test error handling with corrupted SVG content."""
        corrupted_svg = "<svg><invalid>malformed content</svg>"
        output_file = temp_output_dir / "corrupted_test.png"

        # Should return False when error_on_fail is False
        result = converter.convert_svg_content(corrupted_svg, str(output_file))
        assert result is False
