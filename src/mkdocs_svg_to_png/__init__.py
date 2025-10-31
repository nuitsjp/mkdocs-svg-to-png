from __future__ import annotations

from . import _version

__author__ = "Claude Code Assistant"

__description__ = "MkDocs plugin to convert SVG files to PNG images"

from .plugin import SvgToPngPlugin
from .svg_block import SvgBlock

__version__ = _version.__version__

__all__ = ["SvgBlock", "SvgToPngPlugin"]
