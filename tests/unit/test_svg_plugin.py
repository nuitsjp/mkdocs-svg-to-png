"""
SvgToPngPluginクラスのテスト
SVG to PNG変換プラグインの基本動作を検証します。

TDD Red フェーズ: 新しいプラグインクラスのテスト
"""

from mkdocs_svg_to_png.plugin import SvgToPngPlugin


class TestSvgToPngPlugin:
    """SvgToPngPluginクラスのテストクラス"""

    def test_plugin_class_exists(self):
        """SvgToPngPluginクラスが存在することを確認"""
        plugin = SvgToPngPlugin()
        assert plugin is not None
        assert isinstance(plugin, SvgToPngPlugin)

    def test_plugin_has_config_scheme(self):
        """プラグインが設定スキーマを持つことを確認"""
        plugin = SvgToPngPlugin()
        assert hasattr(plugin, "config_scheme")
        assert plugin.config_scheme is not None

    def test_plugin_initialization_defaults(self):
        """プラグインの初期化時のデフォルト値を確認"""
        plugin = SvgToPngPlugin()
        assert plugin.processor is None
        assert plugin.generated_images == []
        assert plugin.files is None
        assert hasattr(plugin, "logger")
