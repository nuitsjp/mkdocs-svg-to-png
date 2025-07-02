# mkdocs-svg-to-png

[![PyPI - Python Version][python-image]][pypi-link]

An MkDocs plugin to convert SVG files to PNG images.

This plugin finds SVG code blocks and image references and converts them to PNG images during the MkDocs build process. This is useful for formats that don't support SVG directly, like PDF, or for ensuring consistent image rendering across different environments.

- [Documents](https://thankful-beach-0f331f600.1.azurestaticapps.net/)

## Requirements

This plugin requires `CairoSVG` and its dependencies. Please ensure you have them installed:

```bash
pip install cairosvg
```

CairoSVG itself has some system-level dependencies (like `cairo`, `pango`, `gdk-pixbuf`). On Debian/Ubuntu, you can install them using:

```bash
sudo apt-get update
sudo apt-get install libcairo2-dev libffi-dev libgdk-pixbuf2.0-dev libpango1.0-dev
```

For other operating systems, please refer to the [CairoSVG documentation](https://cairosvg.org/documentation/#installation).

## Setup

Install the plugin using pip:

```bash
pip install mkdocs-svg-to-png
```

Activate the plugin in `mkdocs.yml`:

```yaml
plugins:
  - search
  - svg-to-png
```

> **Note:** If you have no `plugins` entry in your config file yet, you'll likely also want to add the `search` plugin. MkDocs enables it by default if there is no `plugins` entry set, but now you have to enable it explicitly.

## Options

You can customize the plugin's behavior in `mkdocs.yml`:

```yaml
plugins:
  - svg-to-png:
      output_dir: "assets/images"
      image_format: "png"
      dpi: 300
      quality: 95
      background_color: "transparent"
      cache_enabled: true
      cache_dir: ".svg_cache"
      preserve_original: false
      error_on_fail: false
      log_level: "INFO"
      cleanup_generated_images: false
      enabled_if_env: null
      temp_dir: null
```

-   `output_dir`:
    -   Defaults to `assets/images`.
    -   The directory where generated PNG images will be saved, relative to your `docs` directory.
-   `image_format`:
    -   Defaults to `png`.
    -   The output format for the generated images. Currently, only `png` is supported.
-   `dpi`:
    -   Defaults to `300`.
    -   The Dots Per Inch (DPI) for rendering SVG to PNG. Higher values result in larger, higher-resolution images.
-   `quality`:
    -   Defaults to `95`.
    -   The quality of the output PNG image, a value between 0 (lowest) and 100 (highest). Only applicable for PNG output.
-   `background_color`:
    -   Defaults to `transparent`.
    -   The background color for the generated PNG images. Can be a color name (e.g., `white`), a hex code (e.g., `#FFFFFF`), or `transparent`.
-   `cache_enabled`:
    -   Defaults to `true`.
    -   If `true`, generated images will be cached to avoid re-rendering on subsequent builds if the SVG content hasn't changed.
-   `cache_dir`:
    -   Defaults to `.svg_cache`.
    -   The directory where cached images are stored, relative to the project root.
-   `preserve_original`:
    -   Defaults to `false`.
    -   If `true`, the original SVG code block or image reference will be preserved in the Markdown output, in addition to the generated PNG image.
-   `error_on_fail`:
    -   Defaults to `false`.
    -   If `true`, the MkDocs build will fail if any SVG to PNG conversion encounters an error. If `false`, errors will be logged, and the original SVG content will be kept.
-   `log_level`:
    -   Defaults to `INFO`.
    -   Sets the logging level for the plugin. Can be `DEBUG`, `INFO`, `WARNING`, or `ERROR`.
-   `cleanup_generated_images`:
    -   Defaults to `false`.
    -   If `true`, generated PNG images will be removed from the `output_dir` after the MkDocs build is complete. This is useful for CI/CD pipelines.
-   `enabled_if_env`:
    -   Defaults to `null`.
    -   If set to an environment variable name, the plugin will only be enabled if that environment variable is set to a non-empty value. Useful for conditional builds (e.g., only enable for PDF builds).
-   `temp_dir`:
    -   Defaults to `null`.
    -   Specifies a directory for temporary files created during the conversion process. If `null`, the system's default temporary directory will be used.

[pypi-link]: https://pypi.org/project/mkdocs-svg-to-png/
[python-image]: https://img.shields.io/pypi/pyversions/mkdocs-svg-to-png?logo=python&logoColor=aaaaaa&labelColor=333333
