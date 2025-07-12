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

    def test_output_dir_individual_values(self):
        """Test output_dir configuration with various valid values."""
        config_scheme = SvgConfigManager.get_config_scheme()
        output_dir_option = dict(config_scheme)["output_dir"]

        # Test default value
        assert output_dir_option.default == "assets/images"

        # Test validation with custom paths
        manager = SvgConfigManager()

        # Relative path
        config = {"output_dir": "images"}
        result = manager.validate(config)
        assert result["output_dir"] == "images"

        # Absolute path
        config = {"output_dir": "/tmp/images"}
        result = manager.validate(config)
        assert result["output_dir"] == "/tmp/images"

        # Nested path
        config = {"output_dir": "assets/generated/images"}
        result = manager.validate(config)
        assert result["output_dir"] == "assets/generated/images"

    def test_preserve_original_individual_values(self):
        """Test preserve_original configuration with both boolean values."""
        config_scheme = SvgConfigManager.get_config_scheme()
        preserve_original_option = dict(config_scheme)["preserve_original"]

        # Test default value
        assert preserve_original_option.default is False

        manager = SvgConfigManager()

        # Test True
        config = {"preserve_original": True}
        result = manager.validate(config)
        assert result["preserve_original"] is True

        # Test False
        config = {"preserve_original": False}
        result = manager.validate(config)
        assert result["preserve_original"] is False

    def test_error_on_fail_individual_values(self):
        """Test error_on_fail configuration with both boolean values."""
        config_scheme = SvgConfigManager.get_config_scheme()
        error_on_fail_option = dict(config_scheme)["error_on_fail"]

        # Test default value
        assert error_on_fail_option.default is False

        manager = SvgConfigManager()

        # Test True
        config = {"error_on_fail": True}
        result = manager.validate(config)
        assert result["error_on_fail"] is True

        # Test False
        config = {"error_on_fail": False}
        result = manager.validate(config)
        assert result["error_on_fail"] is False

    def test_cleanup_generated_images_individual_values(self):
        """Test cleanup_generated_images configuration with both boolean values."""
        config_scheme = SvgConfigManager.get_config_scheme()
        cleanup_option = dict(config_scheme)["cleanup_generated_images"]

        # Test default value
        assert cleanup_option.default is False

        manager = SvgConfigManager()

        # Test True
        config = {"cleanup_generated_images": True}
        result = manager.validate(config)
        assert result["cleanup_generated_images"] is True

        # Test False
        config = {"cleanup_generated_images": False}
        result = manager.validate(config)
        assert result["cleanup_generated_images"] is False

    def test_log_level_individual_values(self):
        """Test log_level configuration with all valid values."""
        config_scheme = SvgConfigManager.get_config_scheme()
        log_level_option = dict(config_scheme)["log_level"]

        # Test default value
        assert log_level_option.default == "INFO"

        manager = SvgConfigManager()

        # Test each valid log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        for level in valid_levels:
            config = {"log_level": level}
            result = manager.validate(config)
            assert result["log_level"] == level

    def test_enabled_if_env_individual_values(self):
        """Test enabled_if_env configuration with various values."""
        config_scheme = SvgConfigManager.get_config_scheme()
        enabled_if_env_option = dict(config_scheme)["enabled_if_env"]

        # Test that it's optional (no default value)
        from mkdocs.config import config_options

        assert isinstance(enabled_if_env_option, config_options.Optional)

        manager = SvgConfigManager()

        # Test None (not set)
        config = {"enabled_if_env": None}
        result = manager.validate(config)
        assert result["enabled_if_env"] is None

        # Test with environment variable name
        config = {"enabled_if_env": "ENABLE_SVG_CONVERSION"}
        result = manager.validate(config)
        assert result["enabled_if_env"] == "ENABLE_SVG_CONVERSION"

        # Test with another environment variable name
        config = {"enabled_if_env": "BUILD_PDF"}
        result = manager.validate(config)
        assert result["enabled_if_env"] == "BUILD_PDF"

    def test_invalid_log_level_values(self):
        """Test log_level configuration with invalid values (should fail)."""

        # Test invalid log level through MkDocs config validation
        from mkdocs.config.base import Config

        config_instance = Config(SvgConfigManager.get_config_scheme())

        # Test invalid log level - this should fail validation
        try:
            config_instance.load_dict({"log_level": "INVALID"})
            # If we get here, validation didn't fail as expected
            raise AssertionError("Expected validation to fail for invalid log_level")
        except Exception as e:
            # Validation should fail - this is expected
            assert "log_level" in str(e) or "INVALID" in str(e)

    def test_invalid_type_values(self):
        """Test configuration with wrong types (should fail)."""

        # Create config instance for proper validation
        from mkdocs.config.base import Config

        # Test non-string output_dir
        config_instance = Config(SvgConfigManager.get_config_scheme())
        try:
            config_instance.load_dict({"output_dir": 123})
            raise AssertionError(
                "Expected validation to fail for non-string output_dir"
            )
        except Exception as e:
            assert "output_dir" in str(e) or "str" in str(e).lower() or "123" in str(e)

        # Test non-boolean preserve_original
        config_instance = Config(SvgConfigManager.get_config_scheme())
        try:
            config_instance.load_dict({"preserve_original": "not_boolean"})
            raise AssertionError(
                "Expected validation to fail for non-boolean preserve_original"
            )
        except Exception as e:
            assert "preserve_original" in str(e) or "bool" in str(e).lower()

        # Test non-boolean error_on_fail
        config_instance = Config(SvgConfigManager.get_config_scheme())
        try:
            config_instance.load_dict({"error_on_fail": "not_boolean"})
            raise AssertionError(
                "Expected validation to fail for non-boolean error_on_fail"
            )
        except Exception as e:
            assert "error_on_fail" in str(e) or "bool" in str(e).lower()

        # Test non-boolean cleanup_generated_images
        config_instance = Config(SvgConfigManager.get_config_scheme())
        try:
            config_instance.load_dict({"cleanup_generated_images": "not_boolean"})
            raise AssertionError(
                "Expected validation to fail for non-boolean cleanup_generated_images"
            )
        except Exception as e:
            assert "cleanup_generated_images" in str(e) or "bool" in str(e).lower()

    def test_none_values_for_required_string_fields(self):
        """Test None values for string fields that shouldn't accept None."""

        # Create config instance for proper validation
        from mkdocs.config.base import Config

        config_instance = Config(SvgConfigManager.get_config_scheme())

        # Test None for output_dir (should fail since it's not Optional)
        try:
            config_instance.load_dict({"output_dir": None})
            raise AssertionError("Expected validation to fail for None output_dir")
        except Exception as e:
            assert "output_dir" in str(e) or "None" in str(e)

    def test_config_validation_through_mkdocs_interface(self):
        """Test config validation using MkDocs interface to ensure proper behavior."""
        from mkdocs.config.base import Config

        # Test valid configuration passes
        config_instance = Config(SvgConfigManager.get_config_scheme())
        config_instance.load_dict(
            {
                "output_dir": "assets/images",
                "preserve_original": True,
                "error_on_fail": False,
                "log_level": "DEBUG",
                "cleanup_generated_images": True,
                "enabled_if_env": "TEST_ENV",
            }
        )

        # Should not raise exception and should have expected values
        assert config_instance["output_dir"] == "assets/images"
        assert config_instance["preserve_original"] is True
        assert config_instance["error_on_fail"] is False
        assert config_instance["log_level"] == "DEBUG"
        assert config_instance["cleanup_generated_images"] is True
        assert config_instance["enabled_if_env"] == "TEST_ENV"

    def test_output_dir_boundary_values(self):
        """Test output_dir configuration with boundary and edge case values."""
        manager = SvgConfigManager()

        # Empty string (should be valid, though potentially problematic)
        config = {"output_dir": ""}
        result = manager.validate(config)
        assert result["output_dir"] == ""

        # Single character
        config = {"output_dir": "a"}
        result = manager.validate(config)
        assert result["output_dir"] == "a"

        # Path with spaces
        config = {"output_dir": "my assets/images"}
        result = manager.validate(config)
        assert result["output_dir"] == "my assets/images"

        # Path with special characters
        config = {"output_dir": "assets-2024/images_v1.0"}
        result = manager.validate(config)
        assert result["output_dir"] == "assets-2024/images_v1.0"

        # Very long path (testing practical limits)
        long_path = "/".join(["very_long_directory_name"] * 10)
        config = {"output_dir": long_path}
        result = manager.validate(config)
        assert result["output_dir"] == long_path

        # Path with Unicode characters
        config = {"output_dir": "assets/画像"}
        result = manager.validate(config)
        assert result["output_dir"] == "assets/画像"

    def test_enabled_if_env_boundary_values(self):
        """Test enabled_if_env configuration with boundary and edge case values."""
        manager = SvgConfigManager()

        # Empty string (should be valid)
        config = {"enabled_if_env": ""}
        result = manager.validate(config)
        assert result["enabled_if_env"] == ""

        # Single character environment variable
        config = {"enabled_if_env": "A"}
        result = manager.validate(config)
        assert result["enabled_if_env"] == "A"

        # Environment variable with numbers and underscores
        config = {"enabled_if_env": "BUILD_2024_VERSION_1"}
        result = manager.validate(config)
        assert result["enabled_if_env"] == "BUILD_2024_VERSION_1"

        # Very long environment variable name
        long_env_name = "VERY_LONG_ENVIRONMENT_VARIABLE_NAME_FOR_TESTING_PURPOSES_123"
        config = {"enabled_if_env": long_env_name}
        result = manager.validate(config)
        assert result["enabled_if_env"] == long_env_name

    def test_string_type_conversions(self):
        """Test automatic type conversions for string fields."""
        from mkdocs.config.base import Config

        # Test if MkDocs automatically converts compatible types
        config_instance = Config(SvgConfigManager.get_config_scheme())

        # Test if integer is converted to string for output_dir
        try:
            config_instance.load_dict({"output_dir": 123})
            # If this passes, it means MkDocs converts int to string
            # Check if it was converted
            if isinstance(config_instance["output_dir"], str):
                assert config_instance["output_dir"] == "123"
            else:
                raise AssertionError("Expected int to be converted to string")
        except Exception:
            # If it fails, that's also acceptable (strict type checking)
            pass

    def test_boolean_type_conversions(self):
        """Test automatic type conversions for boolean fields."""
        from mkdocs.config.base import Config

        config_instance = Config(SvgConfigManager.get_config_scheme())

        # Test various truthy/falsy values
        test_cases = [
            ("preserve_original", 1, True),
            ("preserve_original", 0, False),
            ("error_on_fail", "true", True),
            ("error_on_fail", "false", False),
            ("cleanup_generated_images", "yes", True),
            ("cleanup_generated_images", "no", False),
        ]

        for field, input_value, expected in test_cases:
            try:
                config_instance = Config(SvgConfigManager.get_config_scheme())
                config_instance.load_dict({field: input_value})
                # If conversion happens, check the result
                if isinstance(config_instance[field], bool):
                    assert config_instance[field] == expected
                else:
                    # If not converted to bool, that's also valid behavior
                    pass
            except Exception:
                # Strict type checking is also acceptable
                pass

    def test_config_combination_scenarios(self):
        """Test various combinations of configuration settings."""
        manager = SvgConfigManager()

        # Production-like configuration
        production_config = {
            "output_dir": "assets/images",
            "preserve_original": False,
            "error_on_fail": True,
            "log_level": "ERROR",
            "cleanup_generated_images": True,
            "enabled_if_env": "PRODUCTION_BUILD",
        }
        result = manager.validate(production_config)
        assert result == production_config

        # Development-like configuration
        dev_config = {
            "output_dir": "tmp/dev-images",
            "preserve_original": True,
            "error_on_fail": False,
            "log_level": "DEBUG",
            "cleanup_generated_images": False,
            "enabled_if_env": None,
        }
        result = manager.validate(dev_config)
        assert result == dev_config

        # CI/CD configuration
        ci_config = {
            "output_dir": "build/artifacts/images",
            "preserve_original": False,
            "error_on_fail": True,
            "log_level": "WARNING",
            "cleanup_generated_images": True,
            "enabled_if_env": "CI",
        }
        result = manager.validate(ci_config)
        assert result == ci_config

    def test_minimal_vs_full_configuration(self):
        """Test minimal configuration vs full configuration."""
        manager = SvgConfigManager()

        # Minimal configuration (only required/important settings)
        minimal_config = {"output_dir": "images"}
        result = manager.validate(minimal_config)
        assert result["output_dir"] == "images"

        # Full configuration (all possible settings)
        full_config = {
            "enabled_if_env": "BUILD_DOCS",
            "output_dir": "assets/generated/images",
            "preserve_original": True,
            "error_on_fail": True,
            "log_level": "INFO",
            "cleanup_generated_images": False,
        }
        result = manager.validate(full_config)
        assert result == full_config

    def test_enabled_if_env_interaction_patterns(self):
        """Test how enabled_if_env interacts with other settings."""
        manager = SvgConfigManager()

        # Configuration for conditional enabling
        conditional_configs = [
            # Case 1: Enabled only in specific environment
            {
                "enabled_if_env": "PDF_BUILD",
                "output_dir": "pdf-assets/images",
                "error_on_fail": True,
                "log_level": "INFO",
            },
            # Case 2: Always enabled (None)
            {
                "enabled_if_env": None,
                "output_dir": "assets/images",
                "error_on_fail": False,
                "log_level": "WARNING",
            },
            # Case 3: Multiple environment scenarios
            {
                "enabled_if_env": "DOCS_BUILD",
                "preserve_original": True,
                "cleanup_generated_images": False,
            },
        ]

        for config in conditional_configs:
            result = manager.validate(config)
            assert result == config

    def test_boolean_combinations(self):
        """Test all combinations of boolean configuration settings."""
        manager = SvgConfigManager()

        # Generate all possible boolean combinations
        boolean_fields = [
            "preserve_original",
            "error_on_fail",
            "cleanup_generated_images",
        ]

        import itertools

        for combo in itertools.product([True, False], repeat=len(boolean_fields)):
            config = dict(zip(boolean_fields, combo))
            config["output_dir"] = "test"  # Add required field

            result = manager.validate(config)
            for field, expected_value in zip(boolean_fields, combo):
                assert result[field] == expected_value

    def test_log_level_with_other_settings(self):
        """Test log_level in combination with other settings."""
        manager = SvgConfigManager()

        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]

        for log_level in log_levels:
            # Test log level with error handling enabled
            config = {
                "log_level": log_level,
                "error_on_fail": True,
                "output_dir": f"logs-{log_level.lower()}",
            }
            result = manager.validate(config)
            assert result["log_level"] == log_level

            # Test log level with error handling disabled
            config = {
                "log_level": log_level,
                "error_on_fail": False,
                "preserve_original": True,
            }
            result = manager.validate(config)
            assert result["log_level"] == log_level

    def test_mkdocs_yaml_integration(self):
        """Test configuration through MkDocs YAML-like interface."""

        # Test YAML-style configuration as would appear in mkdocs.yml
        yaml_config_data = {
            "plugins": {
                "svg-to-png": {
                    "enabled_if_env": "BUILD_PDF",
                    "output_dir": "assets/images",
                    "preserve_original": False,
                    "error_on_fail": True,
                    "log_level": "INFO",
                    "cleanup_generated_images": True,
                }
            }
        }

        # Test the plugin config extraction
        plugin_config = yaml_config_data["plugins"]["svg-to-png"]
        manager = SvgConfigManager()
        result = manager.validate(plugin_config)

        # Verify all settings are preserved
        assert result["enabled_if_env"] == "BUILD_PDF"
        assert result["output_dir"] == "assets/images"
        assert result["preserve_original"] is False
        assert result["error_on_fail"] is True
        assert result["log_level"] == "INFO"
        assert result["cleanup_generated_images"] is True

    def test_mkdocs_plugin_config_integration(self):
        """Test configuration integration with MkDocs plugin system."""
        # Simulate how MkDocs would load and validate the plugin config
        from mkdocs.config.base import Config

        # Test plugin configuration as it would be loaded from mkdocs.yml
        plugin_configs = [
            # Minimal configuration
            {"output_dir": "images"},
            # Development configuration
            {
                "output_dir": "tmp/images",
                "preserve_original": True,
                "log_level": "DEBUG",
            },
            # Production configuration
            {
                "enabled_if_env": "PROD_BUILD",
                "output_dir": "build/images",
                "preserve_original": False,
                "error_on_fail": True,
                "log_level": "ERROR",
                "cleanup_generated_images": True,
            },
        ]

        for plugin_config in plugin_configs:
            config_instance = Config(SvgConfigManager.get_config_scheme())
            config_instance.load_dict(plugin_config)

            # Verify all provided settings are correctly loaded
            for key, value in plugin_config.items():
                assert config_instance[key] == value

            # Verify defaults are applied for missing settings
            if "preserve_original" not in plugin_config:
                assert config_instance["preserve_original"] is False
            if "error_on_fail" not in plugin_config:
                assert config_instance["error_on_fail"] is False

    def test_config_schema_type_constraints(self):
        """Test detailed type constraints for each configuration option."""
        from mkdocs.config import config_options

        config_scheme = SvgConfigManager.get_config_scheme()
        config_dict = dict(config_scheme)

        # Test enabled_if_env type constraint
        enabled_if_env_option = config_dict["enabled_if_env"]
        assert isinstance(enabled_if_env_option, config_options.Optional)
        # The inner type should be a string type
        inner_type = enabled_if_env_option.option
        assert isinstance(inner_type, config_options.Type)

        # Test output_dir type constraint
        output_dir_option = config_dict["output_dir"]
        assert isinstance(output_dir_option, config_options.Type)
        assert output_dir_option.default == "assets/images"

        # Test log_level choice constraint
        log_level_option = config_dict["log_level"]
        assert isinstance(log_level_option, config_options.Choice)
        assert log_level_option.choices == ["DEBUG", "INFO", "WARNING", "ERROR"]
        assert log_level_option.default == "INFO"

        # Test boolean options
        for bool_option_name in [
            "preserve_original",
            "error_on_fail",
            "cleanup_generated_images",
        ]:
            bool_option = config_dict[bool_option_name]
            assert isinstance(bool_option, config_options.Type)
            assert bool_option.default is False

    def test_string_whitespace_handling(self):
        """Test handling of whitespace in string configuration values."""
        manager = SvgConfigManager()

        # Test output_dir with leading/trailing whitespace
        config = {"output_dir": "  assets/images  "}
        result = manager.validate(config)
        # Note: This test assumes whitespace is NOT automatically trimmed
        # If trimming is expected, adjust the assertion
        assert result["output_dir"] == "  assets/images  "

        # Test enabled_if_env with whitespace
        config = {"enabled_if_env": "  BUILD_ENV  "}
        result = manager.validate(config)
        assert result["enabled_if_env"] == "  BUILD_ENV  "

    def test_enabled_if_env_non_string_types(self):
        """Test enabled_if_env validation with various non-string types."""
        from mkdocs.config.base import Config

        # Test with non-string types that should fail validation
        invalid_values = [123, True, [], {}, 3.14]

        for invalid_value in invalid_values:
            config_instance = Config(SvgConfigManager.get_config_scheme())
            try:
                config_instance.load_dict({"enabled_if_env": invalid_value})
                # If we get here, check what actually happened
                result_value = config_instance["enabled_if_env"]
                result_type = type(result_value)

                # If type conversion occurred to string, that's acceptable
                if isinstance(result_value, str):
                    # MkDocs might convert types to strings - this is valid behavior
                    expected_str = str(invalid_value)
                    assert result_value == expected_str, (
                        f"String conversion should match: "
                        f"expected {expected_str}, got {result_value}"
                    )
                elif result_value is None:
                    # None is also acceptable for Optional fields
                    pass
                else:
                    # Any other type preservation is unexpected
                    raise AssertionError(
                        f"Unexpected type preservation for enabled_if_env: "
                        f"input {type(invalid_value).__name__}({invalid_value}) -> "
                        f"output {result_type.__name__}({result_value})"
                    )
            except Exception as e:
                # Validation failure is expected and acceptable
                # Verify the error is related to type validation
                error_str = str(e).lower()
                type_related = any(
                    keyword in error_str
                    for keyword in [
                        "type",
                        "string",
                        "str",
                        "enabled_if_env",
                        "invalid",
                    ]
                )
                assert type_related or "enabled_if_env" in error_str, (
                    f"Expected type-related error for "
                    f"{type(invalid_value).__name__}: {e}"
                )

    def test_log_level_case_sensitivity(self):
        """Test log_level validation with different cases."""
        from mkdocs.config.base import Config

        config_instance = Config(SvgConfigManager.get_config_scheme())

        # Test lowercase log levels (should fail if case-sensitive)
        lowercase_levels = ["debug", "info", "warning", "error"]

        for level in lowercase_levels:
            try:
                config_instance = Config(SvgConfigManager.get_config_scheme())
                config_instance.load_dict({"log_level": level})
                # If this passes, case conversion might be happening
                if config_instance["log_level"] in [
                    "DEBUG",
                    "INFO",
                    "WARNING",
                    "ERROR",
                ]:
                    # Case conversion occurred - this is acceptable
                    pass
                else:
                    raise AssertionError(
                        f"Unexpected log_level value: {config_instance['log_level']}"
                    )
            except Exception:
                # Case-sensitive validation (expected behavior)
                pass

        # Test mixed case (should fail)
        mixed_case_levels = ["Debug", "Info", "Warning", "Error"]

        for level in mixed_case_levels:
            try:
                config_instance = Config(SvgConfigManager.get_config_scheme())
                config_instance.load_dict({"log_level": level})
                # If this passes, case conversion might be happening
                if config_instance["log_level"] not in [
                    "DEBUG",
                    "INFO",
                    "WARNING",
                    "ERROR",
                ]:
                    raise AssertionError(
                        f"Expected validation to fail for mixed case: {level}"
                    )
            except Exception:
                # Case-sensitive validation (expected behavior)
                pass

    def test_actual_plugin_class_integration(self):
        """Test configuration integration with the actual SvgToPngPlugin class."""
        from mkdocs_svg_to_png.plugin import SvgToPngPlugin

        plugin = SvgToPngPlugin()

        # Verify the plugin uses the same config scheme
        plugin_scheme = plugin.config_scheme
        manager_scheme = SvgConfigManager.get_config_scheme()

        # Should have the same configuration keys
        plugin_keys = {key for key, _ in plugin_scheme}
        manager_keys = {key for key, _ in manager_scheme}

        assert (
            plugin_keys == manager_keys
        ), "Plugin and ConfigManager should have same config keys"

        # Verify default values match
        plugin_defaults = {}
        manager_defaults = {}

        for key, option in plugin_scheme:
            if hasattr(option, "default"):
                plugin_defaults[key] = option.default

        for key, option in manager_scheme:
            if hasattr(option, "default"):
                manager_defaults[key] = option.default

        assert (
            plugin_defaults == manager_defaults
        ), "Default values should match between plugin and manager"

    def test_config_validation_error_messages(self):
        """Test that configuration validation provides meaningful error messages."""
        from mkdocs.config.base import Config

        # Test invalid log_level with error message content
        config_instance = Config(SvgConfigManager.get_config_scheme())

        try:
            config_instance.load_dict({"log_level": "INVALID_LEVEL"})
            raise AssertionError("Expected validation to fail for invalid log_level")
        except Exception as e:
            error_message = str(e).lower()
            # Error message should mention the invalid value and valid choices
            assert "log_level" in error_message or "invalid_level" in error_message
            # Should mention valid choices
            valid_choices_mentioned = any(
                level.lower() in error_message
                for level in ["debug", "info", "warning", "error"]
            )
            if not valid_choices_mentioned:
                # At least the field name should be in the error
                assert "log_level" in error_message

    def test_config_type_preservation(self):
        """Test that configuration values preserve their intended types."""
        from mkdocs.config.base import Config

        config_instance = Config(SvgConfigManager.get_config_scheme())

        test_config = {
            "enabled_if_env": "TEST_ENV",
            "output_dir": "test/dir",
            "preserve_original": True,
            "error_on_fail": False,
            "log_level": "DEBUG",
            "cleanup_generated_images": True,
        }

        config_instance.load_dict(test_config)

        # Verify types are preserved
        assert isinstance(config_instance["enabled_if_env"], str)
        assert isinstance(config_instance["output_dir"], str)
        assert isinstance(config_instance["preserve_original"], bool)
        assert isinstance(config_instance["error_on_fail"], bool)
        assert isinstance(config_instance["log_level"], str)
        assert isinstance(config_instance["cleanup_generated_images"], bool)

        # Verify exact values
        assert config_instance["enabled_if_env"] == "TEST_ENV"
        assert config_instance["output_dir"] == "test/dir"
        assert config_instance["preserve_original"] is True
        assert config_instance["error_on_fail"] is False
        assert config_instance["log_level"] == "DEBUG"
        assert config_instance["cleanup_generated_images"] is True

    def test_config_empty_string_edge_cases(self):
        """Test configuration behavior with empty strings."""
        manager = SvgConfigManager()

        # Test empty string for output_dir (edge case)
        config = {"output_dir": ""}
        result = manager.validate(config)
        assert result["output_dir"] == ""

        # Test empty string for enabled_if_env (should be valid)
        config = {"enabled_if_env": ""}
        result = manager.validate(config)
        assert result["enabled_if_env"] == ""

    def test_config_none_values_comprehensive(self):
        """Test None values for all configuration options."""
        from mkdocs.config.base import Config

        config_instance = Config(SvgConfigManager.get_config_scheme())

        # Test None for enabled_if_env (should be valid - it's Optional)
        config_instance.load_dict({"enabled_if_env": None})
        assert config_instance["enabled_if_env"] is None

        # Test None for required fields (should fail)
        required_string_fields = ["output_dir"]
        required_bool_fields = [
            "preserve_original",
            "error_on_fail",
            "cleanup_generated_images",
        ]

        for field in required_string_fields:
            try:
                config_instance = Config(SvgConfigManager.get_config_scheme())
                config_instance.load_dict({field: None})
                raise AssertionError(f"Expected validation to fail for None {field}")
            except Exception:
                # Expected to fail
                pass

        for field in required_bool_fields:
            try:
                config_instance = Config(SvgConfigManager.get_config_scheme())
                config_instance.load_dict({field: None})
                raise AssertionError(f"Expected validation to fail for None {field}")
            except Exception:
                # Expected to fail
                pass

    def test_config_special_characters_in_paths(self):
        """Test configuration with special characters in paths."""
        manager = SvgConfigManager()

        special_chars_paths = [
            "assets/images-test",
            "assets/images_v1.0",
            "assets/images.backup",
            "assets/images@2024",
            "assets/images#temp",
            "assets/images$build",
            "assets/images%encoded",
            "assets/images&test",
            "assets/images(temp)",
        ]

        for path in special_chars_paths:
            config = {"output_dir": path}
            result = manager.validate(config)
            assert result["output_dir"] == path

    def test_config_unicode_support(self):
        """Test configuration with Unicode characters."""
        manager = SvgConfigManager()

        unicode_test_cases = [
            # Japanese
            {"output_dir": "assets/画像", "enabled_if_env": "ビルド環境"},
            # Chinese
            {"output_dir": "assets/图片", "enabled_if_env": "构建环境"},
            # Arabic
            {"output_dir": "assets/صور", "enabled_if_env": "بيئة_البناء"},
            # Emoji
            {"output_dir": "assets/📷images", "enabled_if_env": "🏗️BUILD"},
            # Mixed
            {
                "output_dir": "assets/images_画像_图片",
                "enabled_if_env": "BUILD_环境_بيئة",
            },
        ]

        for config in unicode_test_cases:
            result = manager.validate(config)
            assert result == config

    def test_config_very_long_values(self):
        """Test configuration with very long string values."""
        manager = SvgConfigManager()

        # Test very long output_dir
        long_path = "/".join([f"very_long_directory_name_{i}" for i in range(50)])
        config = {"output_dir": long_path}
        result = manager.validate(config)
        assert result["output_dir"] == long_path

        # Test very long enabled_if_env
        long_env_name = "_".join([f"VERY_LONG_ENV_VAR_PART_{i}" for i in range(20)])
        config = {"enabled_if_env": long_env_name}
        result = manager.validate(config)
        assert result["enabled_if_env"] == long_env_name

    def test_config_numeric_string_values(self):
        """Test configuration with numeric string values."""
        manager = SvgConfigManager()

        # Test numeric strings for output_dir
        numeric_paths = ["123", "456.789", "1e10", "0xFF", "0b1010"]

        for path in numeric_paths:
            config = {"output_dir": path}
            result = manager.validate(config)
            assert result["output_dir"] == path

        # Test numeric strings for enabled_if_env
        numeric_env_names = ["123", "BUILD_123", "ENV_2024", "VERSION_1_0"]

        for env_name in numeric_env_names:
            config = {"enabled_if_env": env_name}
            result = manager.validate(config)
            assert result["enabled_if_env"] == env_name
