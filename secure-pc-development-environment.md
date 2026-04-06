# Secure PC Development Environment

Windows Administrator権限がない環境での安全で効率的な開発環境構築ガイドです。GitHub Codespaces を活用し、ローカルにファイルを保存せず、すべての開発をクラウド上で実施します。

## 概要

セキュアPC環境では以下の制約があります：
- Windows Administrator 権限がない
- WSL 2 が利用できない
- Docker が使用できない
- ローカルファイルが暗号化される

**解決策：GitHub Codespaces を使用することで、これらの制約を回避し、クラウド上に完全な開発環境を構築できます。**

---

## 1. GitHub Codespaces の基本的な説明と利点

### Codespaces とは

GitHub Codespaces は、GitHub 上でホストされるクラウドベースの開発環境です。ブラウザ上で VS Code が動作し、すべてのコード・実行環境がクラウドに存在します。

### セキュアPC環境での主な利点

| 利点 | 説明 |
|------|------|
| **ローカルファイル不要** | ファイルはすべて GitHub 上に保存。ローカルの暗号化問題を回避 |
| **Administrator権限不要** | ブラウザのみで開発可能。ローカルインストール不要 |
| **一貫した環境** | チーム全体が同じ開発環境を使用可能 |
| **セキュリティ** | ローカルマシンにファイルが残らないため、データ漏洩リスクが低い |
| **フルスタック開発対応** | Node.js、Python、Go、Java など主要言語・フレームワークがプリインストール |

---

## 2. セキュアPC環境での使用方法

### 前提条件

- GitHub アカウント
- インターネット接続（セキュアPC環境で許可されていること）
- 最新のブラウザ（Chrome、Firefox、Safari など）

### ステップ1：リポジトリへのアクセス

1. GitHub 上で開発対象のリポジトリにアクセス
2. ブラウザで `.` キーを押すか、URL の `github.com` を `github.dev` に変更
   - 例：`https://github.dev/owner/repo`
3. ブラウザベースの VS Code が起動

### ステップ2：Codespaces の起動

1. VS Code 画面左下の「<>」アイコンをクリック
2. 「Codespaces」を選択
3. 「Create new codespace」をクリック
4. ブランチとマシンスペックを選択
5. 環境が起動するまで待機（初回は 2-3 分程度）

### ステップ3：開発環境の確認

- Terminal を開く（Ctrl + `` ` ``）
- 以下のコマンドで基本ツールが利用可能か確認：
  ```bash
  node --version
  python --version
  git --version
  ```

---

## 3. セットアップ手順

### `.devcontainer/devcontainer.json` の設定

プロジェクトルートに `.devcontainer/devcontainer.json` を作成し、プロジェクト固有の開発環境を定義します。

```json
{
  "name": "Project Development Environment",
  "image": "mcr.microsoft.com/devcontainers/universal:latest",
  "features": {
    "ghcr.io/devcontainers/features/node:latest": {
      "nodeGptVersion": "lts"
    },
    "ghcr.io/devcontainers/features/python:latest": {
      "version": "3.11"
    }
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-vscode.vscode-typescript-next",
        "ms-python.python",
        "ms-git.github",
        "esbenp.prettier-vscode",
        "dbaeumer.vscode-eslint"
      ],
      "settings": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "esbenp.prettier-vscode"
      }
    }
  },
  "postCreateCommand": "npm install && pip install -r requirements.txt",
  "remoteUser": "codespace"
}
```

### カスタマイズ項目の説明

| 項目 | 説明 |
|------|------|
| `image` | ベースイメージ。Universal イメージは複数の言語をサポート |
| `features` | 追加インストール。Node.js、Python など |
| `extensions` | VS Code 拡張機能。チーム全体で同じ拡張をインストール |
| `postCreateCommand` | 環境起動後に実行するコマンド。依存パッケージのインストールなど |

---

## 4. ベストプラクティス

### 4.1 VS Code 拡張機能の推奨設定

`.devcontainer/devcontainer.json` の `extensions` フィールドに以下を含めることを推奨：

```json
"extensions": [
  "ms-vscode-remote.remote-containers",
  "ms-vscode.remote-explorer",
  "ms-git.github",
  "ms-python.python",
  "ms-vscode.vscode-typescript-next",
  "esbenp.prettier-vscode",
  "dbaeumer.vscode-eslint",
  "GitHub.Copilot",
  "ms-vscode.makefile-tools"
]
```

### 4.2 環境変数の管理

機密情報（API キー、データベース接続文字列など）は：
- リポジトリに **絶対にコミットしない**
- GitHub Secrets を使用
- Codespaces では環境変数として自動注入可能

設定方法：
1. リポジトリの Settings → Secrets and variables → Codespaces
2. New repository secret で追加
3. `.devcontainer/devcontainer.json` で参照

### 4.3 定期的な環境リセット

古い Codespaces インスタンスは定期的に削除：
1. GitHub Settings → Codespaces
2. 未使用のインスタンスを削除
3. ストレージと課金を最適化

### 4.4 Git 設定

Codespaces 起動時に自動的に設定されますが、必要に応じて カスタマイズ：

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global init.defaultBranch main
```

---

## 5. 無料枠の使用制限と管理方法

### GitHub Codespaces の無料利用額

| リソース | 月間無料額 |
|---------|---------|
| コンピュート時間 | 120 時間（2GB マシン相当） |
| ストレージ | 15GB |

### コスト最適化のコツ

1. **マシンスペックの選択**
   - 軽量なプロジェクトは 2GB マシンを選択
   - 必要に応じてのみ 4GB 以上にアップグレード

2. **自動シャットダウン設定**
   - Settings → Codespaces
   - Timeout を 30 分に設定（デフォルト 60 分）
   - 非アクティブ状態で自動停止

3. **不要なインスタンスの削除**
   - 使用完了後、明示的にインスタンスを削除
   - GitHub Settings → Codespaces で確認

4. **スケジュール停止**
   - Settings で Codespaces の自動停止をスケジュール

### 使用状況の確認

GitHub Settings → Billing and plans → Codespaces usage で月間利用時間を確認。

---

## 6. ベストプラクティス（開発フロー）

### 推奨ワークフロー

1. **開発ブランチの作成**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **定期的なコミット**
   - 区切りよく、小さなコミットを作成
   - コミットメッセージは明確に

3. **Pull Request の作成**
   - GitHub Web UI から PR を作成
   - コードレビューを受ける
   - Codespaces 内からも PR の確認・対応可能

4. **環境のクリーンアップ**
   ```bash
   # 作業完了後、Codespaces を停止・削除
   # GitHub Settings から管理
   ```

---

## 7. トラブルシューティング

### 問題：Codespaces が起動しない

**原因と対策：**
- GitHub アカウントが有効か確認
- インターネット接続を確認
- ブラウザキャッシュをクリアして再試行
- 別のブラウザで試行

### 問題：拡張機能がインストールされない

**原因と対策：**
- `.devcontainer/devcontainer.json` の `extensions` フィールドを確認
- VS Code 拡張マーケットプレイスで利用可能か確認
- 拡張 ID（例：`ms-vscode.vscode-typescript-next`）が正確か確認

### 問題：`postCreateCommand` が失敗する

**原因と対策：**
- コマンドの構文を確認
- 依存ファイル（`package.json`、`requirements.txt`）が存在するか確認
- Terminal でコマンドを手動実行してエラーメッセージを確認

### 問題：ファイルが同期されない

**原因と対策：**
- GitHub にプッシュしているか確認
- ローカルと Codespaces 両方でプルしているか確認
- ブラウザをリロード

### 問題：無料枠を超えてしまった

**対策：**
- 不要な Codespaces インスタンスを削除
- マシンスペックをダウングレード
- 自動シャットダウン時間を短縮

---

## 8. セキュリティのベストプラクティス

### 8.1 機密情報の保護

- **パスワード・トークン・キー** は絶対に `.devcontainer.json` や `.env` に記載しない
- GitHub Secrets を使用
- ログアウト時に必ずセッションを終了

### 8.2 コードレビューとアクセス制御

- チーム内で PR ベースのワークフローを遵守
- リポジトリのアクセス権限を最小限に設定
- Codespaces の共有は避ける（個人用に使用）

### 8.3 ネットワークセキュリティ

- VPN を使用している場合、接続状態を確認
- 企業の通信ポリシーを遵守

---

## 9. 参考リンク

- [GitHub Codespaces 公式ドキュメント](https://docs.github.com/en/codespaces)
- [Dev Containers 仕様](https://containers.dev/)
- [VS Code Remote Development](https://code.visualstudio.com/docs/remote/remote-overview)