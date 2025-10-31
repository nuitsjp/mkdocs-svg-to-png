from __future__ import annotations

from . import _version

# プラグインのメタ情報をモジュールレベルで公開しておく
__author__ = "Claude Code Assistant"

__description__ = "MkDocs plugin to convert SVG files to PNG images"

# 利用側が直接取り出す代表的なエントリポイントを読み込む
from .plugin import SvgToPngPlugin
from .svg_block import SvgBlock

# バージョン管理モジュールから公開用のバージョン番号を反映する
__version__ = _version.__version__

# MkDocs で参照される公開シンボルを明示的に列挙する
__all__ = ["SvgBlock", "SvgToPngPlugin"]
