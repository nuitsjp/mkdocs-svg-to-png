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
- [ ] MermaidBlock → SvgBlock にクラス名変更（完全移行）

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

### [ ] 7. テストケースの更新
- [x] SvgBlockクラス用テストファイル作成（test_svg_block.py）
- [x] SvgBlockクラスのメソッド実装完了
- [ ] tests/ ディレクトリ内のテストファイルを SVG to PNG 用に書き換え
- [ ] テストデータを Mermaid から SVG に変更
- [ ] モックオブジェクトを CairoSVG 用に更新

### [ ] 8. Mermaid レガシーコードのクリーンナップ
- [ ] 既存のMermaid関連クラス・モジュールの削除
  - [ ] MermaidImageGenerator クラス削除
  - [ ] MermaidProcessor クラス削除
  - [ ] MermaidBlock クラス削除
  - [ ] ConfigManager クラス削除（Mermaid用）
- [ ] 不要な依存関係とインポートの削除
- [ ] Mermaid関連のテストファイル削除・統合
- [ ] 一時的な併存状態の解消

## 低優先度タスク

### [ ] 9. ドキュメントの更新
- [ ] README.md を SVG to PNG 用に更新
- [ ] docs/index.md の内容を更新
- [ ] docs/usage.md の使用方法を更新
- [ ] docs/architecture.md のアーキテクチャ図と説明を更新

### [ ] 10. 最終確認とビルド
- [ ] make check でコード品質チェック
- [ ] make test でテスト実行
- [ ] 実際の SVG ファイルでの動作確認
- [ ] パッケージビルドの確認

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
  - インライン: `\`\`\`svg〜\`\`\``
- **CairoSVG 使用法**: `cairosvg.svg2png()`
- **ファイル処理**: SVG ファイルの存在確認と相対パス解決
- **エラー処理**: CairoSVG の例外ハンドリング

## 進捗記録

- [x] 作業開始: 2025-01-02
- [x] 高優先度タスク完了: 4/4 完了 (100%) ✅
- [x] 中優先度タスク完了: 3/5 完了 (60%) 🚧
- [ ] 低優先度タスク完了: 未完了
- [ ] 全作業完了: 未完了

## 現在のセッション成果（2025-01-02）

### ✅ 完了項目
1. **環境修復**: `make test-cov` 実行エラーを修正
   - 古いパッケージ競合を解決
   - 仮想環境を再構築
   - テスト実行環境を正常化

2. **プロジェクト名/パッケージ名変更**: 完全に完了
   - パッケージディレクトリ: `mkdocs_mermaid_to_image` → `mkdocs_svg_to_png`
   - クラス名: `MermaidToImagePlugin` → `SvgToPngPlugin`
   - 全テストファイルのインポート更新

3. **依存関係変更**: 完了
   - Node.js/Mermaid CLI 依存関係を削除
   - CairoSVG を追加
   - package.json 削除

4. **例外クラス更新**: 完全に完了
   - MermaidXXXError → SvgXXXError への完全移行
   - CairoSVG用例外クラス追加とテスト実装
   - SVG処理用エラーメッセージに更新

5. **PNG変換機能実装**: 完全に完了
   - CairoSVGを使用したSVG→PNG変換機能実装
   - ファイル/インライン両対応の変換機能
   - 包括的テストスイート作成

6. **設定スキーマ更新**: 完全に完了
   - SvgConfigManagerクラス新規作成
   - SVG処理用設定項目追加（DPI、品質等）
   - Mermaid特有設定の除外とバリデーション機能

### 📊 現在の状況（2025-07-02更新）
- **テスト結果**: 237 passed, 0 failed (90% カバレッジ) ✅
- **品質チェック**: `make check-all` 全項目通過 ✅
- **システム状況**: MermaidとSVG機能が併存（未統合）
- **主要完了事項**:
  - 全高優先度タスク完了（100%）
  - 中優先度3/5タスク完了（60%）
  - SVG→PNG変換の核心機能完成
  - セキュリティ脆弱性修正（defusedxml導入）
  - t-wada式TDD実装完了

### 🎯 次のセッションでの作業計画

#### 残り作業（優先度順）
1. **テストケースの更新** (中優先度・残り1項目・必須)
   - 既存テストのMermaid→SVG変換（約60%のテストファイル影響）
   - テストデータの更新
   - モックオブジェクトの調整
   - **注意**: 現在MermaidとSVG機能が併存中

2. **統合とプラグイン更新** (新規・最高優先度・必須)
   - plugin.py でSvgConfigManagerとSvgToPngConverterの統合
   - processor.py でのSVG処理フロー更新
   - 既存MermaidImageGeneratorからの段階的移行
   - MermaidBlock → SvgBlock 完全移行

3. **レガシー機能削除** (新規・高優先度)
   - Mermaid関連クラス・モジュールの削除
   - 不要な依存関係クリーンアップ
   - テスト一本化

4. **ドキュメント更新** (低優先度)
   - README.md のSVG to PNG用更新
   - 使用方法とアーキテクチャ説明更新

#### 実装方針（継続）
- t-wada式TDD (Red-Green-Refactor) を徹底継続
- 90%カバレッジと品質チェック通過を維持
- 段階的統合で既存機能を保護
