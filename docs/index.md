# MkDocs SVG to PNG Plugin


**MkDocs環境でSVGファイルをPNG画像として事前レンダリングし、PDF出力に対応させるプラグインです。**

- [Sample PDF](MkDocs-Mermaid-to-Image.pdf)

## ✨ 特徴

- SVGファイルをPNG画像として事前レンダリング
- PDF出力対応
- キャッシュ機能による高速ビルド
- 高度な設定オプション（DPI、品質、背景色など）

## Sample SVG

```svg
<svg width="100" height="100">
  <circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" />
</svg>
```

## 開発ガイド

このセクションは `mkdocs-svg-to-png` プラグインの開発に参加するための総合的なガイドです。

### 前提条件

開発を始める前に、以下のツールがシステムにインストールされていることを確認してください。

- **Python**: 3.9 以上
- **uv**: 高速なPythonパッケージインストーラー
- **Make**: ビルド自動化ツール
- **CairoSVGの依存関係**: `libcairo2-dev libffi-dev libgdk-pixbuf2.0-dev libpango1.0-dev` (Debian/Ubuntuの場合)

### セットアップ

開発環境のセットアップは、リポジトリのルートで以下のコマンドを実行するだけです。

```bash
make setup
```

このコマンドは、Pythonの依存関係をインストールし、pre-commitフックを設定します。

### ローカルでのビルドとインストール

開発中にプラグインの動作を確認するには、ローカルでビルドしてインストールする必要があります。
ソースコードの変更を即座に反映させるために、編集可能モード (`-e`) でインストールすることを推奨します。

```bash
make install-dev
```

これにより、`mkdocs.yml` で `svg-to-png` プラグインを指定したMkDocsプロジェクトで、開発中のプラグインを直接テストできます。

### よく使うコマンド

`Makefile` には、開発を効率化するためのコマンドが多数定義されています。

#### 開発コマンド

- `make install-dev`: 開発用に編集可能モードでパッケージをインストールします。
- `make test`: すべてのテストを実行します。
- `make test-cov`: カバレッジレポート付きでテストを実行します。

#### 品質チェック

- `make check`: 品質チェック（pre-commitフックと同等の内容）を実行します。
- `make check-security`: セキュリティチェック（bandit + pip-audit）を実行します。
- `make check-all`: 完全チェック（品質 + セキュリティ）を実行します。

#### MkDocsコマンド

- `uv run mkdocs serve`: 開発用のローカルサーバーを起動します。
- `uv run mkdocs build`: ドキュメントサイトをビルドします。
- `ENABLE_PDF_EXPORT=1 uv run mkdocs build`: PDF生成を有効にしてドキュメントサイトをビルドします。

利用可能なすべてのコマンドについては、`make help` を実行して確認してください。

### 開発ワークフロー

#### 日常的な開発

1. **コード変更後**:
   ```bash
   make check  # 品質チェック（自動修正含む）
   ```

2. **テスト実行**:
   ```bash
   make test   # 全テスト実行
   ```

#### コミット前

```bash
make check  # pre-commitフックと同等のチェック
```

#### プルリクエスト前

```bash
make check-all  # 品質 + セキュリティの完全チェック
```

#### PDF生成テスト

```bash
ENABLE_PDF_EXPORT=1 uv run mkdocs build
```
