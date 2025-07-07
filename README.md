# mkdocs-svg-to-png

[![PyPI - Python Version][python-image]][pypi-link]

An MkDocs plugin to convert SVG files to PNG images using Playwright.

This plugin finds SVG code blocks and image references and converts them to PNG images during the MkDocs build process. While PDF formats do support SVG, some SVG content may not render correctly when using [mkdocs-to-pdf](https://github.com/domWalters/mkdocs-to-pdf) for PDF generation. This plugin ensures consistent, high-quality rendering by converting SVG to PNG images before PDF creation.

**Primary use case**: Works seamlessly with [mkdocs-mermaid-to-image](https://github.com/nuitsjp/mkdocs-mermaid-to-image) to create a complete pipeline for Mermaid diagrams → SVG → PNG → PDF without external services.

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
  - mermaid-to-image:
      enabled_if_env: ENABLE_PDF_EXPORT
  - svg-to-png:
      enabled_if_env: ENABLE_PDF_EXPORT
  - to-pdf:
      enabled_if_env: ENABLE_PDF_EXPORT
```

This creates a complete pipeline:
1. **mermaid-to-image** converts Mermaid diagrams to SVG
2. **svg-to-png** converts SVG to high-quality PNG images
3. **to-pdf** generates PDF with properly rendered diagrams

## Development Workflow

For optimal development experience, use `enabled_if_env` to conditionally enable plugins:

```bash
# Development: Fast preview without image conversion
mkdocs serve

# Production: Build with image conversion and PDF generation
ENABLE_PDF_EXPORT=1 mkdocs build
```

This approach ensures fast iteration during development while maintaining high-quality output for production builds.

## Configuration Options

You can customize the plugin's behavior in `mkdocs.yml`:

```yaml
plugins:
  - svg-to-png:
      enabled_if_env: null
      output_dir: "assets/images"
      dpi: 300
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

-   **`enabled_if_env`** (default: `null`)
    -   Environment variable name to conditionally enable the plugin. Only activates if the variable is set and non-empty. If not set, the plugin is enabled by default

-   **`output_dir`** (default: `"assets/images"`)
    -   Directory where generated PNG images will be saved, relative to your `docs` directory. All images are generated in PNG format

-   **`dpi`** (default: `300`)
    -   Resolution in dots per inch for generated PNG images

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

See [Development Guide](docs/development.md) for detailed development instructions.

[pypi-link]: https://pypi.org/project/mkdocs-svg-to-png/
[python-image]: https://img.shields.io/pypi/pyversions/mkdocs-svg-to-png?logo=python&logoColor=aaaaaa&labelColor=333333
