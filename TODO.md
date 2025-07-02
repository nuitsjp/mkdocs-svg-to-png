# TODO: SVG to PNG プラグイン変換作業

## 重要な指示

1. **進捗を更新すること**: 各タスクの完了時に、[このファイル](./TODO.md)の進捗状況を更新してください
2. **進捗更新時に計画を再考すること**: タスク完了時に、残りの作業と依存関係を見直し、必要に応じて計画を調整してください
3. **t-wada式TDDを徹底すること**:
   - プロダクトソースを修正する場合、**必ず先に修正先を想定したテストを実装する**
   - 各タスクを **Red-Green-Refactor** サイクルで実行する
   - タスクは小さな単位に分解し、各タスクごとにサイクルを回す
   - `make test-cov` と `make check-all` を利用して品質を維持する

**TDDサイクル**:
- **Red**: 失敗するテストを書く
- **Green**: テストを通す最小限のコードを書く
- **Refactor**: コードを改善する（テストは通し続ける）

新しいセッションでも作業を継続できるよう、常に最新の状況を反映させることが重要です。

## 全体概要

`mkdocs-mermaid-to-image` プラグインを `mkdocs-svg-to-png` プラグインに変換する作業です。

- **変換前**: Mermaid コードブロックを抽出 → Mermaid CLI で画像生成
- **変換後**: SVG ファイル/コードブロックを抽出 → CairoSVG で PNG 変換

## 高優先度タスク

### [x] 1. プロジェクト名とパッケージ名の変更
- [x] プロジェクト名を `mkdocs-svg-to-png` に変更
- [x] パッケージディレクトリ名を `mkdocs_svg_to_png` に変更
- [x] pyproject.toml の name と description を更新
- [x] __init__.py の内容を更新
- [x] plugin.py のクラス名を `SvgToPngPlugin` に変更

### [x] 2. 依存関係の変更
- [x] pyproject.toml から Node.js/Mermaid CLI 関連の依存関係を削除
- [x] CairoSVG を依存関係に追加
- [x] package.json を削除（Node.js 依存関係が不要になるため）

### [x] 3. SVG ブロック抽出ロジックの実装
- [x] markdown_processor.py で SVG ファイル参照の検出ロジックを実装
- [x] インライン SVG ブロック（```svg〜```）の検出ロジックを実装
- [x] SVG ファイルパスの解決機能を実装
- [x] SvgBlock クラスを新規作成
- [x] MermaidBlock → SvgBlock にクラス名変更（完全移行）

### [x] 4. PNG 変換機能の実装
- [x] svg_converter.py で CairoSVG を使用した SVG→PNG 変換機能を実装
- [x] SVGファイル/インライン両対応の変換機能実装
- [x] CairoSVG用エラーハンドリング追加
- [x] テスト作成とTDD実装完了

## 中優先度タスク

### [x] 5. 設定スキーマの更新
- [x] config.py に SvgConfigManager クラスを追加
- [x] SVG 処理用の設定項目を追加（DPI、品質等）
- [x] Mermaid 特有の設定を除外した新しいスキーマ
- [x] 設定バリデーション機能追加

### [x] 6. 例外クラスの更新
- [x] exceptions.py の例外クラス名を SVG 関連に変更
- [x] MermaidXXXError → SvgXXXError に変更
- [x] SVG処理用エラーメッセージに更新
- [x] CairoSVG用例外クラス追加

### [x] 7. テストケースの更新
- [x] SvgBlockクラス用テストファイル作成（test_svg_block.py）
- [x] SvgBlockクラスのメソッド実装完了
- [x] tests/ ディレクトリ内のテストファイルを SVG to PNG 用に書き換え
- [x] テストデータを Mermaid から SVG に変更
- [x] モックオブジェクトを CairoSVG 用に更新

### [x] 8. Mermaid レガシーコードのクリーンナップ
- [x] 既存のMermaid関連クラス・モジュールの削除
  - [x] MermaidImageGenerator クラス削除
  - [x] MermaidProcessor クラス削除
  - [x] MermaidBlock クラス削除
  - [x] ConfigManager クラス削除（Mermaid用）
- [x] 不要な依存関係とインポートの削除
- [x] Mermaid関連のテストファイル削除・統合
- [x] 一時的な併存状態の解消

## 低優先度タスク

### [x] 9. ドキュメントの更新
- [x] README.md を SVG to PNG 用に更新
- [x] docs/index.md の内容を更新
- [x] docs/usage.md の使用方法を更新
- [x] docs/architecture.md のアーキテクチャ図と説明を更新

### [x] 10. 最終確認とビルド
- [x] make check でコード品質チェック
- [x] make test でテスト実行
- [x] 実際の SVG ファイルでの動作確認
- [x] パッケージビルドの確認

### [x] 11. ログフォーマットの修正
- [x] ログフォーマットをより簡潔で読みやすい形式に修正

## 各タスクでの作業手順（TDD）

各タスクは以下の手順で実行する：

1. **テスト作成（Red）**:
   ```bash
   # 期待する動作のテストを先に書く
   # テストは失敗することを確認する
   make test-cov
   ```

2. **最小限の実装（Green）**:
   ```bash
   # テストを通すための最小限のコードを書く
   make test-cov  # テストが通ることを確認
   make check-all # 品質チェック
   ```

3. **リファクタリング（Refactor）**:
   ```bash
   # コードを改善する（テストは通し続ける）
   make test-cov  # リファクタリング後もテストが通ることを確認
   make check-all # 品質維持
   ```

## 技術的な注意点

- **SVG 検出パターン**:
  - ファイル参照: `![alt](path/to/file.svg)`
  - インライン: ````svg〜````
- **CairoSVG 使用法**: `cairosvg.svg2png()`
- **ファイル処理**: SVG ファイルの存在確認と相対パス解決
- **エラー処理**: CairoSVG の例外ハンドリング

## 進捗記録

- [x] 作業開始: 2025-01-02
- [x] 高優先度タスク完了: 4/4 完了 (100%) ✅
- [x] 中優先度タスク完了: 5/5 完了 (100%) ✅
- [x] 低優先度タスク完了: 4/4 完了 (100%) ✅
- [x] 全作業完了: 完了 ✅

## 現在のセッション成果（2025-07-02更新）
- **テスト結果**: 154 passed, 0 failed ✅
- **品質チェック**: `make check-all` 全項目通過 ✅
- **システム状況**: Mermaid関連のコードはすべて削除され、SVG機能に完全に移行済み。
- **主要完了事項**:
  - 全高優先度タスク完了
  - 全中優先度タスク完了
  - 全低優先度タスク完了
  - SVG→PNG変換の核心機能完成
  - セキュリティ脆弱性修正（defusedxml導入）
  - t-wada式TDD実装完了
  - ログフォーマットの修正
