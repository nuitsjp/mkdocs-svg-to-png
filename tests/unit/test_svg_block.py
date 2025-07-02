"""
SvgBlockクラスのテスト
このファイルでは、SvgBlockクラスの動作を検証します。

SvgBlockは以下をサポートする：
- インラインSVGコード
- SVGファイル参照
- 属性の処理
"""

from unittest.mock import Mock

from mkdocs_svg_to_png.svg_block import (
    SvgBlock,
    _calculate_relative_path_prefix,
)


class TestSvgBlock:
    """SvgBlockクラスのテストクラス"""

    def test_inline_svg_block_creation(self):
        """インラインSVGブロック生成のテスト"""
        svg_code = "<svg><rect width='100' height='100'/></svg>"
        block = SvgBlock(code=svg_code, start_pos=0, end_pos=50)
        assert block.code == svg_code
        assert block.file_path == ""
        assert block.start_pos == 0
        assert block.end_pos == 50
        assert block.attributes == {}

    def test_svg_file_block_creation(self):
        """SVGファイル参照ブロック生成のテスト"""
        file_path = "images/diagram.svg"
        block = SvgBlock(file_path=file_path, start_pos=10, end_pos=40)
        assert block.code == ""
        assert block.file_path == file_path
        assert block.start_pos == 10
        assert block.end_pos == 40
        assert block.attributes == {}

    def test_block_with_attributes(self):
        """属性付きSVGブロックのテスト"""
        svg_code = "<svg><circle r='50'/></svg>"
        attributes = {"width": "200", "height": "150", "alt": "Circle diagram"}
        block = SvgBlock(code=svg_code, start_pos=5, end_pos=25, attributes=attributes)
        assert block.code == svg_code
        assert block.start_pos == 5
        assert block.end_pos == 25
        assert block.attributes == attributes

    def test_block_repr_with_code(self):
        """インラインSVGブロックの文字列表現テスト"""
        svg_code = "<svg><rect width='100' height='100' fill='blue'/></svg>"
        block = SvgBlock(code=svg_code, start_pos=0, end_pos=50)
        repr_str = repr(block)
        assert "SvgBlock(code='" in repr_str
        assert "start=0, end=50)" in repr_str

    def test_block_repr_with_file_path(self):
        """SVGファイル参照ブロックの文字列表現テスト"""
        file_path = "assets/diagrams/architecture.svg"
        block = SvgBlock(file_path=file_path, start_pos=10, end_pos=40)
        repr_str = repr(block)
        assert f"SvgBlock(file_path='{file_path}'" in repr_str
        assert "start=10, end=40)" in repr_str

    def test_generate_png_conversion(self):
        """SVG→PNG変換のテスト"""
        svg_code = "<svg><rect width='100' height='100' fill='red'/></svg>"
        block = SvgBlock(code=svg_code, start_pos=0, end_pos=50)

        # Mock SVG converter
        mock_converter = Mock()
        mock_converter.convert_svg_content.return_value = True

        config = {"dpi": 300, "quality": 95}
        result = block.generate_png("output.png", mock_converter, config)

        assert result is True
        mock_converter.convert_svg_content.assert_called_once_with(
            svg_code, "output.png"
        )

    def test_generate_png_from_file(self):
        """SVGファイルからPNG変換のテスト"""
        file_path = "diagrams/flow.svg"
        block = SvgBlock(file_path=file_path, start_pos=0, end_pos=30)

        # Mock SVG converter
        mock_converter = Mock()
        mock_converter.convert_svg_file.return_value = True

        config = {"dpi": 150, "quality": 80}
        result = block.generate_png("output.png", mock_converter, config)

        assert result is True
        mock_converter.convert_svg_file.assert_called_once_with(file_path, "output.png")

    def test_get_image_markdown(self):
        """画像Markdown生成のテスト"""
        svg_code = "<svg><text>Test</text></svg>"
        block = SvgBlock(code=svg_code, start_pos=0, end_pos=30)

        image_path = "generated/test.png"
        page_file = "docs/guide.md"

        markdown = block.get_image_markdown(image_path, page_file)

        expected = "![SVG Diagram](../assets/images/test.png)"
        assert markdown == expected

    def test_get_image_markdown_with_preserve_original(self):
        """元のSVGコード保持でのMarkdown生成テスト"""
        svg_code = "<svg><rect/></svg>"
        attributes = {"width": "200"}
        block = SvgBlock(code=svg_code, start_pos=0, end_pos=20, attributes=attributes)

        image_path = "generated/test.png"
        page_file = "guide.md"

        markdown = block.get_image_markdown(
            image_path, page_file, preserve_original=True
        )

        assert "![SVG Diagram](assets/images/test.png)" in markdown
        assert "```svg {width: 200}" in markdown
        assert svg_code in markdown

    def test_get_filename(self):
        """ファイル名生成のテスト"""
        svg_code = "<svg><circle/></svg>"
        block = SvgBlock(code=svg_code, start_pos=0, end_pos=20)

        page_file = "docs/examples.md"
        index = 1
        image_format = "png"

        filename = block.get_filename(page_file, index, image_format)

        assert filename.endswith(".png")
        assert "examples" in filename
        assert "1" in filename


class TestRelativePathCalculation:
    """相対パス計算のテスト"""

    def test_root_level_file(self):
        """ルートレベルファイルの相対パステスト"""
        result = _calculate_relative_path_prefix("index.md")
        assert result == ""

    def test_one_level_deep(self):
        """1階層深いファイルの相対パステスト"""
        result = _calculate_relative_path_prefix("docs/guide.md")
        assert result == "../"

    def test_two_levels_deep(self):
        """2階層深いファイルの相対パステスト"""
        result = _calculate_relative_path_prefix("docs/advanced/config.md")
        assert result == "../../"

    def test_empty_page_file(self):
        """空のページファイルの相対パステスト"""
        result = _calculate_relative_path_prefix("")
        assert result == ""
