from pathlib import Path
from typing import Any

from mkdocs.config import config_options

from .exceptions import (
    MermaidConfigError,
    MermaidFileError,
    SvgConfigError,
)


class ConfigManager:
    @staticmethod
    def get_config_scheme() -> tuple[tuple[str, Any], ...]:
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
                "image_format",
                config_options.Choice(["png", "svg"], default="svg"),
            ),
            (
                "mermaid_config",
                config_options.Optional(config_options.Type(str)),
            ),
            (
                "mmdc_path",
                config_options.Type(str, default="mmdc"),
            ),
            (
                "theme",
                config_options.Choice(
                    ["default", "dark", "forest", "neutral"], default="default"
                ),
            ),
            ("background_color", config_options.Type(str, default="white")),
            ("width", config_options.Type(int, default=800)),
            ("height", config_options.Type(int, default=600)),
            (
                "scale",
                config_options.Type(float, default=1.0),
            ),
            (
                "css_file",
                config_options.Optional(config_options.Type(str)),
            ),
            (
                "puppeteer_config",
                config_options.Optional(config_options.Type(str)),
            ),
            (
                "temp_dir",
                config_options.Optional(config_options.Type(str)),
            ),
            (
                "cache_enabled",
                config_options.Type(bool, default=True),
            ),
            (
                "cache_dir",
                config_options.Type(str, default=".mermaid_cache"),
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

    @staticmethod
    def validate_config(config: dict[str, Any]) -> bool:
        # 必須パラメータの存在チェック
        required_keys = ["width", "height", "scale"]
        for key in required_keys:
            if key not in config:
                raise MermaidConfigError(
                    f"Required configuration key '{key}' is missing",
                    config_key=key,
                    suggestion=f"Add '{key}' to your plugin configuration",
                )

        if config["width"] <= 0 or config["height"] <= 0:
            raise MermaidConfigError(
                "Width and height must be positive integers",
                config_key="width/height",
                config_value=f"width={config['width']}, height={config['height']}",
                suggestion="Set width and height to positive integer values "
                "(e.g., width: 800, height: 600)",
            )

        if config["scale"] <= 0:
            raise MermaidConfigError(
                "Scale must be a positive number",
                config_key="scale",
                config_value=config["scale"],
                suggestion="Set scale to a positive number (e.g., scale: 1.0)",
            )

        # オプションパラメータのチェック（存在する場合のみ）
        if (
            "css_file" in config
            and config["css_file"]
            and not Path(config["css_file"]).exists()
        ):
            raise MermaidFileError(
                f"CSS file not found: {config['css_file']}",
                file_path=config["css_file"],
                operation="read",
                suggestion="Ensure the CSS file exists or remove the "
                "css_file configuration",
            )

        if (
            "puppeteer_config" in config
            and config["puppeteer_config"]
            and not Path(config["puppeteer_config"]).exists()
        ):
            raise MermaidFileError(
                f"Puppeteer config file not found: {config['puppeteer_config']}",
                file_path=config["puppeteer_config"],
                operation="read",
                suggestion="Ensure the Puppeteer config file exists or "
                "remove the puppeteer_config configuration",
            )

        return True


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

    @staticmethod
    def validate_config(config: dict[str, Any]) -> bool:
        """Validate SVG conversion configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            True if configuration is valid

        Raises:
            SvgConfigError: If configuration is invalid
        """
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

        return True
