# ideas リポジトリ

CIとCD、安全な開発環境に関するドキュメンテーションリポジトリです。

## 📋 リポジトリ構成

```
/
├── devops_environment.md          # CI/CD環境の定義・プロセス
├── project-start-guid.md          # プロジェクト開始ガイド
├── secure-pc-development-environment.md  # 安全なPC開発環境
├── note.md                        # 開発ノート
├── PRE_COMMIT_SETUP.md           # Pre-commitセットアップガイド
├── .pre-commit-config.yaml       # Pre-commit設定（シークレット検出）
├── .gitignore                    # Git除外設定
└── test/                         # テストスイート
    ├── TEST_PLAN.md              # テスト計画（TC-01～TC-17）
    ├── run_tests.sh              # 統合テスト実行スクリプト
    ├── test_structure.py         # ファイル構造チェック（TC-05～TC-07）
    ├── test_yaml.py              # YAML形式チェック（TC-02）
    ├── test_markdown.py          # Markdown形式チェック（TC-01, TC-03, TC-04）
    ├── test_security.py          # セキュリティチェック（TC-08～TC-10）
    └── test_precommit_hooks.py   # Pre-commitフック動作確認（TC-11～TC-17）
```

## 🔒 セキュリティ機能

- **Pre-commit フレームワーク**: コミット前に自動チェック
- **秘密検出**: 秘密鍵やAPIキーの自動検出・防止
- **形式チェック**: YAML、Markdown形式の検証
- **.gitignore**: 機密ファイルの自動除外

詳細は [PRE_COMMIT_SETUP.md](PRE_COMMIT_SETUP.md) を参照してください。

## ✅ テスト

### 全テスト実行

```bash
./test/run_tests.sh
```

### 個別テスト実行

```bash
# ファイル構造チェック
python3 test/test_structure.py

# YAML形式チェック
python3 test/test_yaml.py

# Markdown形式チェック
python3 test/test_markdown.py

# セキュリティチェック
python3 test/test_security.py

# Pre-commitフック動作確認（TC-11～TC-17）
python3 test/test_precommit_hooks.py
```

### テスト カテゴリ

- **TC-01～04**: ファイル形式チェック（Markdown、YAML、末尾チェック）
- **TC-05～07**: 内容チェック（ファイル存在、セクション、リンク形式）
- **TC-08～10**: セキュリティチェック（秘密検出、.gitignore確認）
- **TC-11～17**: Pre-commitフック動作確認（秘密検出、形式修正、大容量ファイル）

詳細は [test/TEST_PLAN.md](test/TEST_PLAN.md) 参照。

## 📝 使用方法

### 開発ワークフロー

1. **ドキュメント編集**
   ```bash
   # ファイルを編集
   vim devops_environment.md
   ```

2. **テスト実行**（コミット前）
   ```bash
   ./test/run_tests.sh
   ```

3. **コミット** （pre-commitが自動実行）
   ```bash
   git add .
   git commit -m "Update documentation"
   ```

### トラブル

**Q: pre-commitをバイパスしたい**
```bash
git commit --no-verify
```

**Q: チェックが失敗した**

pre-commitが変更を自動修正している場合があります：
```bash
git add .
git commit -m "message"
```

## 📚 主要ドキュメント

- [CI/CD環境の定義](devops_environment.md)
- [Pre-commitセットアップガイド](PRE_COMMIT_SETUP.md)
- [テスト計画](test/TEST_PLAN.md)
- [安全なPC開発環境](secure-pc-development-environment.md)

## 🛠 セットアップ

### 初回セットアップ

```bash
# Pre-commit インストール
pip install pre-commit

# Git hook登録
pre-commit install

# テスト実行
./test/run_tests.sh
```

### 依存パッケージ

- `pre-commit`: Git hook管理
- `pyyaml`: YAML解析（テスト実行時に自動インストール）
