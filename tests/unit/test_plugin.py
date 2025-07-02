"""
SvgToPngPluginクラスのテスト
このファイルでは、プラグイン本体の動作を検証します。
"""

from unittest.mock import Mock, patch

import pytest

from mkdocs_svg_to_png.exceptions import SvgConfigError
from mkdocs_svg_to_png.plugin import SvgToPngPlugin


class TestSvgToPngPlugin:
    """SvgToPngPluginクラスのテストクラス"""

    @pytest.fixture
    def plugin(self):
        """テスト用のプラグインインスタンスを返すfixture"""
        return SvgToPngPlugin()

    @pytest.fixture
    def mock_config(self):
        """テスト用のモック設定を返すfixture"""
        config = Mock()
        config.__getitem__ = Mock(
            side_effect=lambda key: {
                "docs_dir": "/tmp/docs",
                "site_dir": "/tmp/site",
            }.get(key)
        )
        return config

    @pytest.fixture
    def mock_page(self):
        """テスト用のモックページを返すfixture"""
        page = Mock()
        page.file = Mock()
        page.file.src_path = "test.md"
        return page

    def test_plugin_initialization(self, plugin):
        """初期化時のプロパティが正しいかテスト"""
        assert plugin.processor is None
        assert plugin.generated_images == []

    def test_config_validation_success(self, plugin, mock_config):
        """有効な設定でon_configが成功するかテスト"""
        plugin.config = {
            "enabled": True,
            "output_dir": "assets/images",
            "image_format": "png",
            "dpi": 150,
            "quality": 90,
            "output_format": "png",
            "preserve_original": False,
            "error_on_fail": False,
            "log_level": "INFO",
        }

        with (
            patch("mkdocs_svg_to_png.plugin.SvgProcessor"),
            patch("mkdocs_svg_to_png.plugin.get_logger") as mock_logger,
        ):
            mock_logger.return_value = Mock()
            result = plugin.on_config(mock_config)
            assert result == mock_config
            assert plugin.processor is not None

    def test_config_validation_disabled_plugin(self, plugin, mock_config):
        """プラグインが無効な場合にprocessorがNoneになるかテスト"""
        plugin.config = {
            "enabled": False,
            "output_dir": "assets/images",
            "image_format": "png",
            "dpi": 150,
            "quality": 90,
            "output_format": "png",
            "preserve_original": False,
            "error_on_fail": False,
            "log_level": "INFO",
        }

        with patch("mkdocs_svg_to_png.plugin.get_logger") as mock_logger:
            mock_logger.return_value = Mock()
            result = plugin.on_config(mock_config)
            assert result == mock_config
            assert plugin.processor is None

    def test_config_validation_invalid_dpi(self, plugin, mock_config):
        """DPIが不正な場合に例外が発生するかテスト"""
        plugin.config = {
            "enabled": True,
            "dpi": -100,
            "quality": 90,
            "output_format": "png",
            "log_level": "INFO",
        }

        with pytest.raises(SvgConfigError):
            plugin.on_config(mock_config)

    def test_on_files_disabled(self, plugin):
        """プラグイン無効時のon_filesの挙動をテスト"""
        plugin.config = {"enabled": False}
        files = ["file1.md", "file2.md"]

        result = plugin.on_files(files, config={})
        assert result == files
        assert plugin.generated_images == []

    def test_on_files_enabled(self, plugin):
        """プラグイン有効時のon_filesの挙動をテスト"""
        plugin.config = {"enabled": True}
        plugin.processor = Mock()
        files = ["file1.md", "file2.md"]

        result = plugin.on_files(files, config={})
        assert result == files
        assert plugin.generated_images == []

    @patch("mkdocs_svg_to_png.plugin.SvgProcessor")
    def test_on_page_markdown_disabled(self, _mock_processor_class, plugin, mock_page):
        """プラグイン無効時は元のMarkdownが返るかテスト"""
        plugin.config = {"enabled": False}
        markdown = "# Test\n\nSome content"

        result = plugin.on_page_markdown(markdown, page=mock_page, config={}, files=[])
        assert result == markdown

    @patch("mkdocs_svg_to_png.plugin.SvgProcessor")
    def test_on_page_markdown_success(
        self, _mock_processor_class, plugin, mock_page, mock_config
    ):
        """ページ内にSVGブロックがある場合の処理をテスト"""
        plugin.config = {
            "enabled": True,
            "output_dir": "assets/images",
            "error_on_fail": False,
            "log_level": "INFO",
        }

        # processorをモック
        mock_processor = Mock()
        mock_processor.process_page.return_value = (
            "modified content",
            ["/path/to/image.png"],
        )
        plugin.processor = mock_processor

        markdown = "# Test\n\n```svg\n<svg></svg>\n```"

        result = plugin.on_page_markdown(
            markdown, page=mock_page, config=mock_config, files=[]
        )

        assert result == "modified content"
        assert plugin.generated_images == ["/path/to/image.png"]
        mock_processor.process_page.assert_called_once()
