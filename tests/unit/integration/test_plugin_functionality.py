"""
MkDocs Svg to Png Plugin - 統合機能テストスクリプト
"""

import sys
from unittest.mock import Mock, patch

from mkdocs_svg_to_png.config import SvgConfigManager
from mkdocs_svg_to_png.plugin import SvgToPngPlugin
from mkdocs_svg_to_png.processor import SvgProcessor
from mkdocs_svg_to_png.utils import (
    generate_image_filename,
)


def test_plugin_initialization():
    """プラグインの初期化テスト"""
    plugin = SvgToPngPlugin()
    assert plugin is not None


def test_processor_functionality():
    """Svgプロセッサの機能テスト"""
    config = {
        "output_dir": "assets/images",
        "image_format": "png",
        "preserve_original": False,
        "error_on_fail": False,
        "log_level": "INFO",
        "output_path": "assets/images",
        "dpi": 150,
        "quality": 90,
    }
    processor = SvgProcessor(config)
    markdown_content = """# Test

```svg
<svg>A</svg>
```

Some text.

![An SVG](image.svg)
"""
    blocks = processor.markdown_processor.extract_svg_blocks(markdown_content)
    assert len(blocks) == 2
    assert "<svg>A</svg>" in blocks[0].code
    assert "image.svg" in blocks[1].file_path


def test_config_validation():
    """設定検証機能のテスト"""
    valid_config = {
        "output_path": "assets/images",
        "dpi": 150,
        "quality": 90,
        # Configuration for processor
    }
    # This test might need adjustment depending on the new config structure
    # For now, we assume a simple validation check
    assert SvgConfigManager().validate(valid_config) == valid_config


def test_utils():
    """ユーティリティ関数のテスト"""
    filename = generate_image_filename("test.md", 0, "<svg></svg>", "png")
    assert filename.endswith(".png")
    assert "test_svg_0_" in filename


def test_serve_mode_integration():
    """serve モード統合テスト - 実際のワークフローを模擬"""

    # Test 1: serve モードでの完全なワークフロー
    with patch.object(sys, "argv", ["mkdocs", "serve"]):
        # プラグイン初期化
        plugin = SvgToPngPlugin()
        assert plugin.is_serve_mode is True

        # 設定を模擬
        plugin.config = {
            "enabled": True,
            "output_dir": "assets/images",
            "image_format": "png",
            "preserve_original": False,
            "error_on_fail": False,
            "log_level": "INFO",
            "dpi": 150,
            "quality": 90,
        }

        # プロセッサを模擬（実際には初期化されない想定）
        plugin.processor = Mock()

        # Mockページとconfig
        mock_page = Mock()
        mock_page.file.src_path = "example.md"
        mock_config = {"docs_dir": "/docs"}

        # 複数のSVGブロックを含むMarkdown
        test_markdown = """
# サンプルページ

## フローチャート

```svg
<svg>A</svg>
```

## シーケンス図

![An SVG](b.svg)

通常のテキストコンテンツ
"""

        # ページ処理実行
        result = plugin.on_page_markdown(
            test_markdown, page=mock_page, config=mock_config, files=[]
        )

        # 検証
        assert result == test_markdown  # 元のMarkdownがそのまま返される
        plugin.processor.process_page.assert_not_called()  # プロセッサが呼ばれない
        assert len(plugin.generated_images) == 0  # 画像は生成されない


def test_build_mode_integration():
    """build モード統合テスト - 実際のワークフローを模擬"""

    # Test 2: build モードでの完全なワークフロー
    with patch.object(sys, "argv", ["mkdocs", "build"]):
        # プラグイン初期化
        plugin = SvgToPngPlugin()
        assert plugin.is_serve_mode is False

        # 設定を模擬
        plugin.config = {
            "enabled": True,
            "output_dir": "assets/images",
            "error_on_fail": False,
            "dpi": 150,
            "quality": 90,
        }

        # プロセッサを模擬して成功ケースを再現
        mock_processor = Mock()
        mock_processor.process_page.return_value = (
            """
# サンプルページ

## フローチャート

<img alt=\"SVG Diagram\" src=\"assets/images/example_svg_0_abc123.png\" />

## シーケンス図

<img alt=\"SVG Diagram\" src=\"assets/images/example_svg_1_def456.png\" />

通常のテキストコンテンツ
""".strip(),
            [
                "assets/images/example_svg_0_abc123.png",
                "assets/images/example_svg_1_def456.png",
            ],
        )
        plugin.processor = mock_processor

        # Mockページとconfig
        mock_page = Mock()
        mock_page.file.src_path = "example.md"
        mock_config = {"docs_dir": "/docs", "site_dir": "/site"}

        # 複数のSVGブロックを含むMarkdown
        test_markdown = """
# サンプルページ

## フローチャート

```svg
<svg>A</svg>
```

## シーケンス図

![An SVG](b.svg)

通常のテキストコンテンツ
"""

        # ページ処理実行
        result = plugin.on_page_markdown(
            test_markdown, page=mock_page, config=mock_config, files=[]
        )

        # 検証
        assert "assets/images/example_svg_0_abc123.png" in result
        assert "assets/images/example_svg_1_def456.png" in result
        plugin.processor.process_page.assert_called_once()  # プロセッサが呼ばれる
        assert len(plugin.generated_images) == 2  # 2つの画像が記録される


def test_mixed_command_scenarios():
    """様々なコマンドシナリオでのserve検出テスト"""

    # gh-deploy コマンド
    with patch.object(sys, "argv", ["mkdocs", "gh-deploy", "--force"]):
        plugin = SvgToPngPlugin()
        assert plugin.is_serve_mode is False

    # serve コマンド（詳細オプション付き）
    with patch.object(
        sys, "argv", ["mkdocs", "serve", "--dev-addr", "0.0.0.0:8000", "--livereload"]
    ):
        plugin = SvgToPngPlugin()
        assert plugin.is_serve_mode is True

    # build コマンド（クリーンオプション付き）
    with patch.object(sys, "argv", ["mkdocs", "build", "--clean"]):
        plugin = SvgToPngPlugin()
        assert plugin.is_serve_mode is False


def test_serve_mode_performance_optimization():
    """serve モードでのパフォーマンス最適化効果の検証"""

    with patch.object(sys, "argv", ["mkdocs", "serve"]):
        plugin = SvgToPngPlugin()
        plugin.config = {"enabled": True}
        plugin.processor = Mock()
        plugin.logger = Mock()

        # 大量のSVGブロックを含むMarkdown（パフォーマンステスト用）
        large_markdown = "# Test Page\n\n"
        for i in range(10):  # 10個のSVGブロック
            large_markdown += f"""
## Diagram {i}
```svg
<svg>{i}</svg>
```
"""

        mock_page = Mock()
        mock_page.file.src_path = "large_page.md"
        mock_config = {"docs_dir": "/docs"}

        # ページ処理実行
        result = plugin.on_page_markdown(
            large_markdown, page=mock_page, config=mock_config, files=[]
        )

        # パフォーマンス最適化の検証
        assert result == large_markdown  # 元のMarkdownがそのまま返される
        # 重い画像生成処理がスキップされる
        plugin.processor.process_page.assert_not_called()
        assert len(plugin.generated_images) == 0  # 画像生成なし
