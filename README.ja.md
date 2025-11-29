# mkdocs-svg-to-png

[![PyPI - Python Version][python-image]][pypi-link]

MkDocs で Markdown 内の SVG コードブロックやローカル SVG ファイル参照を
Playwright で PNG へ変換するプラグインです。`mkdocs-to-pdf` で PDF を作る際に
背景色やテーマ適用が抜け、図が正しく描画されない（とくに draw.io 生成の SVG
で顕著）問題を回避するために、SVG を一度 PNG に変換してから PDF へ含めます。

## 背景と目的

- `mkdocs-to-pdf` では SVG の背景や塗りつぶしがテーマ適用されず、図が透明背景のまま
  埋め込まれるケースがあります。draw.io 由来の SVG では白背景が欠落して文字が読みにくく
  なることがあります。
- SVG を PNG に書き出したものを PDF に載せることで、テーマ色や塗りつぶしを確実に残した
  まま PDF を生成します。
- 外部サービスにアップロードせず、ローカル完結で図を扱えるため機密資料でも安全です。

## 主な機能

- Markdown の ` ```svg` コードブロックとローカル `*.svg` ファイル参照を自動検出し PNG 化
- Playwright ベースのレンダリングで SVG の背景色や塗りつぶしを忠実に反映
- `enabled_if_env` で環境変数がセットされたときだけ動作させる条件付き有効化
- `mkdocs serve` 時は自動的に変換をスキップし、編集時の待ち時間をゼロに維持
- `preserve_original` で変換後の PNG と元の SVG を併記可能（テーマ崩れの比較に便利）
- ビルド後に生成 PNG を削除する `cleanup_generated_images` を備え、CI の一時ファイルを整理

## 動作要件

- Python 3.9+
- MkDocs 1.4.0 以上、MkDocs Material 8.0.0 以上
- Playwright 1.40.0 以上（レンダリング用ブラウザのダウンロードが必要）

## インストール

pip の場合:

```bash
pip install mkdocs-svg-to-png
python -m playwright install
```

uv を使う場合（開発向け推奨）:

```bash
uv add mkdocs-svg-to-png
uv run python -m playwright install
```

`python -m playwright install` で Playwright が使うブラウザを取得しないと、変換は失敗します。

## クイックスタート

`mkdocs.yml` でプラグインを登録します。`enabled_if_env` は有効化に使う環境変数名です。

```yaml
plugins:
  - search
  - svg-to-png:
      enabled_if_env: ENABLE_PDF_EXPORT
```

Mermaid → SVG → PNG → PDF をローカルで完結させる構成例:

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

## ENABLE_PDF_EXPORT と運用の考え方

PNG 変換や PDF 生成は Playwright 実行が入るため重い処理です。執筆中の高速なプレビューは
維持しつつ、成果物生成は CI でのみ実行できるように環境変数で制御します。

- 日常の執筆: `mkdocs serve` はプラグインが自動でスキップされるため、そのまま高速プレビュー
- ローカル確認: `mkdocs build`（環境変数なし）で通常の静的サイトだけを生成
- PDF/PNG を含むビルド: `ENABLE_PDF_EXPORT=1 mkdocs build` または
  `ENABLE_PDF_EXPORT=1 make build` を CI で実行する

この切り替えにより、作者は軽いプレビューを保ちつつ、CI では完全な PDF 付き成果物を得られます。

## 使い方

### インライン SVG

```markdown
```svg
<svg width="120" height="120">
  <rect x="10" y="10" width="100" height="100"
        stroke="black" stroke-width="3" fill="white" />
</svg>
```
```

検出されたブロックは PNG を生成し、対応する `<img>` 参照に置き換わります。

### SVG ファイル参照

ローカルファイル参照（HTTP 経由は対象外）も PNG 化されます。

```markdown
![シーケンス図](diagrams/sequence.svg)
```

生成ファイルは `docs/assets/images/`（`output_dir` のデフォルト）以下に配置され、サイトに
組み込まれます。

## 設定

| 設定項目 | デフォルト | 説明 |
| --- | --- | --- |
| `enabled_if_env` | `null` | 指定した環境変数がセットされたときのみプラグインを有効化。未設定なら常に有効。 |
| `output_dir` | `assets/images` | 生成 PNG の保存先。`docs/` からの相対パス。 |
| `preserve_original` | `false` | PNG 参照の下に元の SVG を残します。テーマ崩れ確認や差分比較に便利。 |
| `error_on_fail` | `false` | 変換失敗時にビルドを停止するかどうか。`true` なら例外で中断。 |
| `log_level` | `INFO` | プラグインのログレベル。ルートロガーが DEBUG の場合は自動的に DEBUG を採用。 |
| `cleanup_generated_images` | `false` | ビルド完了後に生成 PNG を削除します。CI のワークスペース掃除に有効。 |

## PDF 向け利用のポイント

1. `mkdocs-mermaid-to-svg` で Mermaid を SVG 化
2. 本プラグインで SVG を PNG 化し、背景・塗りつぶしを確実に残す
3. `mkdocs-to-pdf` で PDF を生成し、draw.io を含む図も崩れず出力

## トラブルシューティング

- Playwright が見つからないエラー: `python -m playwright install` を実行
- 生成先の権限エラー: `output_dir` の書き込み権限とディスク容量を確認
- 変換結果を比較したい: `preserve_original: true` と `log_level: DEBUG` で原因を切り分け
- CI で失敗を検出したい: `error_on_fail: true` で変換エラー時にビルドを落とす

## 開発・メンテナンス

- 依存関係のセットアップ: `make install-dev`
- テスト: `make test`（カバレッジ付きは `make test-cov`）
- 静的解析: `make format` / `make lint` / `make typecheck`
- ドキュメントビルド: `make build`（PDF 付きは `ENABLE_PDF_EXPORT=1 make build-pdf`）

## ライセンスと関連プロジェクト

- ライセンス: MIT
- 関連: [mkdocs-mermaid-to-svg](https://github.com/nuitsjp/mkdocs-mermaid-to-svg) /
  [mkdocs-to-pdf](https://github.com/orzih/mkdocs-to-pdf)

[pypi-link]: https://pypi.org/project/mkdocs-svg-to-png/
[python-image]: https://img.shields.io/pypi/pyversions/mkdocs-svg-to-png?logo=python&logoColor=aaaaaa&labelColor=333333
