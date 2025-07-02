__version__ = "1.0.0"

__author__ = "Claude Code Assistant"

__description__ = "MkDocs plugin to convert SVG files to PNG images"

from .mermaid_block import SvgBlock
from .plugin import SvgToPngPlugin

__all__ = ["SvgToPngPlugin", "SvgBlock"]
