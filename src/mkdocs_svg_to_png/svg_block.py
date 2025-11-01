from pathlib import Path, PurePosixPath
from typing import Any

from .utils import generate_image_filename


def _calculate_relative_path_prefix(page_file: str) -> str:
    """ページファイルパスから適切な相対パスプレフィックスを計算する。

    引数:
        page_file: ページファイルのパス（例: "appendix/mkdocs-architecture.md"）

    戻り値:
        相対パスプレフィックス（例: "../" や "../../../"）
    """
    if not page_file:
        return ""

    page_path = Path(page_file)
    # ディレクトリの深さを計算（ファイル名を除く）
    depth = len(page_path.parent.parts)

    # ルートレベル（深さ0）の場合は相対パス不要
    if depth == 0:
        return ""
    else:
        # 各階層に対して "../" を追加
        return "../" * depth


class SvgBlock:
    """Markdown から抽出した SVG ブロックを表現し、変換ユーティリティを提供する。"""

    def __init__(
        self,
        code: str = "",
        file_path: str = "",
        start_pos: int = 0,
        end_pos: int = 0,
        attributes: dict[str, Any] | None = None,
    ):
        """ブロック内容と位置情報、付与属性を保持する。"""
        self.code = code.strip()
        self.file_path = file_path
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.attributes = attributes or {}

    def __repr__(self) -> str:
        if self.file_path:
            return (
                f"SvgBlock(file_path='{self.file_path}', "
                f"start={self.start_pos}, end={self.end_pos})"
            )
        else:
            return (
                f"SvgBlock(code='{self.code[:50]}...', "
                f"start={self.start_pos}, end={self.end_pos})"
            )

    def generate_png(self, output_path: str, svg_converter: Any) -> bool:
        """保持している SVG 情報から PNG 変換を実行する。"""
        if self.file_path:
            # SVGファイルから変換
            result = svg_converter.convert_svg_file(self.file_path, output_path)
        else:
            # インラインSVGコードから変換
            result = svg_converter.convert_svg_content(self.code, output_path)
        return bool(result)

    def get_image_markdown(
        self,
        image_path: str,
        page_file: str,
        preserve_original: bool = False,
        output_dir: str | Path | None = None,
    ) -> str:
        """変換結果の PNG を指す Markdown 記法を生成する。"""
        relative_image_subpath = _build_relative_image_subpath(image_path, output_dir)

        # 相対パスプレフィックスを計算
        relative_prefix = _calculate_relative_path_prefix(page_file)

        # 相対パス付きで画像パスを構築
        relative_image_path = f"{relative_prefix}{relative_image_subpath}"

        image_markdown = f"![SVG Diagram]({relative_image_path})"

        if preserve_original:
            if self.file_path:
                # ファイル参照の場合
                if self.attributes:
                    attr_str = ", ".join(
                        f"{k}: {v}" for k, v in self.attributes.items()
                    )
                    original_block = f"![SVG File]({self.file_path}) {{{attr_str}}}"
                else:
                    original_block = f"![SVG File]({self.file_path})"
            elif self.attributes:
                attr_str = ", ".join(f"{k}: {v}" for k, v in self.attributes.items())
                original_block = f"```svg {{{attr_str}}}\n{self.code}\n```"
            else:
                original_block = f"```svg\n{self.code}\n```"

            image_markdown = f"{image_markdown}\n\n{original_block}"

        return image_markdown

    def get_filename(self, page_file: str, index: int, image_format: str) -> str:
        """ページ情報とブロック内容を基に安定した画像ファイル名を生成する。"""
        content = self.file_path if self.file_path else self.code
        return generate_image_filename(page_file, index, content, image_format)


def _build_relative_image_subpath(
    image_path: str, output_dir: str | Path | None
) -> str:
    """生成画像と出力ディレクトリから、ページ基準の相対参照パスを組み立てる。"""
    image_path_obj = Path(image_path)
    image_path_posix = PurePosixPath(str(image_path_obj).replace("\\", "/"))
    output_dir_str = str(output_dir) if output_dir else "assets/images"
    output_dir_posix = PurePosixPath(output_dir_str.replace("\\", "/"))

    output_dir_parts = tuple(
        part for part in output_dir_posix.parts if part not in ("", ".")
    )
    image_parts = tuple(
        part for part in image_path_posix.parts if part not in ("", ".")
    )

    if output_dir_parts:
        match_length = len(output_dir_parts)
        for idx in range(len(image_parts) - match_length, -1, -1):
            if image_parts[idx : idx + match_length] == output_dir_parts:
                return "/".join(image_parts[idx:])

        return "/".join((*output_dir_parts, image_path_obj.name))

    if image_parts:
        return "/".join(image_parts)

    return image_path_obj.name
