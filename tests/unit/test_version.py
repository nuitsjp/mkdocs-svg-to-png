"""Tests for version module."""

from __future__ import annotations


def test_version_imports() -> None:
    """Test that version module imports work correctly."""
    from mkdocs_svg_to_png import __version__

    # Test that version attribute exists and is a string
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_version_matches_generated_version() -> None:
    """__version__ should mirror setuptools-scm generated value."""
    from mkdocs_svg_to_png import __version__, _version

    assert __version__ == _version.__version__
