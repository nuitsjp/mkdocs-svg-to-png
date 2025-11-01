"""プラグインで共有する設定・ログコンテキストの型定義。"""

from __future__ import annotations

from typing import Literal, TypedDict


class PluginConfigDict(TypedDict, total=False):
    """設定ファイルや runtime から受け取るプラグイン設定の型。"""

    output_dir: str
    image_format: Literal["png", "svg"]
    preserve_original: bool
    error_on_fail: bool
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]
    cleanup_generated_images: bool
    enabled_if_env: str


class LogContext(TypedDict, total=False):
    """ログ出力時に付随させる追加情報の型。"""

    page_file: str | None
    block_index: int | None
    image_format: Literal["png", "svg"] | None
    processing_step: str | None
    execution_time_ms: float | None
    error_type: str | None
