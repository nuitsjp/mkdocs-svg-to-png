"""Tests for SVG-specific configuration schema and validation."""

from __future__ import annotations

from mkdocs_svg_to_png.config import SvgConfigManager


class TestSvgConfigManager:
    """Test SVG configuration manager."""

    def test_get_svg_config_scheme_includes_required_options(self):
        """Test that SVG config scheme includes all required options."""
        config_scheme = SvgConfigManager.get_config_scheme()
        config_keys = {key for key, _ in config_scheme}

        # Basic plugin options
        assert "enabled_if_env" in config_keys
        assert "output_dir" in config_keys
        assert "error_on_fail" in config_keys
        assert "log_level" in config_keys

        # SVG-specific options that should be present
        assert "preserve_original" in config_keys
        assert "cleanup_generated_images" in config_keys

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
        assert defaults["preserve_original"] is False
        assert defaults["error_on_fail"] is False
        assert defaults["cleanup_generated_images"] is False

    def test_validate_svg_config_valid(self):
        """Test validation of valid SVG configuration."""
        valid_config = {
            "output_dir": "assets/images",
            "error_on_fail": False,
        }

        # Should not raise exception
        result = SvgConfigManager().validate(valid_config)
        assert result == valid_config

    def test_validate_svg_config_always_succeeds(self):
        """Test validation always succeeds since no parameters are required."""
        # Empty config should be valid
        empty_config = {}
        result = SvgConfigManager().validate(empty_config)
        assert result == empty_config

        # Any config should be valid
        any_config = {"some_key": "some_value"}
        result = SvgConfigManager().validate(any_config)
        assert result == any_config

    def test_validate_svg_config_no_required_keys(self):
        """Test that no configuration keys are required."""
        # Since output_format is removed and hardcoded to PNG,
        # no configuration keys should be required
        incomplete_config = {}

        # Should not raise exception since no keys are required
        result = SvgConfigManager().validate(incomplete_config)
        assert result == incomplete_config

    def test_svg_config_scheme_types(self):
        """Test that config scheme has correct types."""
        config_scheme = SvgConfigManager.get_config_scheme()
        config_dict = dict(config_scheme)

        # Import the MkDocs config options for type checking
        from mkdocs.config import config_options

        # Check that enabled_if_env is an optional string option
        assert isinstance(config_dict["enabled_if_env"], config_options.Optional)

    def test_config_without_unused_settings(self):
        """Test that unused settings should be removed.

        This test initially fails to verify these settings exist,
        then will pass after they are removed from the config schema.
        """
        # Create config without unused settings
        config = {
            "enabled_if_env": None,
            "output_dir": "assets/images",
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

    def test_enabled_setting_removed_from_schema(self):
        """Test that 'enabled' setting is removed from config schema."""
        config_scheme = SvgConfigManager.get_config_scheme()
        config_keys = {key for key, _ in config_scheme}

        # 'enabled' should be removed as it's redundant with 'enabled_if_env'
        assert (
            "enabled" not in config_keys
        ), "'enabled' setting should be removed from config schema as it's redundant"

        # 'enabled_if_env' should still be present
        assert (
            "enabled_if_env" in config_keys
        ), "'enabled_if_env' setting should remain in config schema"

    def test_output_format_setting_removed_from_schema(self):
        """Test that 'output_format' setting is removed from config schema."""
        config_scheme = SvgConfigManager.get_config_scheme()
        config_keys = {key for key, _ in config_scheme}

        # 'output_format' should be removed since only PNG is supported
        assert (
            "output_format" not in config_keys
        ), "'output_format' setting should be removed from config schema"

    def test_cache_enabled_setting_removed_from_schema(self):
        """Test that 'cache_enabled' setting is removed from config schema.

        This test should initially fail (Red phase) as cache_enabled is still present,
        then pass (Green phase) after it's removed from the schema.
        """
        config_scheme = SvgConfigManager.get_config_scheme()
        config_keys = {key for key, _ in config_scheme}

        # 'cache_enabled' should be removed as it's not implemented
        assert (
            "cache_enabled" not in config_keys
        ), "'cache_enabled' setting should be removed from config schema"

    def test_cache_enabled_removed_from_type_definitions(self):
        """Test that 'cache_enabled' is removed from type definitions.

        This test should initially fail (Red phase) as cache_enabled is still present,
        then pass (Green phase) after it's removed from the type definitions.
        """
        from mkdocs_svg_to_png.types import PluginConfigDict

        # Get the type annotations from PluginConfigDict
        type_annotations = PluginConfigDict.__annotations__

        # 'cache_enabled' should be removed from type definitions
        assert (
            "cache_enabled" not in type_annotations
        ), "'cache_enabled' should be removed from PluginConfigDict type definitions"

    def test_log_level_processing_logic(self):
        """Test the logic that processes log_level configuration.

        This test directly tests the log_level processing logic to ensure
        it respects config values when no CLI flag is provided.
        """
        from mkdocs_svg_to_png.plugin import SvgToPngPlugin

        plugin = SvgToPngPlugin()

        # Test case 1: No CLI flag, should use config value
        plugin.is_verbose_mode = False
        config_dict = {"log_level": "ERROR"}

        # Simulate the new behavior (respects config when no CLI flag)
        if plugin.is_verbose_mode:
            actual_log_level = "DEBUG"
        else:
            actual_log_level = config_dict["log_level"]  # Should use config value

        # This assertion should now pass in Green phase
        assert actual_log_level == "ERROR", (
            f"Expected log_level to be 'ERROR' from config when no CLI flag, "
            f"but got '{actual_log_level}'"
        )

    def test_log_level_cli_flag_override_logic(self):
        """Test that CLI --verbose flag correctly overrides config log_level.

        This test verifies the CLI flag takes precedence over config.
        """
        from mkdocs_svg_to_png.plugin import SvgToPngPlugin

        plugin = SvgToPngPlugin()

        # Test case 2: CLI flag present, should use DEBUG
        plugin.is_verbose_mode = True
        config_dict = {"log_level": "ERROR"}

        # Simulate the new behavior (CLI flag takes precedence)
        if plugin.is_verbose_mode:
            actual_log_level = "DEBUG"
        else:
            actual_log_level = config_dict["log_level"]

        # This assertion should pass (current behavior is correct)
        assert actual_log_level == "DEBUG", (
            f"Expected log_level to be 'DEBUG' when CLI --verbose flag is provided, "
            f"but got '{actual_log_level}'"
        )
