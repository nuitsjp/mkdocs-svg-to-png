from typing import Any

from mkdocs.config import config_options

from .exceptions import SvgConfigError


class SvgConfigManager:
    """Configuration manager for SVG to PNG conversion plugin."""

    @staticmethod
    def get_config_scheme() -> tuple[tuple[str, Any], ...]:
        """Get SVG-specific configuration scheme."""
        return (
            (
                "enabled",
                config_options.Type(bool, default=True),
            ),
            (
                "enabled_if_env",
                config_options.Optional(config_options.Type(str)),
            ),
            (
                "output_dir",
                config_options.Type(str, default="assets/images"),
            ),
            (
                "dpi",
                config_options.Type(int, default=300),
            ),
            (
                "output_format",
                config_options.Choice(["png"], default="png"),
            ),
            (
                "quality",
                config_options.Type(int, default=95),
            ),
            (
                "background_color",
                config_options.Type(str, default="transparent"),
            ),
            (
                "cache_enabled",
                config_options.Type(bool, default=True),
            ),
            (
                "cache_dir",
                config_options.Type(str, default=".svg_cache"),
            ),
            (
                "preserve_original",
                config_options.Type(bool, default=False),
            ),
            (
                "error_on_fail",
                config_options.Type(bool, default=False),
            ),
            (
                "log_level",
                config_options.Choice(
                    ["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO"
                ),
            ),
            (
                "cleanup_generated_images",
                config_options.Type(bool, default=False),
            ),
            (
                "temp_dir",
                config_options.Optional(config_options.Type(str)),
            ),
        )

    def validate(self, config: dict[str, Any]) -> dict[str, Any]:
        """Validate SVG conversion configuration."""
        # Required parameters check
        required_keys = ["dpi", "output_format", "quality"]
        for key in required_keys:
            if key not in config:
                raise SvgConfigError(
                    f"Required configuration key '{key}' is missing",
                    config_key=key,
                    suggestion=f"Add '{key}' to your plugin configuration",
                )

        # DPI validation
        if config["dpi"] <= 0:
            raise SvgConfigError(
                "DPI must be a positive integer",
                config_key="dpi",
                config_value=config["dpi"],
                suggestion="Set DPI to a positive integer value (e.g., dpi: 300)",
            )

        # Quality validation
        if not (0 <= config["quality"] <= 100):
            raise SvgConfigError(
                "Quality must be between 0 and 100",
                config_key="quality",
                config_value=config["quality"],
                suggestion="Set quality between 0 and 100 (e.g., quality: 95)",
            )

        # Output format validation
        if config["output_format"] not in ["png"]:
            raise SvgConfigError(
                "Unsupported output format",
                config_key="output_format",
                config_value=config["output_format"],
                suggestion="Currently only 'png' output format is supported",
            )

        return config
