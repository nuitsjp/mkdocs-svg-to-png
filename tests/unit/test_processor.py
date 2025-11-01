"""
SvgProcessorクラスのテスト
このファイルでは、SvgProcessorクラスの動作を検証します。
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from mkdocs_svg_to_png.processor import SvgBlockProcessingResult, SvgProcessor
from mkdocs_svg_to_png.svg_block import SvgBlock


class TestSvgProcessor:
    """SvgProcessorクラスのテストクラス"""

    def test_processor_initialization(self, svg_config):
        """SvgProcessorの初期化が正しく行われるかテスト"""
        processor = SvgProcessor(svg_config)
        assert processor.config == svg_config
        assert processor.logger is not None
        assert processor.markdown_processor is not None
        assert processor.svg_converter is not None
        assert hasattr(processor, "_process_svg_blocks")

    def test_process_page_with_blocks(self, svg_config):
        """SVGブロックがある場合のページ処理をテスト"""
        processor = SvgProcessor(svg_config)

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

    def test_process_page_no_blocks(self, svg_config):
        """SVGブロックがない場合は元の内容が返るかテスト"""
        processor = SvgProcessor(svg_config)

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

    def test_process_page_with_conversion_failure(self, svg_config):
        """画像変換が失敗した場合の挙動をテスト"""
        processor = SvgProcessor(svg_config)

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

    def test_process_page_with_svg_file_reference_failure(self, svg_config):
        """SVGファイル参照の変換が失敗した場合の挙動をテスト（Mermaidのような相対パス）"""
        processor = SvgProcessor(svg_config)

        # SVGファイル参照の変換が失敗するブロックをモック
        mock_block = Mock(spec=SvgBlock)
        mock_block.get_filename.return_value = "test_mermaid_0_abc123.png"
        mock_block.generate_png.return_value = False  # SVGファイルが見つからず失敗

        processor.markdown_processor.extract_svg_blocks = Mock(
            return_value=[mock_block]
        )

        markdown = """# Test Mermaid Reference

![Mermaid Diagram](../assets/images/test_mermaid_0_abc123.svg)
"""
        result_content, result_paths = processor.process_page(
            "subdirectory/test.md", markdown, "/output"
        )

        # error_on_fail=Falseなので元の内容が返る
        assert result_content == markdown
        assert len(result_paths) == 0
        mock_block.generate_png.assert_called_once()

    def test_processor_has_no_legacy_failure_handlers(self, svg_config):
        """未使用のエラーハンドラが残っていないことを確認する。"""
        processor = SvgProcessor(svg_config)

        assert not hasattr(processor, "_log_generation_failure")
        assert not hasattr(processor, "_raise_generation_error")
        assert not hasattr(processor, "_handle_file_error")
        assert not hasattr(processor, "_handle_unexpected_error")

    def test_process_svg_blocks_returns_structured_results(self, svg_config, tmp_path):
        """_process_svg_blocks がブロックとパスを含む専用結果を返すか確認する。"""
        processor = SvgProcessor(svg_config)
        block = SvgBlock(code="<svg width='10' height='10'></svg>")

        with patch.object(SvgBlock, "generate_png", return_value=True) as mock_generate:
            results = processor._process_svg_blocks([block], "diagram.md", tmp_path)

        assert len(results) == 1
        result = results[0]
        assert isinstance(result, SvgBlockProcessingResult)
        assert result.block is block
        assert result.image_path.endswith(".png")
        mock_generate.assert_called_once_with(
            result.image_path, processor.svg_converter
        )

    def test_resolve_svg_file_paths_rejects_non_svg_block(self, svg_config, tmp_path):
        """SvgBlock 以外が渡された場合に例外が発生することを確認する。"""
        processor = SvgProcessor(svg_config)

        with pytest.raises(TypeError):
            processor._resolve_svg_file_paths(
                [object()],
                docs_dir=tmp_path,
                page_file="invalid.md",
            )

    def test_process_page_with_svg_file_reference_needs_docs_base_path(self, tmp_path):
        """SVGファイル参照でdocs_base_pathが必要なケースをテスト"""
        config = {
            "output_dir": "assets/images",
            "preserve_original": False,
            "error_on_fail": False,
            "log_level": "INFO",
            "dpi": 150,
            "quality": 90,
        }
        processor = SvgProcessor(config)

        # MkDocsのようなディレクトリ構造
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        assets_dir = docs_dir / "assets" / "images"
        assets_dir.mkdir(parents=True)

        # SVGファイルを作成
        svg_content = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">'
            '<rect width="100" height="100" fill="red"/>'
            "</svg>"
        )
        svg_file = assets_dir / "architecture_mermaid_0_abc123.svg"
        svg_file.write_text(svg_content)

        # Mermaidプラグインで生成されるようなMarkdown
        markdown = """# Architecture

![Mermaid Diagram](assets/images/architecture_mermaid_0_abc123.svg)
"""

        # 現在の実装では相対パス解決に失敗するはず
        result_content, result_paths = processor.process_page(
            "architecture.md", markdown, str(assets_dir)
        )

        # 変換に失敗してオリジナルのMarkdownが返るはず
        assert result_content == markdown
        assert len(result_paths) == 0

    def test_process_page_svg_file_path_resolution_with_docs_dir(self, tmp_path):
        """SVGファイルパス解決にdocs_dirが必要なケースのテスト"""
        config = {
            "output_dir": "assets/images",
            "preserve_original": False,
            "error_on_fail": False,
            "log_level": "INFO",
            "dpi": 150,
            "quality": 90,
        }
        processor = SvgProcessor(config)

        # MkDocsのようなディレクトリ構造
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        assets_dir = docs_dir / "assets" / "images"
        assets_dir.mkdir(parents=True)

        # SVGファイルを作成
        svg_content = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">'
            '<rect width="100" height="100" fill="red"/>'
            "</svg>"
        )
        svg_file = assets_dir / "architecture_mermaid_0_abc123.svg"
        svg_file.write_text(svg_content)

        # Mermaidプラグインで生成されるようなMarkdown
        markdown = """# Architecture

![Mermaid Diagram](assets/images/architecture_mermaid_0_abc123.svg)
"""

        # process_pageにdocs_dirを渡すことで成功するはず
        result_content, result_paths = processor.process_page(
            "architecture.md",
            markdown,
            str(assets_dir),
            docs_dir=str(docs_dir),  # docs_dirを渡す
        )

        # SVGからPNGへの変換が成功し、画像パスが返るはず
        assert len(result_paths) == 1
        assert result_content != markdown  # Markdownが変更されているはず

        # 生成されたPNGファイルが存在することを確認
        generated_png_path = Path(result_paths[0])
        assert generated_png_path.exists()
        assert generated_png_path.suffix == ".png"
