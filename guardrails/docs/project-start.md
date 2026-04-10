# プロジェクト開始ガイド

新しいプロジェクトでこのリポジトリの構成をテンプレートとして利用する際の手順をまとめています。

## 前提ツール

| ツール | 用途 |
|---|---|
| Git | バージョン管理 |
| Python 3.x | テスト実行・pre-commit |
| pre-commit | コミット前チェック自動化 |

## 手順

### 1. リポジトリの作成

GitHub の Template Repository として新規リポジトリを作成します。

既存リポジトリへ後付け導入する場合は、少なくとも以下を取り込みます。

- `.pre-commit-config.yaml`
- `requirements-ci.txt`
- `.github/workflows/ci.yml`
- `guardrails/scripts/apply_branch_protection.sh`
- `.guardrails-config.yaml`

具体的な取り込み順序と初回 PR の進め方は [既存プロジェクト向け bootstrap 手順](existing-project-bootstrap.md) を参照してください。

### 2. リポジトリのクローン

```bash
git clone https://github.com/<owner>/<repo>.git
cd <repo>
```

### 3. 開発環境のセットアップ

```bash
# CI/ガードレール用依存のインストール
pip install -r requirements-ci.txt

# Git フック登録
pre-commit install

# detect-secrets baseline 初期化または再生成
detect-secrets scan --baseline .secrets.baseline
```

`.secrets.baseline` はコミット対象に含め、差分をレビューします。

### 4. 動作確認

```bash
# 全テスト実行
./guardrails/test/run_tests.sh

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
   ./guardrails/test/run_tests.sh
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

## カスタマイズ対象

テンプレートから作成した直後に、次の項目を見直してください。

- `README.md` のプロジェクト説明
- `guardrails/docs/ci-cd.md` のインフラ固有説明
- `.guardrails-config.yaml` の必須ファイルと任意ドキュメント
- `guardrails/scripts/apply_branch_protection.sh` 実行時の `PROTECTED_BRANCHES` と `REQUIRED_CONTEXTS`

## CIの自動実行（実装済み）

CIは [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) で実装済みです。

運用手順・ブランチ保護・権限チェックリストは
[CI/CD 環境ガイド](ci-cd.md) を参照してください。

## テストの実行

```bash
# 全テスト
./guardrails/test/run_tests.sh

# 個別テスト
python3 guardrails/test/test_structure.py    # ファイル構造
python3 guardrails/test/test_yaml.py         # YAML形式
python3 guardrails/test/test_markdown.py     # Markdown形式
python3 guardrails/test/test_security.py     # セキュリティチェック
python3 guardrails/test/test_precommit_hooks.py  # pre-commitフック動作確認
```

詳細は [guardrails/test/TEST_PLAN.md](../test/TEST_PLAN.md) を参照してください。

## 参考ドキュメント

- [開発環境セットアップ](dev-environment.md) — pre-commit・detect-secrets の設定と運用
- [既存プロジェクト向け bootstrap 手順](existing-project-bootstrap.md) — 既存リポジトリへ後付け導入する流れ
- [CI/CD 環境ガイド](ci-cd.md) — CI/CDの概念・Azure インフラ構成
