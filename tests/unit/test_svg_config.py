"""Tests for SVG-specific configuration schema and validation."""

from __future__ import annotations

import pytest

from mkdocs_svg_to_png.config import SvgConfigManager
from mkdocs_svg_to_png.exceptions import SvgConfigError


class TestSvgConfigManager:
    """Test SVG configuration manager."""

    def test_get_svg_config_scheme_includes_required_options(self):
        """Test that SVG config scheme includes all required options."""
        config_scheme = SvgConfigManager.get_config_scheme()
        config_keys = {key for key, _ in config_scheme}

        # Basic plugin options
        assert "enabled" in config_keys
        assert "enabled_if_env" in config_keys
        assert "output_dir" in config_keys
        assert "error_on_fail" in config_keys
        assert "log_level" in config_keys

        # SVG-specific options
        assert "dpi" in config_keys
        assert "output_format" in config_keys
        assert "quality" in config_keys
        assert "background_color" in config_keys
        assert "cache_enabled" in config_keys

        # Should NOT include Mermaid-specific options
        assert "theme" not in config_keys
        assert "mmdc_path" not in config_keys
        assert "mermaid_config" not in config_keys
        assert "puppeteer_config" not in config_keys
        assert "width" not in config_keys
        assert "height" not in config_keys
        assert "scale" not in config_keys

    def test_svg_config_defaults(self):
        """Test SVG configuration default values."""
        config_scheme = SvgConfigManager.get_config_scheme()
        defaults = {
            key: option.default
            for key, option in config_scheme
            if hasattr(option, "default")
        }

        # Test SVG-specific defaults
        assert defaults["dpi"] == 300
        assert defaults["output_format"] == "png"
        assert defaults["quality"] == 95
        assert defaults["background_color"] == "transparent"
        assert defaults["cache_enabled"] is True
        assert defaults["error_on_fail"] is False

    def test_validate_svg_config_valid(self):
        """Test validation of valid SVG configuration."""
        valid_config = {
            "enabled": True,
            "dpi": 300,
            "output_format": "png",
            "quality": 95,
            "background_color": "white",
            "output_dir": "assets/images",
            "error_on_fail": False,
        }

        # Should not raise exception
        result = SvgConfigManager.validate_config(valid_config)
        assert result is True

    def test_validate_svg_config_invalid_dpi(self):
        """Test validation fails for invalid DPI."""
        invalid_config = {
            "enabled": True,
            "dpi": 0,
            "output_format": "png",
            "quality": 95,
        }

        with pytest.raises(SvgConfigError) as exc_info:
            SvgConfigManager.validate_config(invalid_config)

        assert "DPI must be a positive integer" in str(exc_info.value)
        assert exc_info.value.details["config_key"] == "dpi"
        assert exc_info.value.details["config_value"] == 0

    def test_validate_svg_config_invalid_quality(self):
        """Test validation fails for invalid quality."""
        invalid_config = {
            "enabled": True,
            "dpi": 300,
            "output_format": "png",
            "quality": 150,  # Should be 0-100
        }

        with pytest.raises(SvgConfigError) as exc_info:
            SvgConfigManager.validate_config(invalid_config)

        assert "Quality must be between 0 and 100" in str(exc_info.value)
        assert exc_info.value.details["config_key"] == "quality"
        assert exc_info.value.details["config_value"] == 150

    def test_validate_svg_config_invalid_output_format(self):
        """Test validation fails for unsupported output format."""
        invalid_config = {
            "enabled": True,
            "dpi": 300,
            "output_format": "jpeg",  # Only png supported
            "quality": 95,
        }

        with pytest.raises(SvgConfigError) as exc_info:
            SvgConfigManager.validate_config(invalid_config)

        assert "Unsupported output format" in str(exc_info.value)
        assert exc_info.value.details["config_key"] == "output_format"
        assert exc_info.value.details["config_value"] == "jpeg"

    def test_validate_svg_config_missing_required_key(self):
        """Test validation fails for missing required configuration."""
        incomplete_config = {
            "enabled": True,
            # Missing dpi
            "output_format": "png",
            "quality": 95,
        }

        with pytest.raises(SvgConfigError) as exc_info:
            SvgConfigManager.validate_config(incomplete_config)

        assert "Required configuration key 'dpi' is missing" in str(exc_info.value)
        assert exc_info.value.details["config_key"] == "dpi"

    def test_svg_config_scheme_types(self):
        """Test that config scheme has correct types."""
        config_scheme = SvgConfigManager.get_config_scheme()
        config_dict = dict(config_scheme)

        # Import the MkDocs config options for type checking
        from mkdocs.config import config_options

        # Check that dpi is an integer option
        assert isinstance(config_dict["dpi"], config_options.Type)

        # Check that output_format is a choice option
        assert isinstance(config_dict["output_format"], config_options.Choice)

        # Check that enabled is a boolean option
        assert isinstance(config_dict["enabled"], config_options.Type)
