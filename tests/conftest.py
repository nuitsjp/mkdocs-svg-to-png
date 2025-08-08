"""
共通テストフィクスチャとユーティリティ

このファイルは、テストファイル間で共有される共通のフィクスチャを定義します。
重複したモック設定を削減し、テストコードの保守性を向上させることが目的です。
"""

from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_svg_block():
    """SvgBlockのモックを返すフィクスチャ"""
    mock_block = Mock()
    mock_block.get_filename.return_value = "test_0_abc123.png"
    mock_block.generate_png.return_value = True
    mock_block.get_image_markdown.return_value = "![SVG Diagram](test_0_abc123.png)"
    mock_block.index = 0
    mock_block.code = "<svg></svg>"
    mock_block.file_path = ""
    return mock_block


@pytest.fixture
def mock_failed_svg_block():
    """画像生成に失敗するSvgBlockのモック"""
    mock_block = Mock()
    mock_block.get_filename.return_value = "test_0_abc123.png"
    mock_block.generate_png.return_value = False
    mock_block.get_image_markdown.return_value = "![SVG Diagram](test_0_abc123.png)"
    mock_block.index = 0
    mock_block.code = "<svg></svg>"
    mock_block.file_path = ""
    return mock_block


@pytest.fixture
def mock_config():
    """MkDocsの設定オブジェクトのモック"""
    config = Mock()
    config.__getitem__ = Mock(
        side_effect=lambda key: {
            "docs_dir": "/tmp/docs",
            "site_dir": "/tmp/site",
        }.get(key)
    )
    return config


@pytest.fixture
def mock_page():
    """MkDocsのPageオブジェクトのモック"""
    page = Mock()
    page.file = Mock()
    page.file.src_path = "test.md"
    page.file.dest_path = "test.html"
    page.title = "Test Page"
    return page


@pytest.fixture
def mock_logger():
    """ロガーオブジェクトのモック"""
    logger = Mock()
    return logger


@pytest.fixture
def mock_command_available():
    """コマンド利用可能性チェックのモック（利用可能）"""
    with patch("mkdocs_svg_to_png.image_generator.is_command_available") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_command_unavailable():
    """コマンド利用可能性チェックのモック（利用不可）"""
    with patch("mkdocs_svg_to_png.image_generator.is_command_available") as mock:
        mock.return_value = False
        yield mock


@pytest.fixture
def mock_subprocess_success():
    """サブプロセス実行成功のモック"""
    with patch("subprocess.run") as mock:
        mock.return_value = Mock(returncode=0, stderr="")
        yield mock


@pytest.fixture
def mock_subprocess_failure():
    """サブプロセス実行失敗のモック"""
    with patch("subprocess.run") as mock:
        mock.return_value = Mock(returncode=1, stderr="Error: Invalid syntax")
        yield mock


@pytest.fixture
def mock_file_operations():
    """ファイル操作のモック（存在するファイル用）"""
    mocks = {}
    with (
        patch("pathlib.Path.exists") as mock_exists,
        patch("pathlib.Path.unlink") as mock_unlink,
    ):
        mock_exists.return_value = True
        mocks["exists"] = mock_exists
        mocks["unlink"] = mock_unlink
        yield mocks


@pytest.fixture
def mock_file_not_exists():
    """ファイル操作のモック（存在しないファイル用）"""
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.return_value = False
        yield mock_exists


@pytest.fixture
def mock_temp_file():
    """一時ファイル操作のモック"""
    with (
        patch("mkdocs_svg_to_png.utils.get_temp_file_path") as mock_temp_path,
        patch("mkdocs_svg_to_png.utils.clean_temp_file") as mock_clean,
    ):
        mock_temp_path.return_value = "/tmp/test.mmd"
        yield {"temp_path": mock_temp_path, "clean": mock_clean}


@pytest.fixture
def svg_config():
    """SVG処理用の基本設定"""
    return {
        "output_dir": "assets/images",
        "scale": 1.0,
        "device_scale_factor": 1.0,
        "default_width": 800,
        "default_height": 600,
        "preserve_original": False,
        "error_on_fail": False,
        "log_level": "INFO",
        "dpi": 150,
        "quality": 90,
    }


@pytest.fixture
def sample_svg_content():
    """テスト用のサンプルSVGコンテンツ"""
    return """# Test Document

```svg
<svg width="100" height="100">
  <circle cx="50" cy="50" r="40" fill="red" />
</svg>
```

Some text.

![An SVG](image.svg)
"""


@pytest.fixture
def sample_svg_code():
    """サンプルSVGコード"""
    return (
        '<svg width="100" height="100">'
        '<circle cx="50" cy="50" r="40" fill="red" />'
        "</svg>"
    )


@pytest.fixture
def mock_ci_environment():
    """CI環境のモック"""
    with patch("os.getenv") as mock_getenv:
        mock_getenv.side_effect = lambda key: {
            "CI": "true",
            "GITHUB_ACTIONS": "true",
        }.get(key)
        yield mock_getenv
    with patch("os.getenv") as mock_getenv:
        mock_getenv.return_value = None
        yield mock_getenv
