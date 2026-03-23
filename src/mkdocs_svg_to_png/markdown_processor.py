import posixpath
import re
from bisect import bisect_right
from pathlib import Path, PurePosixPath
from typing import Any

from .exceptions import SvgParsingError
from .logging_config import get_logger
from .svg_block import SvgBlock


class MarkdownProcessor:
    """Markdown 内の SVG コードやファイル参照を処理するコンバーター。"""

    def __init__(self, config: dict[str, Any]) -> None:
        """プラグイン設定を受け取り、ロガーを初期化する。"""
        self.config = config
        self.logger = get_logger(__name__)

    def _parse_attributes(self, attr_str: str) -> dict[str, Any]:
        """SVG コードブロックに付与された属性文字列を辞書へ変換する。"""
        attributes = {}
        if attr_str:
            # カンマ区切りの key:value を順に取り出し正規化する
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
        blocks: list[SvgBlock],
        image_paths: list[str],
        page_file: str,
    ) -> str:
        """検出した SVG ブロックを対応する画像マークダウンに差し替える。"""
        if len(blocks) != len(image_paths):
            # 画像生成結果とブロック数が合わない場合はパース失敗として扱う
            raise SvgParsingError(
                "Number of blocks and image paths must match",
                source_file=page_file,
                svg_content=f"Expected {len(blocks)} images, got {len(image_paths)}",
            )

        # 後方から置換するため開始位置の降順で並び替える
        sorted_blocks = sorted(
            zip(blocks, image_paths), key=lambda x: x[0].start_pos, reverse=True
        )

        result = markdown_content

        for block, image_path in sorted_blocks:
            # 各ブロックを変換ポリシーに従って画像マークダウンへ変形する
            image_markdown = block.get_image_markdown(
                image_path,
                page_file,
                self.config.get("preserve_original", False),
                self.config.get("output_dir", "assets/images"),
            )

            result = (
                result[: block.start_pos] + image_markdown + result[block.end_pos :]
            )

        return result

    def extract_svg_blocks(self, markdown_content: str) -> list[SvgBlock]:
        """SVGファイル参照とインラインSVGコードブロックを抽出する"""
        # SVGファイル参照パターン: ![alt](path.svg)
        file_pattern = r"!\[[^\]]*\]\(((?!https?://)[^)]+\.svg)\)"

        blocks, fenced_ranges = self._extract_svg_blocks_from_fences(markdown_content)
        fenced_ranges, fenced_range_starts = self._build_range_index(fenced_ranges)

        for match in re.finditer(file_pattern, markdown_content):
            if self._is_position_in_ranges(
                match.start(), fenced_ranges, fenced_range_starts
            ):
                continue
            file_path = match.group(1)
            blocks.append(
                SvgBlock(
                    file_path=file_path,
                    start_pos=match.start(),
                    end_pos=match.end(),
                )
            )

        blocks.sort(key=lambda x: x.start_pos)

        self.logger.info(f"Found {len(blocks)} SVG blocks")
        return blocks

    def _extract_svg_blocks_from_fences(
        self, markdown_content: str
    ) -> tuple[list[SvgBlock], list[tuple[int, int]]]:
        fence_pattern = re.compile(
            r"^(?P<indent>[ \t]{0,3})(?P<fence>`{3,}|~{3,})(?P<info>[^\n]*)$",
            re.MULTILINE,
        )

        blocks: list[SvgBlock] = []
        fenced_ranges: list[tuple[int, int]] = []

        in_fence = False
        open_fence_char = ""
        open_fence_len = 0
        fence_block_start = 0

        in_svg = False
        svg_start = 0
        svg_content_start = 0
        svg_attributes: dict[str, Any] = {}

        for match in fence_pattern.finditer(markdown_content):
            fence = match.group("fence")
            info = match.group("info") or ""
            info_stripped = info.strip()
            fence_char = fence[0]

            if not in_fence:
                if fence_char == "`" and "`" in info:
                    continue

                attributes = self._parse_svg_info(info_stripped)
                in_svg = attributes is not None
                svg_attributes = attributes or {}

                in_fence = True
                open_fence_char = fence_char
                open_fence_len = len(fence)
                fence_block_start = match.start()

                if in_svg:
                    svg_start = fence_block_start
                    svg_content_start = self._advance_past_newline(
                        markdown_content, match.end()
                    )
                continue

            if not self._is_closing_fence(
                fence, info_stripped, open_fence_char, open_fence_len
            ):
                continue

            fenced_ranges.append((fence_block_start, match.end()))

            if in_svg:
                code = markdown_content[svg_content_start : match.start()].strip()
                blocks.append(
                    SvgBlock(
                        code=code,
                        start_pos=svg_start,
                        end_pos=match.end(),
                        attributes=svg_attributes,
                    )
                )

            in_fence = False
            in_svg = False
            open_fence_char = ""
            open_fence_len = 0
            fence_block_start = 0
            svg_start = 0
            svg_content_start = 0
            svg_attributes = {}

        if in_fence:
            fenced_ranges.append((fence_block_start, len(markdown_content)))

        return blocks, fenced_ranges

    def _build_range_index(
        self, ranges: list[tuple[int, int]]
    ) -> tuple[list[tuple[int, int]], list[int]]:
        sorted_ranges = sorted(ranges, key=lambda r: r[0])
        starts = [start for start, _ in sorted_ranges]
        return sorted_ranges, starts

    def _is_position_in_ranges(
        self,
        pos: int,
        ranges: list[tuple[int, int]],
        starts: list[int],
    ) -> bool:
        if not ranges:
            return False
        idx = bisect_right(starts, pos) - 1
        if idx < 0:
            return False
        start, end = ranges[idx]
        return start <= pos < end

    def _parse_svg_info(self, info_str: str) -> dict[str, Any] | None:
        if not info_str.startswith("svg"):
            return None

        rest = info_str[len("svg") :]
        if rest and not rest[0].isspace() and not rest.startswith("{"):
            return None

        attr_match = re.search(r"\{([^}]*)\}", rest)
        if attr_match:
            return self._parse_attributes(attr_match.group(1).strip())
        return {}

    def _advance_past_newline(self, text: str, pos: int) -> int:
        if text.startswith("\r\n", pos):
            return pos + 2
        if pos < len(text) and text[pos] == "\n":
            return pos + 1
        return pos

    def _is_closing_fence(
        self, fence: str, info_str: str, fence_char: str, fence_len: int
    ) -> bool:
        return fence[0] == fence_char and len(fence) >= fence_len and info_str == ""

    def _create_svg_block(self, code: str, file_path: str) -> SvgBlock:
        """SVGブロックを作成するヘルパーメソッド（テスト用）"""
        return SvgBlock(code=code, file_path=file_path)

    def resolve_svg_file_paths(
        self, svg_blocks: list[SvgBlock], base_path: str
    ) -> list[str]:
        """SVGファイルパスを絶対パスに解決する（従来の方法）"""
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
                    # 相対パスをプロジェクト基準の絶対パスへ変換する
                    resolved_path = base_path_obj / file_path
                    resolved_paths.append(str(resolved_path.resolve()))

        return resolved_paths

    def resolve_svg_file_paths_from_page(
        self, svg_blocks: list[SvgBlock], page_file: str, docs_dir: str
    ) -> list[str]:
        """ページファイルの位置を基準にしてSVGファイルパスを絶対パスに解決する"""
        resolved_paths: list[str] = []

        # docs_dir はテストで POSIX 形式('/home/ubuntu/...') を前提としているため、
        # ファイルシステムに触れない PurePosixPath と posixpath.normpath で解決する。
        docs_dir_posix = docs_dir.replace("\\", "/").rstrip("/")
        page_parent = PurePosixPath(page_file.replace("\\", "/")).parent
        page_base = PurePosixPath(docs_dir_posix) / page_parent

        for block in svg_blocks:
            if not block.file_path:  # インラインSVGの場合は空文字
                resolved_paths.append("")
                continue

            original = block.file_path.replace("\\", "/")

            # 先頭が '/' なら（Linux 風の絶対パスとして）そのまま返す
            if original.startswith("/"):
                resolved_paths.append(original)
                continue

            # Windows ドライブレター形式 (例: C:/path/to/file.svg) はそのまま返す
            if re.match(r"^[A-Za-z]:/", original):
                resolved_paths.append(original)
                continue

            # ページファイルのディレクトリを基準に相対パスを解決する（../ 含む）
            # PurePosixPath は .. を畳まないため、POSIX 文字列として normpath する
            combined = (page_base / original).as_posix()
            resolved_paths.append(posixpath.normpath(combined))

        return resolved_paths
