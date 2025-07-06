from pathlib import Path
from typing import Any, Union

from .exceptions import SvgConversionError, SvgFileError, SvgImageError
from .logging_config import get_logger
from .markdown_processor import MarkdownProcessor
from .svg_converter import SvgToPngConverter


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
        page_url: str = "",
        docs_dir: Union[str, Path, None] = None,
    ) -> tuple[str, list[str]]:
        blocks = self.markdown_processor.extract_svg_blocks(markdown_content)

        if not blocks:
            return markdown_content, []

        self._resolve_svg_file_paths(blocks, docs_dir)
        image_paths, successful_blocks = self._process_svg_blocks(
            blocks, page_file, output_dir
        )

        if successful_blocks:
            modified_content = self.markdown_processor.replace_blocks_with_images(
                markdown_content, successful_blocks, image_paths, page_file, page_url
            )
            return modified_content, image_paths

        return markdown_content, []

    def _resolve_svg_file_paths(
        self, blocks: list[Any], docs_dir: Union[str, Path, None]
    ) -> None:
        """SVGファイルパスを解決する"""
        if not docs_dir:
            return

        resolved_paths = self.markdown_processor.resolve_svg_file_paths(
            blocks, str(docs_dir)
        )
        # 解決されたパスをブロックに設定
        for block, resolved_path in zip(blocks, resolved_paths):
            if resolved_path and block.file_path:  # ファイル参照の場合のみ
                block.file_path = resolved_path

    def _process_svg_blocks(
        self, blocks: list[Any], page_file: str, output_dir: Union[str, Path]
    ) -> tuple[list[str], list[Any]]:
        """SVGブロックを処理してPNG画像を生成する"""
        image_paths: list[str] = []
        successful_blocks: list[Any] = []

        for i, block in enumerate(blocks):
            try:
                image_path = self._generate_image_path(block, page_file, i, output_dir)
                success = block.generate_png(
                    str(image_path), self.svg_converter, self.config
                )

                if success:
                    image_paths.append(str(image_path))
                    successful_blocks.append(block)
                elif not self.config["error_on_fail"]:
                    self._log_generation_failure(page_file, i, image_path)
                else:
                    self._raise_generation_error(page_file, i, image_path)

            except SvgConversionError:
                raise
            except (FileNotFoundError, OSError, PermissionError) as e:
                if not self._handle_file_error(e, page_file, i, image_path):
                    continue
            except Exception as e:
                if not self._handle_unexpected_error(e, page_file, i):
                    continue

        return image_paths, successful_blocks

    def _generate_image_path(
        self, block: Any, page_file: str, index: int, output_dir: Union[str, Path]
    ) -> Path:
        """画像パスを生成する"""
        image_filename = str(
            block.get_filename(page_file, index, self.config["output_format"])
        )
        return Path(str(output_dir)) / image_filename

    def _log_generation_failure(
        self, page_file: str, index: int, image_path: Path
    ) -> None:
        """PNG生成失敗をログに記録する"""
        self.logger.warning(
            "PNG generation failed, keeping original SVG block",
            extra={
                "context": {
                    "page_file": page_file,
                    "block_index": index,
                    "image_path": str(image_path),
                    "suggestion": "Check SVG content and CairoSVG installation",
                }
            },
        )

    def _raise_generation_error(
        self, page_file: str, index: int, image_path: Path
    ) -> None:
        """PNG生成エラーを発生させる"""
        raise SvgImageError(
            f"PNG generation failed for block {index} in {page_file}",
            image_path=str(image_path),
            suggestion="Check SVG content and CairoSVG installation",
        )

    def _handle_file_error(
        self, error: Exception, page_file: str, index: int, image_path: Path
    ) -> bool:
        """ファイルシステムエラーを処理する"""
        error_msg = (
            f"File system error processing block {index} in {page_file}: {error!s}"
        )
        self.logger.error(error_msg)
        if self.config["error_on_fail"]:
            raise SvgFileError(
                error_msg,
                file_path=str(image_path),
                operation="image_generation",
                suggestion="Check file permissions and ensure output "
                "directory exists",
            ) from error
        return False

    def _handle_unexpected_error(
        self, error: Exception, page_file: str, index: int
    ) -> bool:
        """予期しないエラーを処理する"""
        error_msg = (
            f"Unexpected error processing block {index} in {page_file}: {error!s}"
        )
        self.logger.error(error_msg)
        if self.config["error_on_fail"]:
            raise SvgConversionError(error_msg) from error
        return False
