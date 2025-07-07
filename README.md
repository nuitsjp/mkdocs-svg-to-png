# mkdocs-svg-to-png

[![PyPI - Python Version][python-image]][pypi-link]

An MkDocs plugin to convert SVG files to PNG images using Playwright.

This plugin finds SVG code blocks and image references and converts them to PNG images during the MkDocs build process. This is useful for formats that don't support SVG directly, like PDF, or for ensuring consistent image rendering across different environments.

- [Documents](https://thankful-beach-0f331f600.1.azurestaticapps.net/)

## Requirements

This plugin requires Python 3.9+ and automatically installs the following dependencies:

- **MkDocs** (>=1.4.0) - Documentation site generator
- **MkDocs Material** (>=8.0.0) - Material theme for MkDocs
- **Playwright** (>=1.40.0) - Browser automation for SVG to PNG conversion

## Setup

Install the plugin using pip:

```bash
pip install mkdocs-svg-to-png
python -m playwright install
```

If you're using **uv** (recommended for development):

```bash
uv add mkdocs-svg-to-png
uv run python -m playwright install
```

> **Note:** The `python -m playwright install` command is required to download the browser binaries that Playwright needs for rendering SVG content. Without this step, the plugin will fail to convert SVG files.

Activate the plugin in `mkdocs.yml`:

```yaml
plugins:
  - search
  - svg-to-png
```

> **Note:** If you have no `plugins` entry in your config file yet, you'll likely also want to add the `search` plugin. MkDocs enables it by default if there is no `plugins` entry set, but now you have to enable it explicitly.

## Configuration Options

You can customize the plugin's behavior in `mkdocs.yml`:

```yaml
plugins:
  - svg-to-png:
      enabled: true
      enabled_if_env: null
      output_dir: "assets/images"
      dpi: 300
      output_format: "png"
      quality: 95
      background_color: "transparent"
      cache_enabled: true
      cache_dir: ".svg_cache"
      preserve_original: false
      error_on_fail: false
      log_level: "INFO"
      cleanup_generated_images: false
      temp_dir: null
```

### Configuration Parameters

-   **`enabled`** (default: `true`)
    -   Enable or disable the plugin

-   **`enabled_if_env`** (default: `null`)
    -   Environment variable name to conditionally enable the plugin. Only activates if the variable is set and non-empty

-   **`output_dir`** (default: `"assets/images"`)
    -   Directory where generated PNG images will be saved, relative to your `docs` directory

-   **`dpi`** (default: `300`)
    -   Resolution in dots per inch for generated PNG images

-   **`output_format`** (default: `"png"`)
    -   Output format for generated images. Currently supports `png`

-   **`quality`** (default: `95`)
    -   Image quality setting (0-100). Higher values produce better quality but larger files

-   **`background_color`** (default: `"transparent"`)
    -   Background color for generated images. Can be `"transparent"`, color names (e.g., `"white"`), or hex codes (e.g., `"#FFFFFF"`)

-   **`cache_enabled`** (default: `true`)
    -   Enable caching to avoid re-rendering unchanged SVG content

-   **`cache_dir`** (default: `".svg_cache"`)
    -   Directory for cache files, relative to your project root

-   **`preserve_original`** (default: `false`)
    -   If `true`, keeps the original SVG code block alongside the generated PNG image

-   **`error_on_fail`** (default: `false`)
    -   If `true`, stops the build when SVG conversion fails. If `false`, logs errors and continues

-   **`log_level`** (default: `"INFO"`)
    -   Logging level for the plugin. Options: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`

-   **`cleanup_generated_images`** (default: `false`)
    -   If `true`, removes generated PNG images after the build completes (useful for CI/CD)

-   **`temp_dir`** (default: `null`)
    -   Custom directory for temporary files. Uses system default if not specified

## Development

### Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) (recommended package manager)

### Development Commands

```bash
# Setup development environment
make setup

# Run tests
make test

# Run tests with coverage
make test-cov

# Code quality checks
make check

# Build documentation
make build

# Serve documentation locally
make serve
```

[pypi-link]: https://pypi.org/project/mkdocs-svg-to-png/
[python-image]: https://img.shields.io/pypi/pyversions/mkdocs-svg-to-png?logo=python&logoColor=aaaaaa&labelColor=333333
