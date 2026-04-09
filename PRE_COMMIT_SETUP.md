# Pre-Commit セットアップガイド

このリポジトリではpre-commitフレームワークを導入し、シークレットなどの機密情報がコミットされるのを防いでいます。

## セットアップ内容

### インストール済みのツール
- **pre-commit**: Gitコミット前に自動チェック
- **detect-private-key**: 秘密鍵の検出
- **detect-secrets**: APIキー・DB接続情報・認証情報などの検出
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
- ✅ APIキー・DB接続文字列・ログイン情報などの検出
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

#### detect-secrets が検出した場合
```
ERROR: Potential secrets about to be committed to git repo!
```

対処法：
1. 実際の秘密情報なら値を削除し、環境変数やシークレット管理に移動
2. サンプル値など許容対象なら `.secrets.baseline` を更新
3. 再度 `pre-commit run --all-files` で確認後にコミット

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

更新内容を確認する場合：
```bash
git diff .secrets.baseline
```

定常運用の推奨：
- フック更新時（`pre-commit autoupdate` 後）に baseline の差分をレビュー
- `.secrets.baseline` の変更は理由をPR本文に明記

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
