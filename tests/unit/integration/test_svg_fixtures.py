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

    def test_mermaid_architecture_diagram_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of Mermaid architecture diagram."""
        svg_file = fixtures_input_dir / "architecture_mermaid_0_07a67020.svg"
        output_file = temp_output_dir / "architecture_test.png"

        if not svg_file.exists():
            pytest.skip(f"SVG file not found: {svg_file}")

        # Test actual conversion (this is our main real conversion test)
        result = converter.convert_svg_file(str(svg_file), str(output_file))

        assert result is True, f"Conversion failed for {svg_file}"
        assert output_file.exists()
        assert output_file.stat().st_size > 1000  # Basic size check

    def test_class_design_diagram_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of class design diagram."""
        svg_file = fixtures_input_dir / "class-design_mermaid_0_86b4976d.svg"
        output_file = temp_output_dir / "class_design_test.png"

        if not svg_file.exists():
            pytest.skip(f"SVG file not found: {svg_file}")

        # Test actual conversion
        result = converter.convert_svg_file(str(svg_file), str(output_file))

        assert result is True, f"Conversion failed for {svg_file}"
        assert output_file.exists()
        assert output_file.stat().st_size > 1000  # Basic size check

    def test_database_design_diagram_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of database design diagram."""
        # Skip this test to reduce execution time
        pytest.skip("Skipping - actual conversion tested elsewhere")

    def test_drawio_diagram_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of Draw.io diagram."""
        # Skip this test to reduce execution time
        pytest.skip("Skipping - actual conversion tested elsewhere")

    def test_project_plan_diagram_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of project plan diagram."""
        # Skip this test to reduce execution time
        pytest.skip("Skipping - actual conversion tested elsewhere")

    def test_state_management_diagram_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of state management diagram."""
        # Skip this test to reduce execution time
        pytest.skip("Skipping - actual conversion tested elsewhere")

    def test_system_overview_diagram_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of system overview diagram."""
        # Skip this test to reduce execution time
        pytest.skip("Skipping - actual conversion tested elsewhere")

    def test_user_journey_diagram_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of user journey diagram."""
        # Skip this test to reduce execution time
        pytest.skip("Skipping - actual conversion tested elsewhere")

    def test_basic_output_svg_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of basic output SVG."""
        svg_file = fixtures_input_dir / "output_basic.svg"
        output_file = temp_output_dir / "output_basic_test.png"

        if not svg_file.exists():
            pytest.skip(f"SVG file not found: {svg_file}")

        # Test actual conversion for basic SVG
        result = converter.convert_svg_file(str(svg_file), str(output_file))

        assert result is True, f"Conversion failed for {svg_file}"
        assert output_file.exists()
        assert output_file.stat().st_size > 1000  # Basic size check

    def test_sequence_output_svg_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of sequence output SVG."""
        # Skip this test to reduce execution time
        pytest.skip("Skipping - actual conversion tested elsewhere")

    def test_multiple_svg_conversion_with_different_scales(
        self, converter_config, fixtures_input_dir, temp_output_dir
    ):
        """Test multiple SVG conversions with different scale settings."""
        # Skip this test to reduce execution time
        pytest.skip("Skipping - actual conversion tested elsewhere")

    def test_svg_dimension_extraction_from_fixtures(
        self, converter, fixtures_input_dir
    ):
        """Test SVG dimension extraction from various fixture files."""
        test_cases = [
            {
                "file": "architecture_mermaid_0_07a67020.svg",
                "expected_min_width": 1000,  # Large architecture diagram
                "expected_min_height": 500,
            },
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

        for svg_file in svg_files[:5]:  # Test first 5 SVG files
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

    def test_conversion_with_custom_device_scale_factor(
        self, converter_config, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion with custom device scale factor."""
        # Skip this test to reduce execution time
        pytest.skip("Skipping - actual conversion tested elsewhere")

    def test_batch_conversion_performance(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test batch conversion of multiple SVG files."""
        # Skip this test to reduce execution time
        pytest.skip("Skipping - actual conversion tested elsewhere")
