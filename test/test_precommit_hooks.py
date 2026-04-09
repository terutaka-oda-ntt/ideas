#!/usr/bin/env python3
"""
Pre-commitフック動作確認テスト

このテストは、pre-commitが実際に期待通りに動作するかを確認します：
- シークレット検出が機能するか
- 形式修正が機能するか
- 各種フックが正常に動作するか

テストは独立した一時的なgitリポジトリ上で実行され、
元のリポジトリに影響を与えません。
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

class PreCommitHookTester:
    """pre-commitフック動作テスト"""

    def __init__(self):
        self.test_repo = None
        self.passed_tests = []
        self.failed_tests = []
        self.original_dir = os.getcwd()
        self.repo_root = Path(__file__).resolve().parent.parent

    def setup(self):
        """テスト用の一時的なgitリポジトリを作成"""
        # 一時ディレクトリ作成
        self.test_repo = tempfile.mkdtemp(prefix="precommit_test_")
        print(f"テストリポジトリ作成: {self.test_repo}")

        os.chdir(self.test_repo)

        # Git初期化
        subprocess.run(["git", "init"], capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], capture_output=True, check=True)

        # リポジトリルートから pre-commit 設定をコピー
        parent_config = self.repo_root / ".pre-commit-config.yaml"
        if parent_config.exists():
            shutil.copy(parent_config, ".pre-commit-config.yaml")
            print("✓ pre-commit設定をコピー")

        # detect-secrets の baseline をコピー
        parent_baseline = self.repo_root / ".secrets.baseline"
        if parent_baseline.exists():
            shutil.copy(parent_baseline, ".secrets.baseline")
            print("✓ detect-secrets baselineをコピー")

        # 初期コミットを作成（設定ファイルを追跡対象にする）
        files_for_initial_commit = [".pre-commit-config.yaml"]
        if Path(".secrets.baseline").exists():
            files_for_initial_commit.append(".secrets.baseline")

        subprocess.run(["git", "add", *files_for_initial_commit], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit with pre-commit config"], capture_output=True)

        # pre-commitをインストール
        result = subprocess.run(["pre-commit", "install"], capture_output=True)
        if result.returncode == 0:
            print("✓ pre-commitをインストール")
        else:
            stderr = result.stderr.decode() if result.stderr else ""
            if "already" in stderr.lower():
                print("✓ pre-commitは既にインストール済み")
            else:
                print(f"⚠ pre-commitインストール警告: {stderr[:100]}")

    def cleanup(self):
        """テスト用リポジトリを削除"""
        os.chdir(self.original_dir)
        if self.test_repo and os.path.exists(self.test_repo):
            shutil.rmtree(self.test_repo)
            print(f"\n✓ テストリポジトリをクリーンアップ")

    def run_test(self, test_name, setup_func, should_fail=False):
        """テスト実行ヘルパー"""
        try:
            # テスト前のクリーンアップ
            subprocess.run(["git", "reset", "--hard"], capture_output=True)
            subprocess.run(["git", "clean", "-fd"], capture_output=True)

            # ファイルをセットアップ
            setup_func()

            # ファイルをステージ
            subprocess.run(["git", "add", "."], capture_output=True, check=True)

            # コミット試行
            result = subprocess.run(
                ["git", "commit", "-m", f"Test: {test_name}"],
                capture_output=True,
                text=True
            )

            # フックがファイルを修正した場合は再ステージして再コミット
            if result.returncode != 0:
                git_status = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True
                )

                if git_status.stdout.strip():
                    # 修正されたファイルを再度ステージしてコミット
                    subprocess.run(["git", "add", "."], capture_output=True)
                    result = subprocess.run(
                        ["git", "commit", "-m", f"Test: {test_name} (after fix)"],
                        capture_output=True,
                        text=True
                    )

            # 結果判定
            commit_succeeded = result.returncode == 0

            if should_fail:
                if not commit_succeeded:
                    print(f"✓ {test_name}: フック検出成功（コミット中止）")
                    self.passed_tests.append(test_name)
                    if "Aborting" in result.stdout or "Aborting" in result.stderr:
                        print(f"  → {result.stderr[:100] if result.stderr else result.stdout[:100]}")
                else:
                    print(f"✗ {test_name}: フック検出失敗（コミット成功）")
                    self.failed_tests.append((test_name, "should have failed"))
            else:
                if commit_succeeded:
                    print(f"✓ {test_name}: コミット成功")
                    self.passed_tests.append(test_name)
                else:
                    print(f"✗ {test_name}: コミット失敗")
                    self.failed_tests.append((test_name, "should have succeeded"))
                    print(f"  → Error: {result.stderr[:100] if result.stderr else result.stdout[:100]}")

        except Exception as e:
            print(f"✗ {test_name}: テスト実行エラー - {str(e)}")
            self.failed_tests.append((test_name, str(e)))

    def test_private_key_detection(self):
        """TC-11: 秘密鍵検出テスト"""
        def setup():
            # フック検出テスト用のダミー秘密鍵（文字列結合で構築し、ソース自体が検出されることを防ぐ）
            header = "-----BEGIN RSA " + "PRIVATE KEY-----"
            footer = "-----END RSA " + "PRIVATE KEY-----"
            dummy_key = f"{header}\nMIIEowIBAAKCAQEA1234567890abcdefghijklmnopqrstuvwxyz\n{footer}"
            Path("id_rsa").write_text(dummy_key)
            Path("README.md").write_text("# Test")

        self.run_test("TC-11: 秘密鍵検出", setup, should_fail=True)

    def test_api_key_detection(self):
        """TC-12: APIキー検出テスト"""
        def setup():
            Path("config.py").write_text("API_KEY = 'sk-12345678901234567890abcdefghij'")
            Path("README.md").write_text("# Test")

        self.run_test("TC-12: APIキー検出", setup, should_fail=True)

    def test_trailing_whitespace_fix(self):
        """TC-13: 末尾空白の自動修正テスト"""
        try:
            # テスト前のクリーンアップ
            subprocess.run(["git", "reset", "--hard", "HEAD"], capture_output=True)
            subprocess.run(["git", "clean", "-fd"], capture_output=True)

            Path("test.md").write_text("# Test File  \nThis has trailing spaces on line 1.")
            Path("README.md").write_text("# Test")

            subprocess.run(["git", "add", "."], capture_output=True, check=True)

            # 修正前の内容を保存
            original_content = Path("test.md").read_text()

            # コミット試行
            result = subprocess.run(
                ["git", "commit", "-m", "TC-13: 末尾空白の自動修正"],
                capture_output=True,
                text=True
            )

            # 修正後の内容を確認
            modified_content = Path("test.md").read_text()

            if original_content != modified_content and "  \n" not in modified_content:
                print(f"✓ TC-13: 末尾空白の自動修正: フック修正成功")
                print(f"  ✓ → ファイルが自動修正されました")
                self.passed_tests.append("TC-13: 末尾空白の自動修正")
            else:
                print(f"✗ TC-13: 末尾空白の自動修正: ファイルが修正されませんでした")
                self.failed_tests.append(("TC-13: 末尾空白の自動修正", "file not modified"))
        except Exception as e:
            print(f"✗ TC-13: テスト実行エラー - {str(e)}")
            self.failed_tests.append(("TC-13: 末尾空白の自動修正", str(e)))

    def test_end_of_file_fixer(self):
        """TC-14: ファイル末尾の自動修正テスト"""
        try:
            # テスト前のクリーンアップ
            subprocess.run(["git", "reset", "--hard", "HEAD"], capture_output=True)
            subprocess.run(["git", "clean", "-fd"], capture_output=True)

            Path("test.txt").write_bytes(b"This file has no newline at end")
            Path("README.md").write_text("# Test")

            subprocess.run(["git", "add", "."], capture_output=True, check=True)

            # 修正前の内容を保存
            original_content = Path("test.txt").read_bytes()

            # コミット試行
            result = subprocess.run(
                ["git", "commit", "-m", "TC-14: ファイル末尾の自動修正"],
                capture_output=True,
                text=True
            )

            # 修正後の内容を確認
            modified_content = Path("test.txt").read_bytes()

            if original_content != modified_content and modified_content.endswith(b"\n"):
                print(f"✓ TC-14: ファイル末尾の自動修正: フック修正成功")
                print(f"  ✓ → ファイルに改行が追加されました")
                self.passed_tests.append("TC-14: ファイル末尾の自動修正")
            else:
                print(f"✗ TC-14: ファイル末尾の自動修正: ファイルが修正されませんでした")
                self.failed_tests.append(("TC-14: ファイル末尾の自動修正", "file not modified"))
        except Exception as e:
            print(f"✗ TC-14: テスト実行エラー - {str(e)}")
            self.failed_tests.append(("TC-14: ファイル末尾の自動修正", str(e)))

    def test_normal_file_commit(self):
        """TC-15: 正常なファイルのコミット成功テスト"""
        def setup():
            Path("normal.md").write_text("# Normal File\n\nThis is a normal file.\n")
            Path("README.md").write_text("# Test\n")

        self.run_test("TC-15: 正常なファイルのコミット", setup, should_fail=False)

    def test_invalid_yaml(self):
        """TC-16: YAML形式エラー検出テスト"""
        def setup():
            Path("invalid.yaml").write_text("""repos:
  - repo: https://example.com
    rev: v1.0
  invalid: [unclosed bracket
""")
            Path("README.md").write_text("# Test")

        self.run_test("TC-16: YAML形式エラー検出", setup, should_fail=True)

    def test_large_file_detection(self):
        """TC-17: 大容量ファイル検出テスト"""
        def setup():
            large_file = Path("large_file.bin")
            large_file.write_bytes(b"X" * (1024 * 1024 + 1))
            Path("README.md").write_text("# Test")

        self.run_test("TC-17: 大容量ファイル検出", setup, should_fail=True)

    def test_db_connection_secret_detection(self):
        """TC-18: DB接続文字列（認証情報入り）検出テスト"""
        def setup():
            Path("db_config.env").write_text(
                "DATABASE_URL='postgresql://dbadmin:SuperSecretP@ssw0rd@db.example.local:5432/prod_db'\n"
            )
            Path("README.md").write_text("# Test")

        self.run_test("TC-18: DB接続文字列検出", setup, should_fail=True)

    def test_login_credentials_detection(self):
        """TC-19: ログイン情報（username/password）検出テスト"""
        def setup():
            Path("credentials.yaml").write_text(
                "username: service-admin\npassword: 'UltraSecretLoginPass123!'\n"
            )
            Path("README.md").write_text("# Test")

        self.run_test("TC-19: ログイン情報検出", setup, should_fail=True)

    def run_all_tests(self):
        """すべてのテストを実行"""
        print("\n" + "=" * 60)
        print("Pre-commitフック動作確認テスト")
        print("=" * 60 + "\n")

        try:
            self.setup()

            print("\n--- テスト実行開始 ---\n")

            self.test_private_key_detection()
            self.test_api_key_detection()
            self.test_trailing_whitespace_fix()
            self.test_end_of_file_fixer()
            self.test_normal_file_commit()
            self.test_invalid_yaml()
            self.test_large_file_detection()
            self.test_db_connection_secret_detection()
            self.test_login_credentials_detection()

            print("\n--- テスト結果 ---")
            print(f"\n✓ 成功: {len(self.passed_tests)}")
            print(f"✗ 失敗: {len(self.failed_tests)}")

            if self.failed_tests:
                print("\nテスト詳細:")
                for test_name, reason in self.failed_tests:
                    print(f"  - {test_name}: {reason}")

            print()
            return len(self.failed_tests) == 0

        finally:
            self.cleanup()

if __name__ == "__main__":
    tester = PreCommitHookTester()
    success = tester.run_all_tests()

    if success:
        print("=" * 60)
        print("すべてのpre-commitフックテストに通りました！")
        print("=" * 60)
        sys.exit(0)
    else:
        print("=" * 60)
        print(f"{len(tester.failed_tests)}件のテストが失敗しました")
        print("=" * 60)
        sys.exit(1)
