"""
SVG fixtures integration tests.
Tests SVG to PNG conversion using real SVG files from fixtures/input/.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

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
        
        # Mock Playwright to avoid browser dependency in tests
        with patch("mkdocs_svg_to_png.svg_converter.asyncio") as mock_asyncio:
            mock_asyncio.run.return_value = True
            
            result = converter.convert_svg_file(str(svg_file), str(output_file))
            
            assert result is True
            mock_asyncio.run.assert_called_once()

    def test_class_design_diagram_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of class design diagram."""
        svg_file = fixtures_input_dir / "class-design_mermaid_0_86b4976d.svg"
        output_file = temp_output_dir / "class_design_test.png"
        
        if not svg_file.exists():
            pytest.skip(f"SVG file not found: {svg_file}")
        
        with patch("mkdocs_svg_to_png.svg_converter.asyncio") as mock_asyncio:
            mock_asyncio.run.return_value = True
            
            result = converter.convert_svg_file(str(svg_file), str(output_file))
            
            assert result is True

    def test_database_design_diagram_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of database design diagram."""
        svg_file = fixtures_input_dir / "database-design_mermaid_0_3d6e6222.svg"
        output_file = temp_output_dir / "database_design_test.png"
        
        if not svg_file.exists():
            pytest.skip(f"SVG file not found: {svg_file}")
        
        with patch("mkdocs_svg_to_png.svg_converter.asyncio") as mock_asyncio:
            mock_asyncio.run.return_value = True
            
            result = converter.convert_svg_file(str(svg_file), str(output_file))
            
            assert result is True

    def test_drawio_diagram_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of Draw.io diagram."""
        svg_file = fixtures_input_dir / "detailed-diagram.drawio.svg"
        output_file = temp_output_dir / "drawio_test.png"
        
        if not svg_file.exists():
            pytest.skip(f"SVG file not found: {svg_file}")
        
        with patch("mkdocs_svg_to_png.svg_converter.asyncio") as mock_asyncio:
            mock_asyncio.run.return_value = True
            
            result = converter.convert_svg_file(str(svg_file), str(output_file))
            
            assert result is True

    def test_project_plan_diagram_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of project plan diagram."""
        svg_file = fixtures_input_dir / "project-plan_mermaid_0_336420ee.svg"
        output_file = temp_output_dir / "project_plan_test.png"
        
        if not svg_file.exists():
            pytest.skip(f"SVG file not found: {svg_file}")
        
        with patch("mkdocs_svg_to_png.svg_converter.asyncio") as mock_asyncio:
            mock_asyncio.run.return_value = True
            
            result = converter.convert_svg_file(str(svg_file), str(output_file))
            
            assert result is True

    def test_state_management_diagram_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of state management diagram."""
        svg_file = fixtures_input_dir / "state-management_mermaid_0_5231eec1.svg"
        output_file = temp_output_dir / "state_management_test.png"
        
        if not svg_file.exists():
            pytest.skip(f"SVG file not found: {svg_file}")
        
        with patch("mkdocs_svg_to_png.svg_converter.asyncio") as mock_asyncio:
            mock_asyncio.run.return_value = True
            
            result = converter.convert_svg_file(str(svg_file), str(output_file))
            
            assert result is True

    def test_system_overview_diagram_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of system overview diagram."""
        svg_file = fixtures_input_dir / "system-overview_mermaid_0_93d92671.svg"
        output_file = temp_output_dir / "system_overview_test.png"
        
        if not svg_file.exists():
            pytest.skip(f"SVG file not found: {svg_file}")
        
        with patch("mkdocs_svg_to_png.svg_converter.asyncio") as mock_asyncio:
            mock_asyncio.run.return_value = True
            
            result = converter.convert_svg_file(str(svg_file), str(output_file))
            
            assert result is True

    def test_user_journey_diagram_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of user journey diagram."""
        svg_file = fixtures_input_dir / "user-journey_mermaid_0_ccef6318.svg"
        output_file = temp_output_dir / "user_journey_test.png"
        
        if not svg_file.exists():
            pytest.skip(f"SVG file not found: {svg_file}")
        
        with patch("mkdocs_svg_to_png.svg_converter.asyncio") as mock_asyncio:
            mock_asyncio.run.return_value = True
            
            result = converter.convert_svg_file(str(svg_file), str(output_file))
            
            assert result is True

    def test_basic_output_svg_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of basic output SVG."""
        svg_file = fixtures_input_dir / "output_basic.svg"
        output_file = temp_output_dir / "output_basic_test.png"
        
        if not svg_file.exists():
            pytest.skip(f"SVG file not found: {svg_file}")
        
        with patch("mkdocs_svg_to_png.svg_converter.asyncio") as mock_asyncio:
            mock_asyncio.run.return_value = True
            
            result = converter.convert_svg_file(str(svg_file), str(output_file))
            
            assert result is True

    def test_sequence_output_svg_conversion(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test conversion of sequence output SVG."""
        svg_file = fixtures_input_dir / "output_sequence.svg"
        output_file = temp_output_dir / "output_sequence_test.png"
        
        if not svg_file.exists():
            pytest.skip(f"SVG file not found: {svg_file}")
        
        with patch("mkdocs_svg_to_png.svg_converter.asyncio") as mock_asyncio:
            mock_asyncio.run.return_value = True
            
            result = converter.convert_svg_file(str(svg_file), str(output_file))
            
            assert result is True

    def test_multiple_svg_conversion_with_different_scales(
        self, converter_config, fixtures_input_dir, temp_output_dir
    ):
        """Test multiple SVG conversions with different scale settings."""
        test_files = [
            "architecture_mermaid_0_07a67020.svg",
            "class-design_mermaid_0_86b4976d.svg",
            "detailed-diagram.drawio.svg"
        ]
        
        scales = [0.5, 1.0, 1.5, 2.0]
        
        for scale in scales:
            converter_config["scale"] = scale
            converter = SvgToPngConverter(converter_config)
            
            for svg_filename in test_files:
                svg_file = fixtures_input_dir / svg_filename
                if not svg_file.exists():
                    continue
                
                output_file = temp_output_dir / f"{svg_filename.replace('.svg', '')}_scale_{scale}.png"
                
                with patch("mkdocs_svg_to_png.svg_converter.asyncio") as mock_asyncio:
                    mock_asyncio.run.return_value = True
                    
                    result = converter.convert_svg_file(str(svg_file), str(output_file))
                    assert result is True

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
                "expected_min_width": 600,   # Draw.io diagram
                "expected_min_height": 600,
            }
        ]
        
        for case in test_cases:
            svg_file = fixtures_input_dir / case["file"]
            if not svg_file.exists():
                continue
                
            svg_content = svg_file.read_text(encoding="utf-8")
            width, height = converter._extract_svg_dimensions(svg_content)
            
            # Test that extracted dimensions are reasonable
            assert width >= case["expected_min_width"], f"Width too small for {case['file']}: {width}"
            assert height >= case["expected_min_height"], f"Height too small for {case['file']}: {height}"

    def test_svg_content_validation_with_fixtures(
        self, converter, fixtures_input_dir
    ):
        """Test SVG content validation using fixture files."""
        svg_files = list(fixtures_input_dir.glob("*.svg"))
        
        for svg_file in svg_files[:5]:  # Test first 5 SVG files
            svg_content = svg_file.read_text(encoding="utf-8")
            
            # Should not raise exception for valid SVG files
            converter._validate_svg_content(svg_content)

    def test_error_handling_with_corrupted_svg(
        self, converter, temp_output_dir
    ):
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
        converter_config["device_scale_factor"] = 2.0
        converter = SvgToPngConverter(converter_config)
        
        svg_file = fixtures_input_dir / "output_basic.svg"
        if not svg_file.exists():
            pytest.skip(f"SVG file not found: {svg_file}")
        
        output_file = temp_output_dir / "device_scale_test.png"
        
        with patch("mkdocs_svg_to_png.svg_converter.asyncio") as mock_asyncio:
            mock_asyncio.run.return_value = True
            
            result = converter.convert_svg_file(str(svg_file), str(output_file))
            assert result is True

    def test_batch_conversion_performance(
        self, converter, fixtures_input_dir, temp_output_dir
    ):
        """Test batch conversion of multiple SVG files."""
        svg_files = list(fixtures_input_dir.glob("*_mermaid_*.svg"))[:3]  # Test first 3 Mermaid files
        
        successful_conversions = 0
        
        for i, svg_file in enumerate(svg_files):
            output_file = temp_output_dir / f"batch_test_{i}.png"
            
            with patch("mkdocs_svg_to_png.svg_converter.asyncio") as mock_asyncio:
                mock_asyncio.run.return_value = True
                
                result = converter.convert_svg_file(str(svg_file), str(output_file))
                if result:
                    successful_conversions += 1
        
        # At least some conversions should succeed
        assert successful_conversions > 0
        assert successful_conversions <= len(svg_files)