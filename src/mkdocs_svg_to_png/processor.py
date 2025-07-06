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
    ) -> tuple[str, list[str]]:
        blocks = self.markdown_processor.extract_svg_blocks(markdown_content)

        if not blocks:
            return markdown_content, []

        image_paths = []
        successful_blocks = []

        for i, block in enumerate(blocks):
            try:
                image_filename = block.get_filename(
                    page_file, i, self.config["output_format"]
                )
                image_path = Path(output_dir) / image_filename

                success = block.generate_png(
                    str(image_path), self.svg_converter, self.config
                )

                if success:
                    image_paths.append(str(image_path))
                    successful_blocks.append(block)
                elif not self.config["error_on_fail"]:
                    self.logger.warning(
                        "PNG generation failed, keeping original SVG block",
                        extra={
                            "context": {
                                "page_file": page_file,
                                "block_index": i,
                                "image_path": str(image_path),
                                "suggestion": "Check SVG content and CairoSVG installation",  # noqa: E501
                            }
                        },
                    )
                    continue
                else:
                    raise SvgImageError(
                        f"PNG generation failed for block {i} in {page_file}",
                        image_path=str(image_path),
                        suggestion="Check SVG content and CairoSVG installation",
                    )

            except SvgConversionError:
                # カスタム例外はそのまま再発生
                raise
            except (FileNotFoundError, OSError, PermissionError) as e:
                error_msg = (
                    f"File system error processing block {i} in {page_file}: {e!s}"
                )
                self.logger.error(error_msg)
                if self.config["error_on_fail"]:
                    raise SvgFileError(
                        error_msg,
                        file_path=str(image_path),
                        operation="image_generation",
                        suggestion="Check file permissions and ensure output "
                        "directory exists",
                    ) from e
                continue
            except Exception as e:
                error_msg = (
                    f"Unexpected error processing block {i} in {page_file}: {e!s}"
                )
                self.logger.error(error_msg)
                if self.config["error_on_fail"]:
                    raise SvgConversionError(error_msg) from e
                continue

        if successful_blocks:
            modified_content = self.markdown_processor.replace_blocks_with_images(
                markdown_content, successful_blocks, image_paths, page_file, page_url
            )
            return modified_content, image_paths

        return markdown_content, []
