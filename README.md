# mkdocs-svg-to-png

[![PyPI - Python Version][python-image]][pypi-link]

An MkDocs plugin that converts SVG code blocks and local SVG files to PNG with
Playwright. It is designed to prevent background colors or theme fills from
dropping when generating PDFs (notably with `mkdocs-to-pdf` and draw.io SVGs) by
embedding PNGs instead of raw SVG.

- [Documentation](https://mango-dune-02db2c010.3.azurestaticapps.net/)
- [DeepWiki](https://deepwiki.com/nuitsjp/mkdocs-svg-to-png)

## Background and Purpose

- `mkdocs-to-pdf` can emit PDFs where SVG backgrounds and fills are lost,
  especially for draw.io exports, making diagrams hard to read.
- Applying the theme directly to SVG during PDF creation is difficult; converting
  SVG to PNG preserves backgrounds and fill colors before PDF embedding.
- Everything runs locally, keeping sensitive diagrams off external services.

## Features

- Converts Markdown ```svg code blocks and local `*.svg` file references to PNG
- Playwright-based rendering to capture backgrounds and fills faithfully
- Conditional activation via `enabled_if_env`; automatically skipped on
  `mkdocs serve` for fast previews
- Optional `preserve_original` to keep the original SVG alongside the PNG
- Optional cleanup of generated PNGs after a build for clean CI workspaces

## Requirements

- Python 3.9+
- MkDocs 1.4.0+, MkDocs Material 8.0.0+
- Playwright 1.40.0+ (browser binaries must be installed)

## Installation

With pip:

```bash
pip install mkdocs-svg-to-png
python -m playwright install
```

With uv (recommended for development):

```bash
uv add mkdocs-svg-to-png
uv run python -m playwright install
```

Run `python -m playwright install` to download the browsers Playwright uses;
without it, conversion will fail.

## Quick Start

Add the plugin to `mkdocs.yml`. `enabled_if_env` is the environment variable name
that controls activation.

```yaml
plugins:
  - search
  - svg-to-png:
      enabled_if_env: ENABLE_PDF_EXPORT
```

For a full Mermaid → SVG → PNG → PDF pipeline:

```yaml
plugins:
  - search
  - mermaid-to-svg:
      enabled_if_env: ENABLE_PDF_EXPORT
  - svg-to-png:
      enabled_if_env: ENABLE_PDF_EXPORT
  - to-pdf:
      enabled_if_env: ENABLE_PDF_EXPORT
```

## ENABLE_PDF_EXPORT and Workflow

PNG conversion and PDF generation are heavy (Playwright launches a browser), so
they are typically disabled while writing and enabled only in CI.

- Writing phase: `mkdocs serve` automatically skips this plugin, keeping preview
  fast.
- Local HTML build: `mkdocs build` (no env var) produces a normal static site
  without PNG/PDF generation.
- PDF/PNG build: run `ENABLE_PDF_EXPORT=1 mkdocs build` or
  `ENABLE_PDF_EXPORT=1 make build` in CI to generate PNGs and PDFs.

This keeps authoring lightweight while CI produces the full artifacts.

## Usage

### Inline SVG

````markdown
```svg
<svg width="120" height="120">
  <rect x="10" y="10" width="100" height="100"
        stroke="black" stroke-width="3" fill="white" />
</svg>
```
````

The block is converted to PNG and replaced with an `<img>` reference.

### SVG File References

Local references (non-HTTP) are also converted:

```markdown
![Sequence](diagrams/sequence.svg)
```

Generated PNGs are placed under `docs/assets/images/` (the default `output_dir`)
and bundled into the site.

## Configuration

| Option | Default | Description |
| --- | --- | --- |
| `enabled_if_env` | `null` | Enable only when the specified environment variable is set and non-empty; if `null`, always enabled. |
| `output_dir` | `assets/images` | Where generated PNGs are saved, relative to `docs/`. |
| `preserve_original` | `false` | Keep the original SVG beneath the PNG; useful for comparing theme/render differences. |
| `error_on_fail` | `false` | Stop the build on conversion errors when `true`; otherwise log and continue. |
| `log_level` | `INFO` | Plugin log level; if the root logger requests DEBUG, DEBUG is used automatically. |
| `cleanup_generated_images` | `false` | Remove generated PNGs after the build (handy for CI cleanup). |

## PDF Tips

1. Use `mkdocs-mermaid-to-svg` to produce SVG from Mermaid.
2. Convert SVG to PNG with this plugin to lock in backgrounds and fills.
3. Generate the final PDF with `mkdocs-to-pdf`; draw.io diagrams remain intact.

## Troubleshooting

- Playwright not found: run `python -m playwright install`.
- Permission errors: ensure `output_dir` is writable and disk space is available.
- Need side-by-side comparison: set `preserve_original: true` and
  `log_level: DEBUG`.
- Detect failures in CI: set `error_on_fail: true` to fail the build on errors.

## Development and Maintenance

- Setup: `make install-dev`
- Tests: `make test` (with coverage: `make test-cov`)
- Static checks: `make format` / `make lint` / `make typecheck`
- Docs build: `make build` (with PDF: `ENABLE_PDF_EXPORT=1 make build-pdf`)

## License and Related Projects

- License: MIT
- Related: [mkdocs-mermaid-to-svg](https://github.com/nuitsjp/mkdocs-mermaid-to-svg) /
  [mkdocs-to-pdf](https://github.com/orzih/mkdocs-to-pdf)

[pypi-link]: https://pypi.org/project/mkdocs-svg-to-png/
[python-image]: https://img.shields.io/pypi/pyversions/mkdocs-svg-to-png?logo=python&logoColor=aaaaaa&labelColor=333333
