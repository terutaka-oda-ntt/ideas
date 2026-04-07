#!/usr/bin/env python3
"""
YAML形式チェック
"""
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: pyyaml がインストールされていません")
    print("インストール: pip install pyyaml")
    sys.exit(1)

def check_yaml_files():
    """YAMLファイルの形式をチェック"""
    root_dir = Path(__file__).parent.parent
    yaml_files = list(root_dir.glob("*.yaml")) + list(root_dir.glob("*.yml"))

    errors = []
    passed = 0

    for yaml_file in yaml_files:
        try:
            # TC-02: YAML形式チェック
            content = yaml_file.read_text(encoding='utf-8')
            data = yaml.safe_load(content)

            # 特定ファイルに対する検証
            if yaml_file.name == ".pre-commit-config.yaml":
                # repos キーが存在するか確認
                if not isinstance(data, dict):
                    errors.append(f"[TC-02] {yaml_file.name}: トップレベルが辞書型ではありません")
                    continue

                if "repos" not in data:
                    errors.append(f"[TC-02] {yaml_file.name}: 'repos' キーが見つかりません")
                    continue

                if not isinstance(data["repos"], list):
                    errors.append(f"[TC-02] {yaml_file.name}: 'repos' がリスト型ではありません")
                    continue

                # 各repoに必須フィールドがあるか確認
                for i, repo in enumerate(data["repos"]):
                    if not isinstance(repo, dict):
                        errors.append(f"[TC-02] {yaml_file.name}: repos[{i}] が辞書型ではありません")
                        continue

                    if "repo" not in repo:
                        errors.append(f"[TC-02] {yaml_file.name}: repos[{i}] に 'repo' キーがありません")

                    if "hooks" not in repo:
                        errors.append(f"[TC-02] {yaml_file.name}: repos[{i}] に 'hooks' キーがありません")

            if not errors:
                passed += 1
                print(f"✓ {yaml_file.name}: OK")

        except yaml.YAMLError as e:
            errors.append(f"[TC-02] {yaml_file.name}: YAML形式エラー - {str(e)}")
        except Exception as e:
            errors.append(f"[Error] {yaml_file.name}: {str(e)}")

    # YAMLファイルがない場合
    if not yaml_files:
        print("⚠ YAMLファイルが見つかりません")

    return passed, errors

if __name__ == "__main__":
    passed, errors = check_yaml_files()

    print("\n" + "=" * 60)
    print("YAML形式チェック結果")
    print("=" * 60)

    if errors:
        print(f"\n❌ エラー: {len(errors)}件\n")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print(f"\n✓ すべてのYAMLファイルがチェックに通りました（{passed}件）")
        sys.exit(0)
