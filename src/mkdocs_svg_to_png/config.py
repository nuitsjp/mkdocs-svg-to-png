from typing import Any

from mkdocs.config import config_options


class SvgConfigManager:
    """Configuration manager for SVG to PNG conversion plugin."""

    @staticmethod
    def get_config_scheme() -> tuple[tuple[str, Any], ...]:
        """Get SVG-specific configuration scheme."""
        return (
            (
                "enabled_if_env",
                config_options.Optional(config_options.Type(str)),
            ),
            (
                "output_dir",
                config_options.Type(str, default="assets/images"),
            ),
            (
                "cache_enabled",
                config_options.Type(bool, default=True),
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
        )

    def validate(self, config: dict[str, Any]) -> dict[str, Any]:
        """Validate SVG conversion configuration."""
        # No required parameters - all settings have defaults or are optional
        return config
