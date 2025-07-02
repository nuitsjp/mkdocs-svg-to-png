# 使用方法

## プラグイン設定

`mkdocs.yml`でプラグインを設定してください：

```yaml
plugins:
  - svg-to-png:
      enabled: true              # デフォルト: true
      enabled_if_env: "ENABLE_PDF_EXPORT"  # 環境変数による制御（オプション）
      output_dir: "assets/images" # デフォルト: "assets/images"
      image_format: "png"        # 現在は "png" のみサポート (デフォルト: "png")
      dpi: 300                   # デフォルト: 300
      quality: 95                # デフォルト: 95
      background_color: "transparent" # デフォルト: "transparent"
      cache_enabled: true        # デフォルト: true
      cache_dir: ".svg_cache"    # デフォルト: ".svg_cache"
      preserve_original: false   # デフォルト: false
      error_on_fail: false       # デフォルト: false
      log_level: "INFO"          # "DEBUG", "INFO", "WARNING", "ERROR"
      cleanup_generated_images: false # デフォルト: false
      temp_dir: null             # デフォルト: null
```

### 主要設定項目

- **enabled**: プラグインの有効/無効
- **enabled_if_env**: 環境変数による条件付き有効化
- **output_dir**: 生成画像の保存ディレクトリ
- **image_format**: 出力形式（現在PNGのみサポート）
- **dpi**: SVGからPNGへの変換時のDPI
- **quality**: PNG画像の品質（0-100）
- **background_color**: 生成画像の背景色
- **cache_enabled**: キャッシュ機能の有効/無効
- **cache_dir**: キャッシュディレクトリ
- **preserve_original**: 元のSVGコード/参照を保持するか
- **error_on_fail**: エラー時にビルドを停止するか
- **log_level**: プラグインのログレベル
- **cleanup_generated_images**: ビルド後に生成画像をクリーンアップするか
- **temp_dir**: 一時ファイルの保存ディレクトリ

## PDF出力との組み合わせ

### 環境変数による条件付き画像化

PDF生成時のみSVGを画像化したい場合は、`enabled_if_env`オプションを使用します：

```yaml
plugins:
  - search
  - svg-to-png:
      enabled_if_env: ENABLE_PDF_EXPORT
      image_format: png
  - to-pdf:
      cover_subtitle: 'Project Documentation'
      output_path: docs.pdf
```

### 使用方法

**通常のHTMLビルド**（SVGは動的レンダリングまたは元のSVGのまま）：
```bash
mkdocs build
mkdocs serve
```

**PDF生成用ビルド**（SVGは静的画像化）：
```bash
ENABLE_PDF_EXPORT=1 mkdocs build
```

### 環境変数の判定仕様

`enabled_if_env`の動作：

| 環境変数の状態 | プラグイン動作 | 備考 |
|---------------|---------------|------|
| 未設定 | 無効化 | プラグイン処理をスキップ |
| `=""` | 無効化 | 空文字列は無効と判定 |
| `=" "` | 無効化 | 空白のみは無効と判定 |
| `="0"` | **有効化** | 値があれば有効化 |
| `="1"` | 有効化 | 推奨値 |
| `="false"` | **有効化** | 文字列値があれば有効化 |

**注意**: 環境変数に何らかの値が設定されていれば（`0`、`false`等でも）プラグインが有効化されます。

### 実用的なワークフロー例

**CI/CDでの自動PDF生成**：
```yaml
# GitHub Actions例
- name: Build documentation
  run: mkdocs build

- name: Generate PDF
  run: ENABLE_PDF_EXPORT=1 mkdocs build

- name: Upload PDF artifact
  uses: actions/upload-artifact@v3
  with:
    name: documentation-pdf
    path: site/*.pdf
```

**開発時の使い分け**：
```bash
# 開発時（高速）
mkdocs serve

# HTMLプレビュー
mkdocs build

# PDF生成確認
ENABLE_PDF_EXPORT=1 mkdocs build
```

## SVGの記述

### 基本的な記述方法

Markdownファイル内でSVGコードブロックを直接記述できます。

````markdown
```svg
<svg width="100" height="100">
  <circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" />
</svg>
```
````



### 属性の指定

SVGコードブロックには、追加の属性を指定できます。これらの属性は、変換時のオプションとして利用されます。

````markdown
```svg {dpi: 150, background_color: "blue"}
<svg width="200" height="200">
  <rect x="10" y="10" width="180" height="180" fill="green" />
</svg>
```
````

## ビルドと実行

### 通常のビルド

```bash
mkdocs build    # 静的サイト生成（画像変換実行）
mkdocs serve    # 開発サーバー（画像変換スキップ）
```

### ログレベル指定

```bash
mkdocs build --verbose  # 詳細ログ
```

環境変数でログレベルを制御することも可能：

```bash
LOG_LEVEL=DEBUG mkdocs build
```

## 生成される成果物

- **変換前**: SVGコードブロックまたはSVGファイル参照
- **変換後**: 画像タグ（`<img>`）
- **生成画像**: 設定した`output_dir`に保存
- **キャッシュ**: 設定した`cache_dir`に保存（再利用）

### 生成画像の確認

```bash
# デフォルト設定の場合
ls site/assets/images/

# カスタム設定の場合
ls site/[your_output_dir]/
```

## パフォーマンス最適化

### キャッシュ活用

- `cache_enabled: true`（推奨）
- 同じSVGの再生成を回避
- ビルド時間を大幅短縮

### 一時ディレクトリの指定

```yaml
plugins:
  - svg-to-png:
      # 大量のSVGがある場合は一時ディレクトリを分離
      temp_dir: "/tmp/svg_build"
```
