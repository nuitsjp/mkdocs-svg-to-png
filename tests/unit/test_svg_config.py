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
        assert "output_format" in config_keys
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
        assert defaults["output_format"] == "png"
        assert defaults["cache_enabled"] is True
        assert defaults["error_on_fail"] is False

    def test_validate_svg_config_valid(self):
        """Test validation of valid SVG configuration."""
        valid_config = {
            "enabled": True,
            "output_format": "png",
            "output_dir": "assets/images",
            "error_on_fail": False,
        }

        # Should not raise exception
        result = SvgConfigManager().validate(valid_config)
        assert result == valid_config

    def test_validate_svg_config_invalid_output_format(self):
        """Test validation fails for unsupported output format."""
        invalid_config = {
            "enabled": True,
            "output_format": "jpeg",  # Only png supported
        }

        with pytest.raises(SvgConfigError) as exc_info:
            SvgConfigManager().validate(invalid_config)

        assert "Unsupported output format" in str(exc_info.value)
        assert exc_info.value.details["config_key"] == "output_format"
        assert exc_info.value.details["config_value"] == "jpeg"

    def test_validate_svg_config_missing_required_key(self):
        """Test validation fails for missing required configuration."""
        incomplete_config = {
            "enabled": True,
            # Missing output_format
        }

        with pytest.raises(SvgConfigError) as exc_info:
            SvgConfigManager().validate(incomplete_config)

        assert "Required configuration key 'output_format' is missing" in str(
            exc_info.value
        )
        assert exc_info.value.details["config_key"] == "output_format"

    def test_svg_config_scheme_types(self):
        """Test that config scheme has correct types."""
        config_scheme = SvgConfigManager.get_config_scheme()
        config_dict = dict(config_scheme)

        # Import the MkDocs config options for type checking
        from mkdocs.config import config_options

        # Check that output_format is a choice option
        assert isinstance(config_dict["output_format"], config_options.Choice)

        # Check that enabled is a boolean option
        assert isinstance(config_dict["enabled"], config_options.Type)

    def test_config_without_unused_settings(self):
        """Test that unused settings should be removed.

        This test initially fails to verify these settings exist,
        then will pass after they are removed from the config schema.
        """
        # Create config without unused settings
        config = {
            "enabled": True,
            "enabled_if_env": None,
            "output_dir": "assets/images",
            "output_format": "png",
            "cache_enabled": True,
            "cache_dir": ".svg_cache",
            "preserve_original": False,
            "error_on_fail": False,
            "log_level": "INFO",
            "cleanup_generated_images": False,
        }

        # Currently this test will fail because validation requires dpi, quality
        # After removal, this should pass
        manager = SvgConfigManager()

        # This should not raise an exception after unused settings are removed
        try:
            result = manager.validate(config)
            # If validation passes, unused settings have been successfully removed
            assert result == config
            unused_settings_removed = True
        except Exception:
            # If validation fails, unused settings are still present
            unused_settings_removed = False

        # After removal, unused settings should not be required anymore
        assert (
            unused_settings_removed
        ), "Config validation should pass without unused settings"

    def test_unused_settings_removed_from_schema(self):
        """Test that unused settings are completely removed from config schema."""
        config_scheme = SvgConfigManager.get_config_scheme()
        config_keys = {key for key, _ in config_scheme}

        # These settings should be removed
        removed_settings = ["dpi", "quality", "background_color", "temp_dir"]

        for setting in removed_settings:
            assert (
                setting not in config_keys
            ), f"Unused setting '{setting}' should be removed from config schema"
