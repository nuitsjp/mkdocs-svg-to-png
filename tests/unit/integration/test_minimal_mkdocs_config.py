"""Integration test for minimal mkdocs.yml configuration."""

import tempfile
from unittest.mock import patch


class TestMinimalMkDocsConfig:
    """Test plugin functionality with minimal mkdocs.yml configuration."""

    def test_最小構成mkdocs_yml_でプラグイン動作(self):
        """plugins: [svg-to-png] だけの設定でプラグインが動作することを確認。"""
        from mkdocs_svg_to_png.plugin import SvgToPngPlugin

        # プラグインインスタンスを作成
        plugin = SvgToPngPlugin()

        # プラグインconfig にデフォルト値が設定されることをシミュレート
        # これは実際にはMkDocsが config_scheme を元に自動設定する
        plugin.config = {}
        for config_name, config_option in plugin.config_scheme:
            if hasattr(config_option, "default"):
                plugin.config[config_name] = config_option.default

        # 必須設定項目がデフォルト値で設定されていることを確認
        assert plugin.config["enabled"] is True
        assert plugin.config["output_dir"] == "assets/images"
        assert plugin.config["dpi"] == 300
        assert plugin.config["output_format"] == "png"
        assert plugin.config["quality"] == 95
        assert plugin.config["background_color"] == "transparent"
        assert plugin.config["cache_enabled"] is True
        assert plugin.config["cache_dir"] == ".svg_cache"
        assert plugin.config["preserve_original"] is False
        assert plugin.config["error_on_fail"] is False
        assert plugin.config["log_level"] == "INFO"

        # オプショナル設定項目はNoneになっていることを確認
        assert plugin.config["enabled_if_env"] is None
        assert plugin.config["temp_dir"] is None

    def test_最小構成でon_config_が成功する(self):
        """最小構成でon_configフックが成功することを確認。"""
        from mkdocs_svg_to_png.plugin import SvgToPngPlugin

        plugin = SvgToPngPlugin()

        # デフォルト設定を適用
        plugin.config = {}
        for config_name, config_option in plugin.config_scheme:
            if hasattr(config_option, "default"):
                plugin.config[config_name] = config_option.default

        # mock config
        mock_mkdocs_config = {
            "docs_dir": "/tmp/docs",
            "site_dir": "/tmp/site",
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            mock_mkdocs_config["docs_dir"] = temp_dir

            # プロセッサ初期化をモック
            with (
                patch("mkdocs_svg_to_png.plugin.SvgProcessor"),
                patch("mkdocs_svg_to_png.plugin.get_logger"),
            ):
                # on_config が正常に実行されることを確認
                result = plugin.on_config(mock_mkdocs_config)

                # 設定が返されることを確認
                assert result is not None

    def test_デフォルト値でconfig_validation_が通過する(self):
        """デフォルト値で設定検証が通過することを確認。"""
        from mkdocs_svg_to_png.config import SvgConfigManager
        from mkdocs_svg_to_png.plugin import SvgToPngPlugin

        plugin = SvgToPngPlugin()

        # デフォルト設定を適用
        plugin.config = {}
        for config_name, config_option in plugin.config_scheme:
            if hasattr(config_option, "default"):
                plugin.config[config_name] = config_option.default

        # 設定検証が通過することを確認
        result = SvgConfigManager().validate(dict(plugin.config))
        assert result == dict(plugin.config)

    def test_最小構成yaml_パース(self):
        """最小構成のYAMLが正しくパースされることを確認。"""
        import yaml

        # 最小構成のmkdocs.yml内容
        minimal_yaml = """
plugins:
  - svg-to-png
"""

        # YAMLがパースできることを確認
        config_data = yaml.safe_load(minimal_yaml)
        assert "plugins" in config_data
        assert "svg-to-png" in config_data["plugins"]

        # より具体的な形式もテスト
        detailed_minimal_yaml = """
plugins:
  - svg-to-png: {}
"""

        config_data2 = yaml.safe_load(detailed_minimal_yaml)
        assert "plugins" in config_data2
        assert config_data2["plugins"][0]["svg-to-png"] == {}

    def test_全てのオプションにデフォルト値またはオプショナル設定(self):
        """全ての設定項目がデフォルト値を持つかオプショナル設定であることを確認。"""
        from mkdocs_svg_to_png.plugin import SvgToPngPlugin

        plugin = SvgToPngPlugin()

        missing_defaults = []

        for config_name, config_option in plugin.config_scheme:
            # Optionalな設定はdefaultを持たない場合があるため、hasattrでチェック
            if (
                not hasattr(config_option, "default")
                and str(type(config_option)).find("Optional") == -1
            ):
                missing_defaults.append(config_name)

        # 全ての設定項目がデフォルト値を持つかオプショナル設定であることを確認
        assert len(missing_defaults) == 0, (
            f"These config options lack default values or are not optional: "
            f"{missing_defaults}"
        )
