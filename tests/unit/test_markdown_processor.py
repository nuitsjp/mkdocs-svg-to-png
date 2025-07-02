"""
MarkdownProcessorクラスのテスト
このファイルでは、MarkdownProcessorクラスの動作を検証します。

Python未経験者へのヒント：
- pytestを使ってテストを書いています。
- Mockやpatchで外部依存を疑似的に置き換えています。
- assert文で「期待する結果」かどうかを検証します。
"""

from unittest.mock import Mock

import pytest

from mkdocs_svg_to_png.exceptions import SvgParsingError
from mkdocs_svg_to_png.markdown_processor import MarkdownProcessor
from mkdocs_svg_to_png.svg_block import SvgBlock


class TestMarkdownProcessor:
    """MarkdownProcessorクラスのテストクラス"""

    @pytest.fixture
    def basic_config(self):
        """テスト用の基本設定を返すfixture"""
        return {"preserve_original": False, "log_level": "INFO"}

    def test_extract_basic_svg_blocks(self, basic_config):
        """基本的なSVGブロック抽出のテスト"""
        processor = MarkdownProcessor(basic_config)

        markdown = """# Test

```svg
<svg>A</svg>
```

Some text.

![An SVG](image.svg)
"""
        blocks = processor.extract_svg_blocks(markdown)
        assert len(blocks) == 2
        assert "<svg>A</svg>" in blocks[0].code
        assert "image.svg" in blocks[1].file_path
        assert blocks[0].start_pos < blocks[1].start_pos

    def test_extract_svg_blocks_with_attributes(self, basic_config):
        """属性付きSVGブロックの抽出テスト"""
        processor = MarkdownProcessor(basic_config)

        markdown = """```svg {width: "200", height: '150'}
<svg>B</svg>
```"""
        blocks = processor.extract_svg_blocks(markdown)
        assert len(blocks) == 1
        assert blocks[0].attributes.get("width") == "200"
        assert blocks[0].attributes.get("height") == "150"

    def test_extract_no_svg_blocks(self, basic_config):
        """SVGブロックが存在しない場合の抽出テスト"""
        processor = MarkdownProcessor(basic_config)

        markdown = """# Test

```python
print("Hello")
```

Some text.
"""
        blocks = processor.extract_svg_blocks(markdown)
        assert len(blocks) == 0

    def test_extract_mixed_blocks_no_overlap(self, basic_config):
        """属性付き・属性なしブロック混在時の抽出テスト"""
        processor = MarkdownProcessor(basic_config)

        markdown = """```svg {width: 300}
<svg>C</svg>
```

![Another](another.svg)
"""
        blocks = processor.extract_svg_blocks(markdown)
        assert len(blocks) == 2
        assert blocks[0].attributes.get("width") == "300"
        assert blocks[1].attributes == {}

    def test_parse_attributes_basic(self, basic_config):
        """属性文字列のパース基本テスト"""
        processor = MarkdownProcessor(basic_config)

        result = processor._parse_attributes("width: 200, height: 150")
        expected = {"width": "200", "height": "150"}
        assert result == expected

    def test_parse_attributes_with_quotes(self, basic_config):
        """クォート付き属性のパーステスト"""
        processor = MarkdownProcessor(basic_config)

        result = processor._parse_attributes("width: \"200\", height: '150'")
        expected = {"width": "200", "height": "150"}
        assert result == expected

    def test_parse_attributes_with_spaces(self, basic_config):
        """空白を含む属性文字列のパーステスト"""
        processor = MarkdownProcessor(basic_config)

        result = processor._parse_attributes("  width  :  200  ,  height  :  150  ")
        expected = {"width": "200", "height": "150"}
        assert result == expected

    def test_parse_attributes_empty(self, basic_config):
        """空文字列のパースで空辞書が返るかテスト"""
        processor = MarkdownProcessor(basic_config)

        result = processor._parse_attributes("")
        assert result == {}

    def test_parse_attributes_invalid_format(self, basic_config):
        """無効な形式の属性が無視されるかテスト"""
        processor = MarkdownProcessor(basic_config)

        # 無効な形式の属性は無視される
        result = processor._parse_attributes("invalid, width: 200")
        expected = {"width": "200"}
        assert result == expected

    def test_replace_blocks_with_images_basic(self, basic_config):
        """画像Markdownへの置換の基本テスト"""
        processor = MarkdownProcessor(basic_config)

        markdown = """# Test

```svg
<svg>A</svg>
```

More content."""
        # SvgBlockのモックを作成
        mock_block = Mock(spec=SvgBlock)
        mock_block.start_pos = markdown.find("```svg")
        mock_block.end_pos = markdown.find("```", mock_block.start_pos + 1) + 3
        mock_block.get_image_markdown.return_value = (
            "![SVG Diagram](assets/images/test.png)"
        )

        blocks = [mock_block]
        image_paths = ["/path/to/test.png"]

        result = processor.replace_blocks_with_images(
            markdown, blocks, image_paths, "test.md"
        )

        assert "![SVG Diagram](assets/images/test.png)" in result
        assert "```svg" not in result
        mock_block.get_image_markdown.assert_called_once_with(
            "/path/to/test.png", "test.md", False, ""
        )

    def test_replace_blocks_with_images_preserve_original(self, basic_config):
        """元のコードも残す場合の置換テスト"""
        basic_config["preserve_original"] = True
        processor = MarkdownProcessor(basic_config)

        markdown = """```svg
<svg>A</svg>
```"""
        mock_block = Mock(spec=SvgBlock)
        mock_block.start_pos = 0
        mock_block.end_pos = len(markdown)
        mock_block.get_image_markdown.return_value = (
            "![SVG Diagram](test.png)\n\n```svg\n<svg>A</svg>\n```"
        )

        blocks = [mock_block]
        image_paths = ["/path/to/test.png"]

        result = processor.replace_blocks_with_images(
            markdown, blocks, image_paths, "test.md"
        )

        assert "![SVG Diagram](test.png)" in result
        assert "```svg" in result  # Original preserved
        mock_block.get_image_markdown.assert_called_once_with(
            "/path/to/test.png", "test.md", True, ""
        )

    def test_replace_blocks_mismatched_lengths(self, basic_config):
        """ブロック数と画像パス数が異なる場合のエラーをテスト"""
        processor = MarkdownProcessor(basic_config)

        markdown = "test"
        blocks = [Mock(), Mock()]
        image_paths = ["/path/to/test.png"]  # Only one path for two blocks

        with pytest.raises(
            SvgParsingError, match="Number of blocks and image paths must match"
        ):
            processor.replace_blocks_with_images(
                markdown, blocks, image_paths, "test.md"
            )

    def test_replace_multiple_blocks_reverse_order(self, basic_config):
        """複数ブロックを逆順で置換することで位置ズレを防ぐテスト"""
        processor = MarkdownProcessor(basic_config)

        markdown = """```svg
<svg>A</svg>
```

![B](b.svg)"""
        # 2つのブロックを作成（位置が重要）
        block1 = Mock(spec=SvgBlock)
        block1.start_pos = 0
        block1.end_pos = markdown.find("\n\n")
        block1.get_image_markdown.return_value = "![A](a.png)"

        block2 = Mock(spec=SvgBlock)
        block2.start_pos = markdown.find("![B]")
        block2.end_pos = len(markdown)
        block2.get_image_markdown.return_value = "![B](b.png)"

        blocks = [block1, block2]  # 順序通り
        image_paths = ["/a.png", "/b.png"]

        result = processor.replace_blocks_with_images(
            markdown, blocks, image_paths, "test.md"
        )

        assert "![A](a.png)" in result
        assert "![B](b.png)" in result
        assert "```svg" not in result
        assert "b.svg" not in result

        # 両方のブロックが呼び出されることを確認
        block1.get_image_markdown.assert_called_once()
        block2.get_image_markdown.assert_called_once()

    def test_extract_svg_file_references(self, basic_config):
        """SVGファイル参照の抽出テスト"""
        processor = MarkdownProcessor(basic_config)

        markdown = """# Test

![diagram](images/test.svg)

Some text.

![Another diagram](../assets/diagram.svg)
"""
        svg_blocks = processor.extract_svg_blocks(markdown)
        assert len(svg_blocks) == 2
        assert svg_blocks[0].file_path == "images/test.svg"
        assert svg_blocks[1].file_path == "../assets/diagram.svg"

    def test_extract_inline_svg_code_blocks(self, basic_config):
        """インラインSVGコードブロックの抽出テスト"""
        processor = MarkdownProcessor(basic_config)

        markdown = """# Test

```svg
<svg width="100" height="100">
  <circle cx="50" cy="50" r="40" fill="red" />
</svg>
```

Some text.

```svg {width: 200, height: 150}
<svg viewBox="0 0 100 100">
  <rect x="10" y="10" width="80" height="80" fill="blue" />
</svg>
```
"""
        svg_blocks = processor.extract_svg_blocks(markdown)
        assert len(svg_blocks) == 2
        assert "<circle" in svg_blocks[0].code
        assert "<rect" in svg_blocks[1].code
        assert svg_blocks[1].attributes.get("width") == "200"

    def test_extract_mixed_svg_content(self, basic_config):
        """SVGファイル参照とインラインSVGの混在テスト"""
        processor = MarkdownProcessor(basic_config)

        markdown = """# Test

![file ref](diagram.svg)

```svg
<svg><circle cx="50" cy="50" r="20" /></svg>
```

![another file](assets/chart.svg)
"""
        svg_blocks = processor.extract_svg_blocks(markdown)
        assert len(svg_blocks) == 3
        # ファイル参照とインラインコードが正しく区別される
        assert any(block.file_path == "diagram.svg" for block in svg_blocks)
        assert any("<circle" in block.code for block in svg_blocks)
        assert any(block.file_path == "assets/chart.svg" for block in svg_blocks)
