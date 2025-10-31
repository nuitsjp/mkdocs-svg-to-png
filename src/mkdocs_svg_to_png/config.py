from typing import Any

from mkdocs.config import config_options


class SvgConfigManager:
    """SVG→PNG変換プラグインの設定を集約し検証する管理クラス。"""

    @staticmethod
    def get_config_scheme() -> tuple[tuple[str, Any], ...]:
        """MkDocs に渡す SVG 関連設定のスキームを構築する。"""
        # プラグイン有効化条件と入出力先、動作フラグをまとめて列挙する
        return (
            # 実行可否を環境変数で切り替える場合のオプション
            (
                "enabled_if_env",
                config_options.Optional(config_options.Type(str)),
            ),
            # 生成画像の配置ディレクトリを指定する
            (
                "output_dir",
                config_options.Type(str, default="assets/images"),
            ),
            # 元のSVGを残すかどうかの制御
            (
                "preserve_original",
                config_options.Type(bool, default=False),
            ),
            # 変換失敗時に処理を中断させるかの指定
            (
                "error_on_fail",
                config_options.Type(bool, default=False),
            ),
            # ログ出力レベルを制御する
            (
                "log_level",
                config_options.Choice(
                    ["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO"
                ),
            ),
            # 生成したPNGをビルド後に削除するかどうか
            (
                "cleanup_generated_images",
                config_options.Type(bool, default=False),
            ),
        )

    def validate(self, config: dict[str, Any]) -> dict[str, Any]:
        """設定値を確認し、MkDocs にそのまま渡せる形で返す。"""
        # 必須設定は存在せず、すべてデフォルトか任意項目として扱う
        return config
