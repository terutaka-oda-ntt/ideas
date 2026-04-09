# プロジェクト開始ガイド

新しいプロジェクトでこのリポジトリの構成を利用・参考にする際の手順をまとめています。

## 前提ツール

| ツール | 用途 |
|---|---|
| Git | バージョン管理 |
| Python 3.x | テスト実行・pre-commit |
| pre-commit | コミット前チェック自動化 |

## 手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/terutaka-oda-ntt/ideas.git
cd ideas
```

### 2. 開発環境のセットアップ

```bash
# pre-commit インストール
pip install pre-commit

# Git フック登録
pre-commit install

# detect-secrets baseline 初期化
detect-secrets scan --baseline .secrets.baseline
```

### 3. 動作確認

```bash
# 全テスト実行
./test/run_tests.sh

# pre-commitの手動実行（全ファイル対象）
pre-commit run --all-files
```

## 日常の開発ワークフロー

1. **ブランチ作成**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **編集・確認**
   ```bash
   # ファイル編集後、テストで問題ないか確認
   ./test/run_tests.sh
   ```

3. **コミット**（pre-commitが自動実行）
   ```bash
   git add .
   git commit -m "feat: your change description"
   ```

4. **プッシュ・PR作成**
   ```bash
   git push origin feature/your-feature-name
   gh pr create --base main
   ```

## CIの自動実行（実装済み）

CIは [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) で実装済みです。

運用手順・ブランチ保護・権限チェックリストは
[CI/CD 環境ガイド](ci-cd.md) を参照してください。

## テストの実行

```bash
# 全テスト
./test/run_tests.sh

# 個別テスト
python3 test/test_structure.py    # ファイル構造
python3 test/test_yaml.py         # YAML形式
python3 test/test_markdown.py     # Markdown形式
python3 test/test_security.py     # セキュリティチェック
python3 test/test_precommit_hooks.py  # pre-commitフック動作確認
```

詳細は [test/TEST_PLAN.md](../test/TEST_PLAN.md) を参照してください。

## 参考ドキュメント

- [開発環境セットアップ](dev-environment.md) — pre-commit・detect-secrets の設定と運用
- [CI/CD 環境ガイド](ci-cd.md) — CI/CDの概念・Azure インフラ構成
