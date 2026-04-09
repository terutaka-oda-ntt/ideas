#!/usr/bin/env python3
"""
Markdown形式チェック
"""
import os
import sys
import re
from pathlib import Path

def check_markdown_files():
    """Markdownファイルの基本的な形式をチェック"""
    root_dir = Path(__file__).parent.parent
    markdown_files = list(root_dir.glob("*.md")) + list(root_dir.glob("docs/*.md"))

    errors = []
    passed = 0

    for md_file in markdown_files:
        try:
            content = md_file.read_text(encoding='utf-8')

            # TC-01: Markdown形式チェック（基本的な構文）
            if not content:
                errors.append(f"[TC-01] {md_file.name}: ファイルが空です")
                continue

            # TC-03: ファイル末尾確認
            if not content.endswith('\n'):
                errors.append(f"[TC-03] {md_file.name}: ファイルが改行で終了していません")
            else:
                passed += 1

            # TC-04: 末尾空白チェック
            for line_num, line in enumerate(content.split('\n'), 1):
                if line.rstrip('\n') != line.rstrip('\n').rstrip():
                    errors.append(f"[TC-04] {md_file.name}:{line_num} に末尾空白があります")
                    break
            else:
                passed += 1

            # TC-07: リンク形式チェック
            # Markdown形式のリンク: [text](url)
            link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
            links = re.findall(link_pattern, content)
            for text, url in links:
                if not text or not url:
                    errors.append(f"[TC-07] {md_file.name}: 不正なリンク形式 [{text}]({url})")
            if links:
                passed += 1

            # TC-06: セクション確認（重要ファイル向け）
            if md_file.name == "ci-cd.md":
                sections = ["トリガ", "CIのプロセス", "CDのプロセス"]
                for section in sections:
                    if section not in content:
                        errors.append(f"[TC-06] {md_file.name}: セクション '{section}' が見つかりません")
                if all(s in content for s in sections):
                    passed += 1

        except Exception as e:
            errors.append(f"[Error] {md_file.name}: {str(e)}")

    return passed, errors

if __name__ == "__main__":
    passed, errors = check_markdown_files()

    print("=" * 60)
    print("Markdown形式チェック結果")
    print("=" * 60)

    if errors:
        print(f"\n❌ エラー: {len(errors)}件\n")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print(f"\n✓ すべてのMarkdownファイルがチェックに通りました（{passed}件）")
        sys.exit(0)
