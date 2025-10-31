from dataclasses import dataclass
from pathlib import Path
from typing import Any, Union

from .exceptions import SvgImageError
from .logging_config import get_logger
from .markdown_processor import MarkdownProcessor
from .svg_block import SvgBlock
from .svg_converter import SvgToPngConverter


@dataclass(slots=True)
class SvgBlockProcessingResult:
    block: SvgBlock
    image_path: str


class SvgProcessor:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.logger = get_logger(__name__)

        self.markdown_processor = MarkdownProcessor(config)
        self.svg_converter = SvgToPngConverter(config)

    def process_page(
        self,
        page_file: str,
        markdown_content: str,
        output_dir: Union[str, Path],
        docs_dir: Union[str, Path, None] = None,
    ) -> tuple[str, list[str]]:
        blocks = self.markdown_processor.extract_svg_blocks(markdown_content)

        if not blocks:
            return markdown_content, []

        self._resolve_svg_file_paths(blocks, docs_dir, page_file)
        results = self._process_svg_blocks(blocks, page_file, output_dir)

        if results:
            image_paths = [result.image_path for result in results]
            successful_blocks = [result.block for result in results]
            modified_content = self.markdown_processor.replace_blocks_with_images(
                markdown_content, successful_blocks, image_paths, page_file
            )
            return modified_content, image_paths

        return markdown_content, []

    def _resolve_svg_file_paths(
        self,
        blocks: list[SvgBlock],
        docs_dir: Union[str, Path, None],
        page_file: str = "",
    ) -> None:
        """SVGファイルパスを解決する"""
        if any(not isinstance(block, SvgBlock) for block in blocks):
            invalid_types = {
                type(block).__name__
                for block in blocks
                if not isinstance(block, SvgBlock)
            }
            types_str = ", ".join(sorted(invalid_types)) or "Unknown"
            raise TypeError(
                f"blocks must contain only SvgBlock instances, got: {types_str}"
            )

        if not docs_dir:
            return

        if page_file:
            # ページファイル基準の新しいパス解決メソッドを使用
            resolved_paths = self.markdown_processor.resolve_svg_file_paths_from_page(
                blocks, page_file, str(docs_dir)
            )
        else:
            # 従来の方法（後方互換性のため）
            resolved_paths = self.markdown_processor.resolve_svg_file_paths(
                blocks, str(docs_dir)
            )

        # 解決されたパスをブロックに設定
        for block, resolved_path in zip(blocks, resolved_paths):
            if resolved_path and block.file_path:  # ファイル参照の場合のみ
                block.file_path = resolved_path

    def _process_svg_blocks(
        self, blocks: list[SvgBlock], page_file: str, output_dir: Union[str, Path]
    ) -> list[SvgBlockProcessingResult]:
        """SVGブロックを処理してPNG画像を生成する"""
        results: list[SvgBlockProcessingResult] = []

        for i, block in enumerate(blocks):
            try:
                image_path = self._generate_image_path(block, page_file, i, output_dir)

                # 個別変換開始のログを出力
                image_filename = Path(image_path).name
                self.logger.info(
                    f"Converting SVG to PNG: {image_filename} from {page_file}"
                )

                success = block.generate_png(str(image_path), self.svg_converter)

                if success:
                    results.append(
                        SvgBlockProcessingResult(
                            block=block, image_path=str(image_path)
                        )
                    )
                elif self.config["error_on_fail"]:
                    raise SvgImageError(
                        f"PNG generation failed for block {i} in {page_file}",
                        image_path=str(image_path),
                        suggestion="Check SVG content and conversion setup",
                    )
                else:
                    self.logger.warning(
                        f"PNG generation failed for block {i} in {page_file}, "
                        f"keeping original SVG"
                    )

            except Exception as e:
                if self.config["error_on_fail"]:
                    raise
                self.logger.error(f"Error processing block {i} in {page_file}: {e}")

        return results

    def _generate_image_path(
        self, block: Any, page_file: str, index: int, output_dir: Union[str, Path]
    ) -> Path:
        """画像パスを生成する"""
        image_filename = str(block.get_filename(page_file, index, "png"))
        return Path(str(output_dir)) / image_filename
