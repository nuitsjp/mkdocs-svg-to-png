from __future__ import annotations

from typing import Any


class SvgPreprocessorError(Exception):
    """SVG 事前処理で発生する例外の基底クラス。"""

    def __init__(self, message: str, **context_params: Any) -> None:
        """エラーメッセージと任意の文脈情報を受け取って初期化する。

        引数:
            message: 開発者向けの説明文
            **context_params: エラーの補足情報となる任意パラメータ
        """
        details = {k: v for k, v in context_params.items() if v is not None}

        # 可読性のため長いSVG内容は200文字で切り詰める
        for key in ["svg_content", "svg_code"]:
            if (
                key in details
                and isinstance(details[key], str)
                and len(details[key]) > 200
            ):
                details[key] = details[key][:200] + "..."

        super().__init__(message)
        self.details = details


class SvgConfigError(SvgPreprocessorError):
    """設定値の不備を表す例外。"""

    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        config_value: str | int | None = None,
        suggestion: str | None = None,
    ) -> None:
        """設定エラーの内容と関連情報を保持する。

        引数:
            message: エラー内容の説明
            config_key: 問題となった設定キー
            config_value: 不正と判断された値
            suggestion: 推奨される修正方法
        """
        super().__init__(
            message,
            config_key=config_key,
            config_value=config_value,
            suggestion=suggestion,
        )


class SvgConversionError(SvgPreprocessorError):
    """SVG→PNG 変換フェーズでの失敗を表す例外。"""

    def __init__(
        self,
        message: str,
        svg_path: str | None = None,
        output_path: str | None = None,
        svg_content: str | None = None,
        cairo_error: str | None = None,
    ) -> None:
        """変換処理の失敗に関する情報を保持する。

        引数:
            message: エラー内容の説明
            svg_path: 変換対象のSVGファイルパス
            output_path: 出力予定のPNGパス
            svg_content: 変換に失敗したSVG内容
            cairo_error: CairoSVG 由来の詳細メッセージ
        """
        super().__init__(
            message,
            svg_path=svg_path,
            output_path=output_path,
            svg_content=svg_content,
            cairo_error=cairo_error,
        )


class SvgFileError(SvgPreprocessorError):
    """ファイル操作関連の異常を表す例外。"""

    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        operation: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        """ファイル操作で失敗した際の情報を保持する。

        引数:
            message: エラー内容の説明
            file_path: 問題が発生したファイルパス
            operation: 失敗した操作種別（読込、書込など）
            suggestion: 推奨される修正方法
        """
        super().__init__(
            message, file_path=file_path, operation=operation, suggestion=suggestion
        )


class SvgParsingError(SvgPreprocessorError):
    """SVG の構文解析時に発生する例外。"""

    def __init__(
        self,
        message: str,
        source_file: str | None = None,
        line_number: int | None = None,
        svg_content: str | None = None,
    ) -> None:
        """パースエラーの発生箇所と内容を保持する。

        引数:
            message: エラー内容の説明
            source_file: エラーが発生したソースファイル
            line_number: 問題の行番号
            svg_content: 問題を引き起こしたSVG内容
        """
        super().__init__(
            message,
            source_file=source_file,
            line_number=line_number,
            svg_content=svg_content,
        )


class SvgValidationError(SvgPreprocessorError):
    """値の妥当性検証で異常を検出した際の例外。"""

    def __init__(
        self,
        message: str,
        validation_type: str | None = None,
        invalid_value: str | None = None,
        expected_format: str | None = None,
    ) -> None:
        """検証失敗の詳細情報を保持する。

        引数:
            message: エラー内容の説明
            validation_type: 失敗した検証の種類
            invalid_value: 不正と判断された値
            expected_format: 期待される形式やパターン
        """
        super().__init__(
            message,
            validation_type=validation_type,
            invalid_value=invalid_value,
            expected_format=expected_format,
        )


class SvgImageError(SvgPreprocessorError):
    """画像生成や取り扱いに起因する例外。"""

    def __init__(
        self,
        message: str,
        image_format: str | None = None,
        image_path: str | None = None,
        svg_content: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        """画像関連の失敗に伴う情報を保持する。

        引数:
            message: エラー内容の説明
            image_format: 対象となる画像フォーマット
            image_path: 生成または参照しようとしたパス
            svg_content: レンダリングに失敗したSVG内容
            suggestion: 推奨される修正方法
        """
        super().__init__(
            message,
            image_format=image_format,
            image_path=image_path,
            svg_content=svg_content,
            suggestion=suggestion,
        )
