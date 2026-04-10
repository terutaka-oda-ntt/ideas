# ideas リポジトリ

CI/CD・安全な開発環境に関するドキュメンテーション兼テンプレートリポジトリです。

このリポジトリは Python アプリケーションの配布・実行を目的としたプロジェクトではありません。
Python は `guardrails/test/` 配下のテストハーネス実行と CI 検証のためにのみ利用します。

このリポジトリは、他の GitHub プロジェクトへガードレールを導入するための共通ベースとしても利用できます。

## ドキュメント

| ドキュメント | 内容 |
|---|---|
| [プロジェクト開始ガイド](guardrails/docs/project-start.md) | 初回セットアップから日常ワークフローまで |
| [既存プロジェクト向け bootstrap 手順](guardrails/docs/existing-project-bootstrap.md) | 既存リポジトリへガードレールを後付け導入する手順 |
| [開発環境セットアップ](guardrails/docs/dev-environment.md) | pre-commit・detect-secrets の設定と運用 |
| [CI/CD 環境ガイド](guardrails/docs/ci-cd.md) | CI/CDの概念・Azure インフラ構成 |
| [テスト計画](guardrails/test/TEST_PLAN.md) | テストケース一覧（TC-01〜TC-19） |

## クイックスタート

```bash
git clone https://github.com/terutaka-oda-ntt/ideas.git
cd ideas
python3 -m venv guardrails/.venv && source guardrails/.venv/bin/activate
pip install -r requirements-ci.txt
pre-commit install
./guardrails/test/run_tests.sh
```

## テンプレートとして使う

新規プロジェクトにガードレールを導入する場合は、このリポジトリを GitHub Template Repository として利用する想定です。

```bash
# テンプレートから新規リポジトリを作成した後
python3 -m venv guardrails/.venv && source guardrails/.venv/bin/activate
pip install -r requirements-ci.txt
pre-commit install
detect-secrets scan --baseline .secrets.baseline
./guardrails/test/run_tests.sh
```

導入後に最低限見直す項目:

- `README.md` と `guardrails/docs/` のプロジェクト固有説明
- `.guardrails-config.yaml` の必須ファイルと任意ドキュメント
- `guardrails/scripts/apply_branch_protection.sh` の必須チェック名と対象ブランチ
- `.secrets.baseline` の初期化結果

既存プロジェクトへ後付け導入する場合は [guardrails/docs/existing-project-bootstrap.md](guardrails/docs/existing-project-bootstrap.md) を参照してください。

後付け導入を半自動化する場合は [guardrails/scripts/bootstrap_guardrails.sh](guardrails/scripts/bootstrap_guardrails.sh) を利用できます。
事前確認だけしたい場合は `--dry-run` を付けて実行できます。

## セキュリティ機能

- **detect-private-key**: 秘密鍵の自動検出
- **detect-secrets**: APIキー・DB接続情報・認証情報の自動検出
- **check-yaml / check-added-large-files**: 形式・サイズの検証

`.secrets.baseline` は追跡対象として管理し、変更時は差分レビューを前提とします。

詳細は [guardrails/docs/dev-environment.md](guardrails/docs/dev-environment.md) を参照してください。

## テスト

```bash
# 全テスト実行
./guardrails/test/run_tests.sh

# pre-commitの手動実行
pre-commit run --all-files
```

テストカテゴリ：TC-01〜04（形式）、TC-05〜07（内容）、TC-08〜10（セキュリティ）、TC-11〜19（フック動作）

## CI（実装済み）

CIの実装は [`.github/workflows/ci.yml`](.github/workflows/ci.yml) で提供しています。

運用手順・ブランチ保護・権限チェックリストの詳細は
[CI/CD 環境ガイド](guardrails/docs/ci-cd.md) を参照してください。

ブランチ保護の自動適用スクリプトは
[`guardrails/scripts/apply_branch_protection.sh`](guardrails/scripts/apply_branch_protection.sh) を利用します。

既存プロジェクトへのガードレール取り込みは
[`guardrails/scripts/bootstrap_guardrails.sh`](guardrails/scripts/bootstrap_guardrails.sh) を利用します。

既定では `main` と `stage` に `quality-and-security` を必須チェックとして設定します。
別プロジェクトでチェック名やブランチ名が異なる場合は、環境変数で上書きできます。

## リポジトリ構成

```
/
├── .guardrails-config.yaml    # ガードレール検証の設定
├── .pre-commit-config.yaml    # Pre-commit設定
├── .secrets.baseline          # detect-secretsベースライン
├── requirements-ci.txt        # CI/テストハーネス専用依存
├── .gitignore                 # Git除外設定
└── guardrails/
    ├── docs/
    │   ├── ci-cd.md
    │   ├── dev-environment.md
    │   ├── existing-project-bootstrap.md
    │   └── project-start.md
    ├── scripts/
    │   ├── apply_branch_protection.sh # ブランチ保護自動適用
    │   └── bootstrap_guardrails.sh    # 既存プロジェクト導入自動化
    └── test/
        ├── TEST_PLAN.md           # テスト計画（TC-01〜TC-19）
        ├── run_tests.sh           # 統合テスト実行スクリプト
        ├── test_structure.py
        ├── test_yaml.py
        ├── test_markdown.py
        ├── test_security.py
        └── test_precommit_hooks.py
```
