# ideas リポジトリ

CI/CD・安全な開発環境に関するドキュメンテーションリポジトリです。

## ドキュメント

| ドキュメント | 内容 |
|---|---|
| [プロジェクト開始ガイド](docs/project-start.md) | 初回セットアップから日常ワークフローまで |
| [開発環境セットアップ](docs/dev-environment.md) | pre-commit・detect-secrets の設定と運用 |
| [CI/CD 環境ガイド](docs/ci-cd.md) | CI/CDの概念・Azure インフラ構成 |
| [テスト計画](test/TEST_PLAN.md) | テストケース一覧（TC-01〜TC-19） |

## クイックスタート

```bash
git clone https://github.com/terutaka-oda-ntt/ideas.git
cd ideas
pip install pre-commit
pre-commit install
./test/run_tests.sh
```

## セキュリティ機能

- **detect-private-key**: 秘密鍵の自動検出
- **detect-secrets**: APIキー・DB接続情報・認証情報の自動検出
- **check-yaml / check-added-large-files**: 形式・サイズの検証

詳細は [docs/dev-environment.md](docs/dev-environment.md) を参照してください。

## テスト

```bash
# 全テスト実行
./test/run_tests.sh

# pre-commitの手動実行
pre-commit run --all-files
```

テストカテゴリ：TC-01〜04（形式）、TC-05〜07（内容）、TC-08〜10（セキュリティ）、TC-11〜19（フック動作）

## リポジトリ構成

```
/
├── docs/
│   ├── ci-cd.md               # CI/CD概念・Azureインフラ構成
│   ├── dev-environment.md     # pre-commit・detect-secrets設定と運用
│   └── project-start.md       # プロジェクト開始ガイド
├── .pre-commit-config.yaml    # Pre-commit設定
├── .secrets.baseline          # detect-secretsベースライン
├── .gitignore                 # Git除外設定
└── test/
    ├── TEST_PLAN.md           # テスト計画（TC-01〜TC-19）
    ├── run_tests.sh           # 統合テスト実行スクリプト
    ├── test_structure.py
    ├── test_yaml.py
    ├── test_markdown.py
    ├── test_security.py
    └── test_precommit_hooks.py
```
