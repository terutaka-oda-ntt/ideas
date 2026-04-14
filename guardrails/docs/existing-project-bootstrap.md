# 既存プロジェクト向け bootstrap 手順

既存の GitHub リポジトリへ、このテンプレートのガードレールを後付け導入する手順です。

目的は次の 4 点です。

- ローカルで pre-commit による基本チェックを有効化する
- GitHub Actions で同じ基準を継続実行する
- branch protection でマージ条件を強制する
- 構造テストの期待値を対象プロジェクトに合わせる

## 前提

- 対象リポジトリは GitHub 上に存在する
- Python 3.x と Git が利用できる
- 対象リポジトリに変更を入れるブランチを作成できる
- branch protection を適用する場合は管理者権限または相当トークンを持っている

## 導入の考え方

既存プロジェクトでは、テンプレートをそのまま複製せず、まず共通ガードレールだけを導入します。

最初の導入対象:

- `.pre-commit-config.yaml`
- `.secrets.baseline`
- `.guardrails-config.yaml`
- `.gitleaks.toml`
- `requirements-ci.txt`
- `.github/workflows/ci.yml`
- `guardrails/scripts/apply_branch_protection.sh`
- `guardrails/scripts/apply_org_branch_protection.sh`
- `guardrails/test/`

`README.md` や既存の `docs/` は上書きせず、必要な説明だけ追加します。

## 推奨フロー

### 1. 作業ブランチを作成

```bash
git checkout -b chore/bootstrap-guardrails
```

### 2. テンプレートから共通ファイルを取り込む

まずは bootstrap スクリプトを使う方法を推奨します。

```bash
# 既存リポジトリ側で実行
./guardrails/scripts/bootstrap_guardrails.sh --template-dir /path/to/ideas --target-dir .
```

先に変更予定だけ確認したい場合:

```bash
./guardrails/scripts/bootstrap_guardrails.sh --template-dir /path/to/ideas --target-dir . --dry-run
```

`guardrails/docs/` も取り込みたい場合:

```bash
./guardrails/scripts/bootstrap_guardrails.sh --template-dir /path/to/ideas --target-dir . --with-docs
```

既存ファイルを上書きする場合のみ `--force` を使います。

手動で取り込む場合は次の手順を使います。

テンプレートリポジトリを別ディレクトリへ clone してある前提で、必要ファイルだけをコピーします。

```bash
TEMPLATE_DIR=/path/to/ideas

mkdir -p .github/workflows guardrails/scripts guardrails/test
cp "$TEMPLATE_DIR/.pre-commit-config.yaml" .
cp "$TEMPLATE_DIR/.secrets.baseline" .
cp "$TEMPLATE_DIR/.guardrails-config.yaml" .
cp "$TEMPLATE_DIR/.gitleaks.toml" .
cp "$TEMPLATE_DIR/requirements-ci.txt" .
cp "$TEMPLATE_DIR/.github/workflows/ci.yml" .github/workflows/ci.yml
cp "$TEMPLATE_DIR/guardrails/scripts/apply_branch_protection.sh" guardrails/scripts/apply_branch_protection.sh
cp "$TEMPLATE_DIR/guardrails/scripts/apply_org_branch_protection.sh" guardrails/scripts/apply_org_branch_protection.sh
cp -r "$TEMPLATE_DIR/guardrails/test/." guardrails/test/
```

既存プロジェクトに `test/` ディレクトリがあっても、`guardrails/test/` を使うため衝突を回避できます。

### 3. 構造テストの期待値を対象リポジトリへ合わせる

`.guardrails-config.yaml` を編集し、対象プロジェクトで必須としたいファイルだけを残します。

例:

```yaml
required_files:
  - .pre-commit-config.yaml
  - .gitignore
  - package.json

optional_docs:
  - docs/architecture.md
  - guardrails/docs/ci-cd.md
```

ドキュメントを持たないプロジェクトでは `optional_docs` を空配列にして構いません。

### 4. CI の実行条件を対象プロジェクトへ合わせる

`.github/workflows/ci.yml` の既定では、次の 3 点が固定です。

- 対象ブランチは `main`
- `quality-and-security` ジョブで `pre-commit run --all-files` と `./guardrails/test/run_tests.sh` を実行
- `gitleaks-pr-scan` ジョブで PR 差分を検査

`stage` を保護対象にしたい場合は、`.github/workflows/ci.yml` の対象ブランチへ明示的に追加してください。

既存の CI がある場合は、次のどちらかに寄せるのが安全です。

1. 既存 workflow に pre-commit と `./guardrails/test/run_tests.sh` を追加する
2. この workflow を guardrails 専用ジョブとして併設する

### 5. ローカル初期化を実行

```bash
pip install -r requirements-ci.txt
pre-commit install
detect-secrets scan --baseline .secrets.baseline
pre-commit run --all-files
./guardrails/test/run_tests.sh
```

ここで失敗した場合は、既存ファイルに含まれる secret らしき値、YAML 形式エラー、末尾空白などを先に解消します。

### 6. baseline をレビューする

`.secrets.baseline` は導入対象プロジェクトの現状を反映して再生成されます。

確認ポイント:

- 実際の秘密情報を許容していないか
- テスト用ダミー値だけが記録されているか
- 今後もレビュー可能な差分サイズか

不要な許容は残さず、問題のある値は baseline に入れる前にファイル側を修正します。

### 7. 初回 PR を作成

初回 PR では、ガードレール導入と既存コード修正を混ぜない方が安全です。

PR に含める内容は、原則として次に限定します。

- ガードレール関連ファイルの追加
- pre-commit による自動修正
- secret 検出や形式エラーに対する最小修正

### 8. CI 成功後に branch protection を適用

必須チェックは、対象リポジトリで一度成功してから保護ルールへ追加します。

```bash
export GH_TOKEN=<repo admin token>
./guardrails/scripts/apply_org_branch_protection.sh
```

`quality-and-security` も必須にする場合:

```bash
export GH_TOKEN=<repo admin token>
./guardrails/scripts/apply_org_branch_protection.sh --profile full-guardrails
```

`stage` や `release` を守る場合:

```bash
export GH_TOKEN=<repo admin token>
./guardrails/scripts/apply_org_branch_protection.sh --branches main,stage,release
```

## 初回導入で確認する項目

- `pre-commit run --all-files` が通る
- `./guardrails/test/run_tests.sh` が通る
- GitHub Actions の `quality-and-security` と `gitleaks-pr-scan` が通る
- `.secrets.baseline` の差分がレビュー済みである
- `.gitleaks.toml` の allowlist 変更が理由付きでレビューされている
- branch protection の必須チェック名が実際の job 名と一致している

## よくある調整ポイント

### 既存プロジェクトに別のテストランナーがある

このテンプレートの `guardrails/test/` はガードレール検証用です。既存のアプリケーションテストとは分けて扱って構いません。

### `stage` ブランチも保護したい

標準は `main` のみです。`stage` を追加する場合は、`.github/workflows/ci.yml` の対象ブランチと
`./guardrails/scripts/apply_org_branch_protection.sh --branches` を同時に更新してください。

### Python を普段使わないプロジェクトで導入したい

このテンプレートの検証ハーネスは Python 依存です。Node.js や Java のプロジェクトでも導入は可能ですが、guardrails 用の依存として Python は残ります。

### 既存の secret が多すぎる

一度に全面導入せず、まずは `.pre-commit-config.yaml` と baseline のみ先行し、その後 CI と branch protection を段階導入した方が安全です。
