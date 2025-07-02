import re
from pathlib import Path
from typing import Any

from .exceptions import MermaidParsingError
from .logging_config import get_logger
from .mermaid_block import MermaidBlock, SvgBlock


class MarkdownProcessor:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.logger = get_logger(__name__)

    def extract_mermaid_blocks(self, markdown_content: str) -> list[MermaidBlock]:
        blocks = []

        basic_pattern = r"```mermaid\s*\n(.*?)\n```"

        attr_pattern = r"```mermaid\s*\{([^}]*)\}\s*\n(.*?)\n```"

        for match in re.finditer(attr_pattern, markdown_content, re.DOTALL):
            attr_str = match.group(1).strip()
            code = match.group(2).strip()

            attributes = self._parse_attributes(attr_str)

            block = MermaidBlock(
                code=code,
                start_pos=match.start(),
                end_pos=match.end(),
                attributes=attributes,
            )
            blocks.append(block)

        for match in re.finditer(basic_pattern, markdown_content, re.DOTALL):
            overlaps = any(
                match.start() >= block.start_pos and match.end() <= block.end_pos
                for block in blocks
            )
            if not overlaps:
                code = match.group(1).strip()
                block = MermaidBlock(
                    code=code, start_pos=match.start(), end_pos=match.end()
                )
                blocks.append(block)

        blocks.sort(key=lambda x: x.start_pos)

        self.logger.info(f"Found {len(blocks)} Mermaid blocks")
        return blocks

    def _parse_attributes(self, attr_str: str) -> dict[str, Any]:
        attributes = {}
        if attr_str:
            for attr in attr_str.split(","):
                if ":" in attr:
                    key, value = attr.split(":", 1)
                    key = key.strip()
                    value = value.strip().strip("\"'")
                    attributes[key] = value
        return attributes

    def replace_blocks_with_images(
        self,
        markdown_content: str,
        blocks: list[MermaidBlock],
        image_paths: list[str],
        page_file: str,
        page_url: str = "",
    ) -> str:
        if len(blocks) != len(image_paths):
            raise MermaidParsingError(
                "Number of blocks and image paths must match",
                source_file=page_file,
                mermaid_code=f"Expected {len(blocks)} images, got {len(image_paths)}",
            )

        sorted_blocks = sorted(
            zip(blocks, image_paths), key=lambda x: x[0].start_pos, reverse=True
        )

        result = markdown_content

        for block, image_path in sorted_blocks:
            image_markdown = block.get_image_markdown(
                image_path,
                page_file,
                self.config.get("preserve_original", False),
                page_url,
            )

            result = (
                result[: block.start_pos] + image_markdown + result[block.end_pos :]
            )

        return result

    def extract_svg_blocks(self, markdown_content: str) -> list[SvgBlock]:
        """SVGファイル参照とインラインSVGコードブロックを抽出する"""
        blocks = []

        # SVGファイル参照パターン: ![alt](path.svg)
        file_pattern = r"!\[[^\]]*\]\(([^)]+\.svg)\)"

        # インラインSVGコードブロックパターン（属性付き）
        attr_pattern = r"```svg\s*\{([^}]*)\}\s*\n(.*?)\n```"

        # インラインSVGコードブロックパターン（基本）
        basic_pattern = r"```svg\s*\n(.*?)\n```"

        # ファイル参照を処理
        for match in re.finditer(file_pattern, markdown_content):
            file_path = match.group(1)
            block = SvgBlock(
                file_path=file_path, start_pos=match.start(), end_pos=match.end()
            )
            blocks.append(block)

        # 属性付きインラインSVGを処理
        for match in re.finditer(attr_pattern, markdown_content, re.DOTALL):
            attr_str = match.group(1).strip()
            code = match.group(2).strip()
            attributes = self._parse_attributes(attr_str)

            block = SvgBlock(
                code=code,
                start_pos=match.start(),
                end_pos=match.end(),
                attributes=attributes,
            )
            blocks.append(block)

        # 基本インラインSVGを処理（既に処理されたものと重複しないように）
        for match in re.finditer(basic_pattern, markdown_content, re.DOTALL):
            overlaps = any(
                match.start() >= block.start_pos and match.end() <= block.end_pos
                for block in blocks
            )
            if not overlaps:
                code = match.group(1).strip()
                block = SvgBlock(
                    code=code, start_pos=match.start(), end_pos=match.end()
                )
                blocks.append(block)

        blocks.sort(key=lambda x: x.start_pos)

        self.logger.info(f"Found {len(blocks)} SVG blocks")
        return blocks

    def _create_svg_block(self, code: str, file_path: str) -> SvgBlock:
        """SVGブロックを作成するヘルパーメソッド（テスト用）"""
        return SvgBlock(code=code, file_path=file_path)

    def resolve_svg_file_paths(
        self, svg_blocks: list[SvgBlock], base_path: str
    ) -> list[str]:
        """SVGファイルパスを絶対パスに解決する"""
        resolved_paths = []
        base_path_obj = Path(base_path)

        for block in svg_blocks:
            if not block.file_path:  # インラインSVGの場合
                resolved_paths.append("")
            else:
                file_path = Path(block.file_path)
                if file_path.is_absolute():
                    resolved_paths.append(str(file_path))
                else:
                    # 相対パスを絶対パスに変換
                    resolved_path = base_path_obj / file_path
                    resolved_paths.append(str(resolved_path.resolve()))

        return resolved_paths
