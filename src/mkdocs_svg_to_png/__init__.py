__version__ = "1.0.0"

__author__ = "Claude Code Assistant"

__description__ = "MkDocs plugin to convert SVG files to PNG images"

from .plugin import SvgToPngPlugin
from .svg_block import SvgBlock

__all__ = ["SvgBlock", "SvgToPngPlugin"]
