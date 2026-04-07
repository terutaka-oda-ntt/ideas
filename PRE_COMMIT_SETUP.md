# Pre-Commit セットアップガイド

このリポジトリではpre-commitフレームワークを導入し、シークレットなどの機密情報がコミットされるのを防いでいます。

## セットアップ内容

### インストール済みのツール
- **pre-commit**: Gitコミット前に自動チェック
- **detect-private-key**: 秘密鍵の検出
- **trailing-whitespace**: コードの末尾の空白削除
- **end-of-file-fixer**: ファイルの末尾の改行修正
- **check-yaml**: YAML形式の検証
- **check-added-large-files**: 大きなファイルの誤コミット防止

### ファイル構成
```
.pre-commit-config.yaml    # Pre-commit設定ファイル
.secrets.baseline          # detect-secretsのベースラインファイル（用途やリセット時に更新）
.gitignore                 # .secrets.baselineなど機密ファイルを除外
```

## 使用方法

### 1. 初回セットアップ（既に完了）
```bash
pip install pre-commit
pre-commit install
```

### 2. コミット時の動作
ファイルをステージしてコミットすると、自動的に以下のチェックが実行されます：

```bash
git add <file>
git commit -m "commit message"
```

**チェック内容:**
- ✅ 秘密鍵が含まれていないか確認
- ✅ YAMLファイルの形式チェック
- ✅ 大きなファイルの誤コミット確認
- ✅ コード形式の修正（末尾空白など）

### 3. チェックが失敗した場合

#### 秘密鍵が検出された場合
```
Aborting commit. Found private key: path/to/file
```

対処法：
1. ファイルから秘密情報を削除
2. または `.gitignore` に追加
3. ファイルを再度ステージしてコミット

#### 形式ミスが検出された場合
```
- hook id: trailing-whitespace
- files were modified by this hook
```

対処法：
ファイルが自動修正されているので、確認後再度ステージしてコミット
```bash
git add <file>
git commit -m "commit message"
```

### 4. すべてのファイルをチェック（開発時）
```bash
pre-commit run --all-files
```

## 設定の更新

### フックの追加・変更
`.pre-commit-config.yaml` を編集後、フックを再インストール：
```bash
pre-commit install
```

### フックのバージョン更新
```bash
pre-commit autoupdate
```

## baselineのリセット

シークレット検出ベースラインをリセットする場合：
```bash
detect-secrets scan --baseline .secrets.baseline
```

## よくあるトラブル

### Q: pre-commitをバイパスしたい
```bash
git commit --no-verify
```
※ ただし本番環境へリリースされる場合は推奨されません

### Q: 特定ファイルを除外したい
`.pre-commit-config.yaml` で `exclude` を設定:
```yaml
- id: detect-private-key
  exclude: 'test\.py$'
```

### Q: フックのタイムアウトが発生
`.pre-commit-config.yaml` で `timeout` を設定:
```yaml
- id: detect-private-key
  timeout: 10
```
