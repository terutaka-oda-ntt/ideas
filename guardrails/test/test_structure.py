#!/usr/bin/env python3
"""
ファイル構造と必須ファイルのチェック
"""
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: pyyaml がインストールされていません")
    print("インストール: pip install -r requirements-ci.txt")
    sys.exit(1)


def load_guardrail_config(root_dir):
    """構造テストの設定を読み込む"""
    config_path = root_dir / ".guardrails-config.yaml"
    if not config_path.exists():
        return {
            "required_files": [".pre-commit-config.yaml", ".gitignore"],
            "optional_docs": [
                "guardrails/docs/ci-cd.md",
                "guardrails/docs/dev-environment.md",
                "guardrails/docs/project-start.md",
            ],
        }

    with config_path.open(encoding="utf-8") as config_file:
        data = yaml.safe_load(config_file) or {}

    return {
        "required_files": data.get("required_files", []),
        "optional_docs": data.get("optional_docs", []),
    }

def check_file_structure():
    """ファイル構造と必須ファイルをチェック"""
    root_dir = Path(__file__).resolve().parent.parent.parent
    config = load_guardrail_config(root_dir)
    errors = []
    passed = 0

    # TC-05: 重要ファイルの存在確認
    required_files = {
        "README.md": "リポジトリルートファイル",
        ".pre-commit-config.yaml": "pre-commit設定",
        ".gitignore": "Git除外ファイル",
        ".guardrails-config.yaml": "ガードレール検証設定",
    }

    print("必須ファイルをチェック中...")
    for filename in config["required_files"]:
        required_files.setdefault(filename, "テンプレート利用側で定義された必須ファイル")

    for filename, description in required_files.items():
        file_path = root_dir / filename

        # README.mdは存在しなくても良い（後で作成が可能）
        if filename == "README.md":
            continue

        if file_path.exists():
            passed += 1
            print(f"✓ {filename}: {description} - 存在")
        else:
            errors.append(f"[TC-05] {filename}: {description} - 見つかりません")

    # ドキュメントファイルの存在
    doc_files = {
        "guardrails/docs/ci-cd.md": "CI/CD環境ドキュメント",
        "guardrails/docs/dev-environment.md": "開発環境セットアップガイド",
        "guardrails/docs/project-start.md": "プロジェクト開始ガイド",
    }

    print("\nドキュメントファイルをチェック中...")
    for filename in config["optional_docs"]:
        doc_files.setdefault(filename, "テンプレート利用側で定義された任意ドキュメント")

    for filename, description in doc_files.items():
        file_path = root_dir / filename
        if file_path.exists():
            passed += 1
            print(f"✓ {filename}: {description} - 存在")
        else:
            print(f"ℹ {filename}: {description} - 見つかりません")

    return passed, errors

if __name__ == "__main__":
    passed, errors = check_file_structure()

    print("\n" + "=" * 60)
    print("ファイル構造チェック結果")
    print("=" * 60)

    if errors:
        print(f"\n❌ エラー: {len(errors)}件\n")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print(f"\n✓ 必須ファイルが確認されました（{passed}件）")
        sys.exit(0)
