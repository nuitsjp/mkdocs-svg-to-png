# mkdocs-svg-to-png

[![PyPI - Python Version][python-image]][pypi-link]

An MkDocs plugin to convert SVG files to PNG images using Playwright.

This plugin finds SVG code blocks and image references and converts them to PNG images during the MkDocs build process. This is useful for formats that don't support SVG directly, like PDF, or for ensuring consistent image rendering across different environments.

- [Documents](https://thankful-beach-0f331f600.1.azurestaticapps.net/)

## Requirements

This plugin requires Python 3.9+ and automatically installs the following dependencies:

- **Playwright** (for SVG to PNG conversion)
- **Pillow** (for image processing)
- **NumPy** (for image data manipulation)
- **defusedxml** (for secure XML parsing)

## Setup

Install the plugin using pip:

```bash
pip install mkdocs-svg-to-png
```

If you're using **uv** (recommended for development):

```bash
uv add mkdocs-svg-to-png
```

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
      output_dir: "assets/images"
      image_format: "png"
      width: 1200
      height: 800
      scale: 2.0
      background_color: "transparent"
      cache_enabled: true
      preserve_original: false
      error_on_fail: false
      verbose: false
      cleanup_generated_images: false
      enabled_if_env: null
      temp_dir: null
```

### Configuration Parameters

-   **`output_dir`** (default: `"assets/images"`)
    -   Directory where generated PNG images will be saved, relative to your `docs` directory

-   **`image_format`** (default: `"png"`)
    -   Output format for generated images. Currently supports `png`

-   **`width`** (default: `1200`)
    -   Width of the generated PNG images in pixels

-   **`height`** (default: `800`)
    -   Height of the generated PNG images in pixels

-   **`scale`** (default: `2.0`)
    -   Scale factor for high-resolution output (e.g., 2.0 for 2x resolution)

-   **`background_color`** (default: `"transparent"`)
    -   Background color for generated images. Can be `"transparent"`, color names (e.g., `"white"`), or hex codes (e.g., `"#FFFFFF"`)

-   **`cache_enabled`** (default: `true`)
    -   Enable caching to avoid re-rendering unchanged SVG content

-   **`preserve_original`** (default: `false`)
    -   If `true`, keeps the original SVG code block alongside the generated PNG image

-   **`error_on_fail`** (default: `false`)
    -   If `true`, stops the build when SVG conversion fails. If `false`, logs errors and continues

-   **`verbose`** (default: `false`)
    -   Enable detailed logging for debugging

-   **`cleanup_generated_images`** (default: `false`)
    -   If `true`, removes generated PNG images after the build completes (useful for CI/CD)

-   **`enabled_if_env`** (default: `null`)
    -   Environment variable name to conditionally enable the plugin. Only activates if the variable is set and non-empty

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
