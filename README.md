# MkDocs SVG to PNG Plugin

SVG コードブロックや SVG ファイルを、MkDocs のビルド時に PNG 画像へ自動変換するプラグインです。PDF 出力やオフライン閲覧に最適化され、キャッシュや環境変数による条件付き有効化など柔軟な運用が可能です。
## 主な特徴

- Markdown 内の `svg` コードブロックや SVG ファイル参照を PNG 画像へ自動変換
- 変換画像は `output_dir`（デフォルト: `assets/images`）に保存
- 環境変数による条件付き有効化（例: PDF ビルド時のみ変換）
- キャッシュ機能・エラー時の挙動制御・ログレベル指定

---

## インストール
```bash
pip install mkdocs-svg-to-png
```

---

## プラグイン設定例（mkdocs.yml）
```yaml
plugins:
  - search
  - svg-to-png:
      enabled: true                # デフォルト: true
      enabled_if_env: ENABLE_PDF_EXPORT  # 環境変数で有効化制御（例: PDF出力時のみ）
      output_dir: assets/images    # 生成画像の保存先
      image_format: png            # 現在は png のみサポート
      dpi: 300                     # 画像DPI
      quality: 95                  # PNG品質（0-100）
      background_color: transparent # 背景色
      cache_enabled: true          # キャッシュ有効
      preserve_original: false     # 元SVGを残すか
      error_on_fail: false         # 失敗時にビルド停止するか
      log_level: INFO              # ログレベル
      cleanup_generated_images: false # 生成画像のクリーンアップ
      temp_dir: null               # 一時ディレクトリ
```

### 主要設定項目

| オプション                | 説明                                      | デフォルト         |
|--------------------------|-------------------------------------------|-------------------|
| enabled                  | プラグイン有効/無効                       | true              |
| enabled_if_env           | 環境変数で有効化制御                      | なし              |
| output_dir               | 生成画像の保存ディレクトリ                 | assets/images     |
| image_format             | 出力形式（png のみ）                      | png               |
| dpi                      | 画像DPI                                   | 300               |
| quality                  | PNG品質（0-100）                          | 95                |
| background_color         | 背景色                                    | transparent       |
| cache_enabled            | キャッシュ有効/無効                       | true              |
| preserve_original        | 元SVGを残すか                             | false             |
| error_on_fail            | 失敗時にビルド停止                        | false             |
| log_level                | ログレベル（DEBUG/INFO/WARNING/ERROR）     | INFO              |
| cleanup_generated_images | ビルド後に生成画像を削除                   | false             |
| temp_dir                 | 一時ファイル保存先                         | null              |

---

## 使い方

### 通常のHTMLビルド

```bash
mkdocs build    # 画像変換を実行
mkdocs serve    # 開発サーバー（画像変換はスキップ）
```

### PDF出力時のみ画像化したい場合

`enabled_if_env` オプションを利用し、PDF生成時のみ画像変換を有効化できます。

```yaml
plugins:
  - search
  - svg-to-png:
      enabled_if_env: ENABLE_PDF_EXPORT
  - to-pdf:
      enabled_if_env: ENABLE_PDF_EXPORT
      output_path: docs.pdf
```

```bash
# 通常ビルド（SVGのまま）
mkdocs build
# PDF用ビルド（SVG→PNG変換）
ENABLE_PDF_EXPORT=1 mkdocs build
```

#### enabled_if_env の判定仕様

| 環境変数の状態 | プラグイン動作 |
|----------------|---------------|
| 未設定         | 無効化        |
| 空文字列       | 無効化        |
| 0/1/false/true | 有効化        |
| 何らかの値     | 有効化        |

---

## SVG コードブロックの記述例

```markdown
```svg
<svg width="100" height="100">
  <circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" />
</svg>
```

属性付き:

```markdown
```svg {dpi: 150, background_color: "blue"}
<svg width="200" height="200">
  <rect x="10" y="10" width="180" height="180" fill="green" />
</svg>
```

---

## 生成される成果物

- **変換前:** SVG コードブロックまたは SVG ファイル参照
- **変換後:** `<img>` タグ（PNG画像参照）
- **生成画像:** `output_dir` 配下に保存
- **キャッシュ:** 内部キャッシュディレクトリで管理
確認例:

```bash
ls site/assets/images/
# または output_dir を変更した場合
ls site/[your_output_dir]/
```

---

## エラー処理・ログ

- `error_on_fail: true` で変換失敗時にビルド停止
- `log_level` でログ出力レベルを制御
- 環境変数 `MKDOCS_SVG_TO_PNG_LOG_LEVEL` でも上書き可能

---

## 開発・テスト

### テスト実行

```bash
pytest
```

### 主な開発用ディレクトリ

- `src/mkdocs_svg_to_png/` … プラグイン本体
- `tests/` … 単体・統合テスト
- `docs/` … ドキュメント

### コアモジュール構成

- `plugin.py` … MkDocsプラグイン本体
- `config.py` … 設定スキーマ・バリデーション
- `processor.py` … Markdown解析・画像生成オーケストレーション
- `markdown_processor.py` … SVGブロック抽出・置換
- `svg_converter.py` … SVG→PNG変換処理
- `exceptions.py` … 独自例外
- `logging_config.py` … ログ設定
- `utils.py` … ユーティリティ

---

## よくある質問

### Q. SVG以外の画像形式は？
A. 現状PNGのみサポートです。

### Q. Mermaidや他の図式も変換したい
A. Mermaid用には [mkdocs-mermaid-to-svg](https://github.com/nuitsjp/mkdocs-mermaid-to-svg) をご利用ください。

---

## ライセンス

MIT License
# mkdocs-svg-to-png

[![PyPI - Python Version][python-image]][pypi-link]

An MkDocs plugin to convert SVG files to PNG images using Playwright.

This plugin finds SVG code blocks and image references and converts them to PNG images during the MkDocs build process. While PDF formats do support SVG, some SVG content may not render correctly when using [mkdocs-to-pdf](https://github.com/domWalters/mkdocs-to-pdf) for PDF generation. This plugin ensures consistent, high-quality rendering by converting SVG to PNG images before PDF creation.

**Primary use case**: Works seamlessly with [mkdocs-mermaid-to-svg](https://github.com/nuitsjp/mkdocs-mermaid-to-svg) to create a complete pipeline for Mermaid diagrams → SVG → PNG → PDF without external services.

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
  - mermaid-to-svg:
      enabled_if_env: ENABLE_PDF_EXPORT
  - svg-to-png:
      enabled_if_env: ENABLE_PDF_EXPORT
  - to-pdf:
      enabled_if_env: ENABLE_PDF_EXPORT
```

This creates a complete pipeline:
1. **mermaid-to-svg** converts Mermaid diagrams to SVG
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
