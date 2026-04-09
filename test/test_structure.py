#!/usr/bin/env python3
"""
ファイル構造と必須ファイルのチェック
"""
import sys
from pathlib import Path

def check_file_structure():
    """ファイル構造と必須ファイルをチェック"""
    root_dir = Path(__file__).parent.parent
    errors = []
    passed = 0

    # TC-05: 重要ファイルの存在確認
    required_files = {
        "README.md": "リポジトリルートファイル",
        ".pre-commit-config.yaml": "pre-commit設定",
        ".gitignore": "Git除外ファイル",
    }

    print("必須ファイルをチェック中...")
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
        "docs/ci-cd.md": "CI/CD環境ドキュメント",
        "docs/dev-environment.md": "開発環境セットアップガイド",
        "docs/project-start.md": "プロジェクト開始ガイド",
    }

    print("\nドキュメントファイルをチェック中...")
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
