# 開発環境セットアップガイド

このリポジトリではpre-commitフレームワークを導入し、シークレットなどの機密情報がコミットされるのを防いでいます。

## インストール済みのツール

| ツール | 役割 |
|---|---|
| **pre-commit** | Gitコミット前に自動チェックを実行 |
| **detect-private-key** | 秘密鍵の検出 |
| **detect-secrets** | APIキー・DB接続情報・認証情報などの検出 |
| **trailing-whitespace** | 行末の不要な空白を自動削除 |
| **end-of-file-fixer** | ファイル末尾の改行を自動修正 |
| **check-yaml** | YAML形式の検証 |
| **check-added-large-files** | 大きなファイルの誤コミット防止（上限1MB） |

## 関連ファイル

```
.pre-commit-config.yaml    # Pre-commit設定ファイル
.secrets.baseline          # detect-secretsのベースラインファイル
.guardrails-config.yaml    # テンプレート利用時の検証設定
.gitignore                 # 機密ファイルの除外設定
```

## セットアップ手順

### 1. 初回セットアップ

```bash
pip install pre-commit
pre-commit install
detect-secrets scan --baseline .secrets.baseline
```

`.secrets.baseline` は `.gitignore` に入れず、リポジトリで追跡します。

### 2. コミット時の動作

```bash
git add <file>
git commit -m "commit message"
```

コミット時に自動で以下がチェックされます：

- ✅ 秘密鍵が含まれていないか
- ✅ APIキー・DB接続文字列・ログイン情報などの検出
- ✅ YAMLファイルの形式
- ✅ 大きなファイルの誤コミット
- ✅ 行末空白・ファイル末尾改行の自動修正

### 3. 全ファイルチェック（任意）

```bash
pre-commit run --all-files
```

## チェックが失敗した場合の対処

### 秘密鍵が検出された場合

```
Aborting commit. Found private key: path/to/file
```

1. ファイルから秘密情報を削除
2. または `.gitignore` に追加
3. 再度ステージしてコミット

### detect-secrets が検出した場合

```
ERROR: Potential secrets about to be committed to git repo!
```

1. **実際の秘密情報の場合**: 値を削除し、環境変数やシークレット管理サービスへ移動
2. **サンプル値など許容対象の場合**: `.secrets.baseline` を更新してから再コミット
3. `pre-commit run --all-files` で確認後にコミット

### 形式ミスが検出された場合

```
- hook id: trailing-whitespace
- files were modified by this hook
```

フックがファイルを自動修正しているため、確認後に再ステージしてコミット：

```bash
git add <file>
git commit -m "commit message"
```

## 設定の更新

### フックの追加・変更

`.pre-commit-config.yaml` を編集後：

```bash
pre-commit install
```

### フックのバージョン更新

```bash
pre-commit autoupdate
```

## baselineの管理

### baselineの再生成

```bash
detect-secrets scan --baseline .secrets.baseline
```

### 差分の確認

```bash
git diff .secrets.baseline
```

### 定常運用ルール

- `pre-commit autoupdate` 実行後は baseline の差分をレビューする
- `.secrets.baseline` の変更はPR本文に理由を明記する
- テンプレート利用先では `.guardrails-config.yaml` をプロジェクト構成に合わせて更新する

## GitHub Codespaces の設定

Codespacesで開発環境を自動構成する場合は `.devcontainer/devcontainer.json` を作成します：

```json
{
    "name": "Dev Container",
    "image": "mcr.microsoft.com/devcontainers/python:3.11",
    "postCreateCommand": "pip install pre-commit && pre-commit install",
    "customizations": {
        "vscode": {
            "extensions": [
                "ms-python.python",
                "redhat.vscode-yaml"
            ]
        }
    }
}
```

## .gitignore テンプレート

言語別の代表的な除外パターンです。

**Python**
```
__pycache__/
*.py[cod]
*.pyo
.env
```

**Node.js**
```
node_modules/
npm-debug.log
.env
```

**Java**
```
*.class
target/
.env
```

## よくあるトラブル

### Q: pre-commitをバイパスしたい

```bash
git commit --no-verify
```

※ 本番リリースに関わるコミットには使用しないこと

### Q: 特定ファイルを除外したい

`.pre-commit-config.yaml` で `exclude` を設定：

```yaml
- id: detect-private-key
  exclude: 'test\.py$'
```

### Q: フックのタイムアウトが発生する

`.pre-commit-config.yaml` で `timeout` を設定：

```yaml
- id: detect-private-key
  timeout: 10
```
