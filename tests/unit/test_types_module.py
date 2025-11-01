from importlib import import_module

import pytest


@pytest.mark.parametrize(
    "unused_name",
    [
        "PluginStatus",
        "ValidationStatus",
        "ProcessingStatus",
        "ImageFormat",
        "SvgBlockDict",
        "SvgBlockWithMetadata",
        "ProcessingResultDict",
        "ValidationResultDict",
        "ImageGenerationResult",
        "ErrorInfo",
        "PluginHook",
        "ProcessingStats",
        "CommandResult",
    ],
)
def test_types_module_does_not_expose_unused_symbols(unused_name: str) -> None:
    types_module = import_module("mkdocs_svg_to_png.types")

    assert not hasattr(types_module, unused_name)
