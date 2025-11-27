"""
SvgToPngPluginクラスのテスト
このファイルでは、プラグイン本体の動作を検証します。
"""

import logging
from unittest.mock import Mock, patch

import pytest

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

    def test_on_config_detects_serve_mode_from_watch(self, plugin):
        """watch設定がある場合に配信モードと判断するかテスト (TDD RED)"""
        plugin.config = {
            "enabled": True,
            "output_dir": "assets/images",
            "error_on_fail": False,
            "log_level": "INFO",
        }
        mkdocs_config = {
            "docs_dir": "/tmp/docs",
            "site_dir": "/tmp/site",
            "watch": {"docs", "mkdocs.yml"},
        }

        with (
            patch("mkdocs_svg_to_png.plugin.SvgProcessor") as mock_processor,
            patch("mkdocs_svg_to_png.plugin.setup_plugin_logging"),
        ):
            mock_processor.return_value = Mock()
            plugin.on_config(mkdocs_config)

        assert plugin.is_serve_mode is True

    def test_on_serve_sets_serve_mode_flag(self, plugin):
        """on_serve呼び出し時に配信モードフラグが立つかテスト (TDD RED)"""
        plugin.is_serve_mode = False
        server = Mock()

        plugin.on_serve(server, config={}, builder=Mock())

        assert plugin.is_serve_mode is True

    def test_plugin_enabled_state_is_fixed_after_config(
        self, plugin, mock_page, mock_config, monkeypatch
    ):
        """環境変数が後から変わっても初期化時の有効状態を維持するかテスト (TDD RED)"""
        env_var = "ENABLE_SVG_TO_PNG"
        plugin.config = {
            "enabled_if_env": env_var,
            "output_dir": "assets/images",
            "error_on_fail": False,
            "log_level": "INFO",
        }

        monkeypatch.setenv(env_var, "1")

        mock_processor = Mock()
        with (
            patch("mkdocs_svg_to_png.plugin.SvgProcessor", return_value=mock_processor),
            patch("mkdocs_svg_to_png.plugin.setup_plugin_logging"),
        ):
            plugin.on_config(mock_config)

        # 初期化後に環境変数を変更しても有効状態が揺らがないことを確認したい
        monkeypatch.delenv(env_var, raising=False)

        mock_processor.process_page.return_value = ("updated", ["/tmp/image.png"])

        result = plugin.on_page_markdown(
            "# Test", page=mock_page, config=mock_config, files=[]
        )

        assert result == "updated"
        mock_processor.process_page.assert_called_once()

    def test_config_validation_disabled_plugin(self, plugin, mock_config):
        """プラグインが無効な場合にprocessorがNoneになるかテスト"""
        plugin.config = {
            "enabled_if_env": "NONEXISTENT_ENV",
            "output_dir": "assets/images",
            "image_format": "png",
            "preserve_original": False,
            "error_on_fail": False,
            "log_level": "INFO",
        }

        with patch("mkdocs_svg_to_png.plugin.get_logger") as mock_logger:
            mock_logger.return_value = Mock()
            result = plugin.on_config(mock_config)
            assert result == mock_config
            assert plugin.processor is None

    def test_on_config_forces_debug_when_root_logger_debug(self, plugin, mock_config):
        """ルートロガーがDEBUGのときlog_levelがDEBUGに強制されるかテスト (TDD RED)"""
        plugin.config = {
            "enabled": True,
            "output_dir": "assets/images",
            "error_on_fail": False,
            "log_level": "INFO",
        }

        root_logger = logging.getLogger()
        previous_level = root_logger.level
        root_logger.setLevel(logging.DEBUG)

        try:
            with (
                patch("mkdocs_svg_to_png.plugin.SvgProcessor") as mock_processor,
                patch("mkdocs_svg_to_png.plugin.setup_plugin_logging"),
            ):
                plugin.on_config(mock_config)
        finally:
            root_logger.setLevel(previous_level)

        called_config = mock_processor.call_args.args[0]
        assert called_config["log_level"] == "DEBUG"

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

    def test_plugin_initialization_log_message(self, plugin, mock_config):
        """プラグイン初期化ログメッセージが新形式であることをテスト (TDD RED)"""
        plugin.config = {
            "enabled": True,
            "output_dir": "assets/images",
            "image_format": "png",
            "preserve_original": False,
            "error_on_fail": False,
            "log_level": "INFO",
        }

        # プラグインのloggerを直接モック
        mock_logger_instance = Mock()
        plugin.logger = mock_logger_instance

        with patch("mkdocs_svg_to_png.plugin.SvgProcessor"):
            plugin.on_config(mock_config)

            # 新しい簡潔な形式でログが出力されることを期待
            mock_logger_instance.info.assert_called_with(
                "svg-to-png plugin initialized"
            )

    def test_page_processing_log_message(self, plugin, mock_page, mock_config):
        """ページ処理ログメッセージが新形式であることをテスト (TDD RED)"""
        plugin.config = {
            "enabled": True,
            "output_dir": "assets/images",
            "error_on_fail": False,
            "log_level": "INFO",
        }

        # processorとloggerをモック
        mock_processor = Mock()
        mock_processor.process_page.return_value = (
            "modified content",
            ["/path/to/image1.png", "/path/to/image2.png"],
        )
        plugin.processor = mock_processor

        with patch("mkdocs_svg_to_png.plugin.get_logger") as mock_logger:
            mock_logger_instance = Mock()
            mock_logger.return_value = mock_logger_instance
            plugin.logger = mock_logger_instance

            markdown = "# Test\n\n```svg\n<svg></svg>\n```"
            plugin.on_page_markdown(
                markdown, page=mock_page, config=mock_config, files=[]
            )

            # 新しい簡潔な形式でログが出力されることを期待
            mock_logger_instance.info.assert_called_with(
                "Generated 2 images from SVG for test.md"
            )

    def test_post_build_total_log_message(self, plugin, mock_config):
        """ビルド完了後の総数ログメッセージが新形式であることをテスト (TDD RED)"""
        plugin.config = {"enabled": True}
        plugin.generated_images = [
            "/path/to/image1.png",
            "/path/to/image2.png",
            "/path/to/image3.png",
        ]

        with patch("mkdocs_svg_to_png.plugin.get_logger") as mock_logger:
            mock_logger_instance = Mock()
            mock_logger.return_value = mock_logger_instance
            plugin.logger = mock_logger_instance

            plugin.on_post_build(config=mock_config)

            # 新しい簡潔な形式でログが出力されることを期待
            mock_logger_instance.info.assert_called_with(
                "Generated 3 images from SVG total"
            )
