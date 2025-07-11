from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, TypedDict

if TYPE_CHECKING:
    from collections.abc import Mapping

PluginStatus = Literal["success", "error", "pending"]
ValidationStatus = Literal["valid", "invalid", "skipped"]
ProcessingStatus = Literal["processing", "completed", "failed"]

ImageFormat = Literal["png", "svg"]


class PluginConfigDict(TypedDict, total=False):
    output_dir: str
    image_format: ImageFormat
    preserve_original: bool
    error_on_fail: bool
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]
    cleanup_generated_images: bool
    enabled_if_env: str


class SvgBlockDict(TypedDict):
    code: str
    file_path: str
    start_pos: int
    end_pos: int
    attributes: dict[str, Any]


class SvgBlockWithMetadata(SvgBlockDict):
    image_filename: str
    image_path: str
    processed: bool
    processing_status: ProcessingStatus


class ProcessingResultDict(TypedDict):
    status: PluginStatus
    processed_blocks: list[SvgBlockWithMetadata]
    errors: list[str]
    warnings: list[str]
    processing_time_ms: float


class ValidationResultDict(TypedDict):
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    validation_status: ValidationStatus


class ImageGenerationResult(TypedDict):
    success: bool
    image_path: str
    error_message: str | None
    generation_time_ms: float


class ErrorInfo(TypedDict):
    code: str
    message: str
    details: Mapping[str, str | int | None]
    source_file: str | None
    line_number: int | None


class LogContext(TypedDict, total=False):
    page_file: str | None
    block_index: int | None
    image_format: ImageFormat | None
    processing_step: str | None
    execution_time_ms: float | None
    error_type: str | None


CommandResult = tuple[int, str, str]

FileOperation = Literal["read", "write", "create", "delete"]

PluginHook = Literal["on_config", "on_page_markdown", "on_post_build"]


class ProcessingStats(TypedDict):
    total_blocks: int
    processed_blocks: int
    failed_blocks: int
    total_processing_time_ms: float
    average_processing_time_ms: float
