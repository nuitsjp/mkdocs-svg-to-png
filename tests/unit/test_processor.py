"""
SvgProcessorクラスのテスト
このファイルでは、SvgProcessorクラスの動作を検証します。
"""

from unittest.mock import Mock

import pytest

from mkdocs_svg_to_png.processor import SvgProcessor
from mkdocs_svg_to_png.svg_block import SvgBlock


class TestSvgProcessor:
    """SvgProcessorクラスのテストクラス"""

    @pytest.fixture
    def basic_config(self):
        """テスト用の基本設定を返すfixture"""
        return {
            "output_dir": "assets/images",
            "output_format": "png",
            "preserve_original": False,
            "error_on_fail": False,
            "log_level": "INFO",
            "output_path": "assets/images",
            "dpi": 150,
            "quality": 90,
        }

    def test_processor_initialization(self, basic_config):
        """SvgProcessorの初期化が正しく行われるかテスト"""
        processor = SvgProcessor(basic_config)
        assert processor.config == basic_config
        assert processor.logger is not None
        assert processor.markdown_processor is not None
        assert processor.svg_converter is not None

    def test_process_page_with_blocks(self, basic_config):
        """SVGブロックがある場合のページ処理をテスト"""
        processor = SvgProcessor(basic_config)

        # SvgBlockのモックを作成
        mock_block = Mock(spec=SvgBlock)
        mock_block.get_filename.return_value = "test_0_abc123.png"
        mock_block.generate_png.return_value = True

        # markdown_processorのメソッドをモック化
        processor.markdown_processor.extract_svg_blocks = Mock(
            return_value=[mock_block]
        )
        processor.markdown_processor.replace_blocks_with_images = Mock(
            return_value="![SVG](test.png)"
        )

        markdown = """# Test

```svg
<svg></svg>
```
"""
        # ページ処理を実行
        result_content, result_paths = processor.process_page(
            "test.md", markdown, "/output"
        )

        assert result_content == "![SVG](test.png)"
        assert len(result_paths) == 1
        mock_block.generate_png.assert_called_once()
        mock_block.get_filename.assert_called_once_with("test.md", 0, "png")

    def test_process_page_no_blocks(self, basic_config):
        """SVGブロックがない場合は元の内容が返るかテスト"""
        processor = SvgProcessor(basic_config)

        # ブロック抽出が空リストを返すようにモック
        processor.markdown_processor.extract_svg_blocks = Mock(return_value=[])

        markdown = """# Test

```python
print("Hello")
```
"""
        result_content, result_paths = processor.process_page(
            "test.md", markdown, "/output"
        )

        assert result_content == markdown
        assert len(result_paths) == 0

    def test_process_page_with_conversion_failure(self, basic_config):
        """画像変換が失敗した場合の挙動をテスト"""
        processor = SvgProcessor(basic_config)

        # 画像変換が失敗するブロックをモック
        mock_block = Mock(spec=SvgBlock)
        mock_block.get_filename.return_value = "test_0_abc123.png"
        mock_block.generate_png.return_value = False  # 変換失敗

        processor.markdown_processor.extract_svg_blocks = Mock(
            return_value=[mock_block]
        )

        markdown = """```svg
<svg></svg>
```"""
        result_content, result_paths = processor.process_page(
            "test.md", markdown, "/output"
        )

        # error_on_fail=Falseなので元の内容が返る
        assert result_content == markdown
        assert len(result_paths) == 0
