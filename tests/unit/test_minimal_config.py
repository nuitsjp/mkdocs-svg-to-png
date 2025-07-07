"""Test minimal configuration functionality."""

from mkdocs_svg_to_png.config import SvgConfigManager
from mkdocs_svg_to_png.plugin import SvgToPngPlugin


class TestMinimalConfig:
    """Test plugin behavior with minimal configuration."""

    def test_最小構成での初期化成功(self):
        """プラグインが最小構成で初期化できることを確認。"""
        plugin = SvgToPngPlugin()

        # MkDocsのconfig_optionsを使って設定を検証
        # 実際の設定値がデフォルト値で補完されることを確認
        for config_name, config_option in plugin.config_scheme:
            if hasattr(config_option, "default"):
                # デフォルト値が設定されている
                assert config_option.default is not None or config_name in [
                    "enabled_if_env",
                ], f"{config_name} should have a default value"

    def test_enabled_if_env_がオプショナル設定である(self):
        """enabled_if_env オプションがオプショナル設定であることを確認。"""
        plugin = SvgToPngPlugin()

        # enabled_if_env設定を確認
        enabled_if_env_config = None
        for config_name, config_option in plugin.config_scheme:
            if config_name == "enabled_if_env":
                enabled_if_env_config = config_option
                break

        assert enabled_if_env_config is not None
        # Optional設定であることを確認
        assert str(type(enabled_if_env_config)).find("Optional") != -1

    def test_必須設定項目以外は全てデフォルト値を持つ(self):
        """必須設定項目以外は全てデフォルト値を持ち、最小構成で動作することを確認。"""
        plugin = SvgToPngPlugin()

        # 各設定項目がデフォルト値を持つかチェック
        has_defaults = {}

        for config_name, config_option in plugin.config_scheme:
            has_defaults[config_name] = hasattr(config_option, "default")

        # 期待される最小構成で動作に必要な項目
        essential_with_defaults = [
            "output_dir",  # 画像出力先
            "cache_enabled",  # キャッシュ有効化
            "preserve_original",  # 元コード保持
            "error_on_fail",  # エラー時動作
            "log_level",  # ログレベル
            "cleanup_generated_images",  # 生成画像のクリーンアップ
        ]

        for essential in essential_with_defaults:
            assert has_defaults.get(
                essential, False
            ), f"{essential} should have a default value for minimal configuration"

    def test_オプショナル設定はデフォルトNoneまたは空文字(self):
        """オプショナルな設定項目はデフォルトでNoneまたは空文字で問題なく動作することを確認。"""
        plugin = SvgToPngPlugin()

        # オプショナル設定項目
        optional_settings = [
            "enabled_if_env",  # 環境変数による有効化
        ]

        for config_name, config_option in plugin.config_scheme:
            if config_name in optional_settings:
                # オプショナル設定はOptional wrapper または空文字/Noneデフォルト
                is_optional = str(type(config_option)).find("Optional") != -1 or (
                    hasattr(config_option, "default")
                    and config_option.default in [None, ""]
                )
                assert (
                    is_optional
                ), f"{config_name} should be optional or have None/empty default"

    def test_最小設定での設定検証通過(self):
        """最小設定で設定検証が通過することを確認。"""
        # 最小設定（必須項目なし、すべてオプショナル）
        minimal_config = {}

        # 設定検証が成功することを確認
        result = SvgConfigManager().validate(minimal_config)
        assert result == minimal_config
