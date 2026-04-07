#!/usr/bin/env python3
"""
セキュリティチェック（秘密情報と.gitignore検証）
"""
import sys
import re
from pathlib import Path

def check_security():
    """セキュリティに関するチェック"""
    root_dir = Path(__file__).parent.parent
    errors = []
    passed = 0

    # TC-08, TC-09: 秘密情報の簡易検出
    print("秘密情報をスキャン中...")
    secret_patterns = {
        "API_KEY": r"([Aa][Pp][Ii][_-]?[Kk][Ee][Yy][\s]*[=:]\s*['\"]?[A-Za-z0-9_\-]{20,}['\"]?)",
        "AWS_KEY": r"(AKIA[0-9A-Z]{16})",
        "PRIVATE_KEY": r"(-----BEGIN [A-Z ]+ PRIVATE KEY-----)",
        "PASSWORD": r"([Pp]assword[\s]*[=:]\s*['\"][^'\"]+['\"])",
        "TOKEN": r"([Tt]oken[\s]*[=:]\s*['\"]?[A-Za-z0-9_\-]{20,}['\"]?)",
    }

    text_files = list(root_dir.glob("*.md")) + list(root_dir.glob("*.yaml")) + list(root_dir.glob("*.yml"))

    for file_path in text_files:
        if file_path.name.startswith("."):
            continue

        try:
            content = file_path.read_text(encoding='utf-8')

            for pattern_name, pattern in secret_patterns.items():
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    errors.append(f"[TC-08/09] {file_path.name}:{line_num} に {pattern_name} パターンが検出されました")
        except Exception as e:
            pass

    if not errors:
        passed += 1

    # TC-10: .gitignore確認
    gitignore_path = root_dir / ".gitignore"
    if gitignore_path.exists():
        try:
            gitignore_content = gitignore_path.read_text(encoding='utf-8')
            required_excludes = [".baseline", "*.key", "*.pem"]

            # .secrets.baseline が除外されているか確認
            if ".baseline" in gitignore_content or ".secrets.baseline" in gitignore_content:
                passed += 1
                print(f"✓ .gitignore: シークレットベースラインが除外されています")
            else:
                print(f"⚠ .gitignore: .secrets.baseline が除外されていません")
        except Exception as e:
            errors.append(f"[TC-10] .gitignore: {str(e)}")
    else:
        print("⚠ .gitignore が見つかりません")

    return passed, errors

if __name__ == "__main__":
    passed, errors = check_security()

    print("\n" + "=" * 60)
    print("セキュリティチェック結果")
    print("=" * 60)

    if errors:
        print(f"\n❌ エラー: {len(errors)}件\n")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print(f"\n✓ セキュリティチェックに通りました（{passed}件）")
        sys.exit(0)
