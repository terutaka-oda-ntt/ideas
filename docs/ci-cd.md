# CI/CD 環境ガイド

## 背景・目的

現代の開発ワークフローには、ハードウェアやソフトウェアツールだけでなく、**規約とそれを強制するツール・環境**が必要です。
AI以前のワークフローとして、CI/CDパイプラインとステージング環境の整備が先決事項です。

## 用語

| 用語 | 定義 |
|:---|---|
| ビルド | ワークスペースから成果物を生成すること。一般的にはコンパイル等が行われる |
| CI | 継続的インテグレーション |
| CD | 継続的デリバリ |
| テスト | 正常性を確認するためのスクリプト等で、tapまたはxunit形式で出力されるもの。自動テストとも記述する |
| ステージング | テストでとらえられない性質の不具合を人によるUIを通じて確認するための環境。手動テストとも記述する |

## CIのプロセス

### このリポジトリでの実装

本リポジトリでは、GitHub Actionsのワークフロー
`/.github/workflows/ci.yml` をCIの実装として提供しています。

- 対象イベント:
    - `main` / `stage` への `pull_request`
    - `main` / `stage` への `push`
- 実行内容:
    - `pre-commit run --all-files --show-diff-on-failure`
    - `./test/run_tests.sh`

これにより、ローカルのコミットフックで検出できる秘密情報混入を、
リモート（PR/Push）でも同一基準でブロックできます。

### 運用上の必須設定

GitHubのブランチ保護設定で `main` / `stage` に以下を適用します。

- 必須ステータスチェックとして `quality-and-security` を設定
- 直接pushを制限し、Pull Request経由でマージ

この設定は管理者トークンを使って以下で自動適用できます。

```bash
export GH_TOKEN=<repo admin token>
./scripts/apply_branch_protection.sh
```

### 権限チェックリスト（main/stage ブランチ保護）

設定作業前に、以下を順番に確認します。

#### 実施者の権限

- リポジトリ管理者権限（Admin）がある
- Repository Settings を開いて Branch protection を編集できる
- Organization配下の場合、対象リポジトリの設定変更が許可されている

#### トークン権限（CLIで設定する場合）

- Fine-grained PAT の場合:
    - 対象リポジトリに `ideas` が含まれる
    - Repository permissions の `Administration` が `Read and write`
- Classic PAT の場合:
    - `repo` スコープが付与されている
- トークン有効期限が切れていない
- SSO必須の組織ではトークンがSSO承認済み

#### 事前状態

- `main` ブランチが存在する
- `stage` ブランチが存在する

#### 保護ルール設定（main/stageそれぞれ）

- Branch protection が有効
- `Require a pull request before merging` が有効
- `Required approving reviews` が 1 以上
- `Require status checks to pass before merging` が有効
- 必須チェックに `quality-and-security` が含まれる
- `Include administrators` が有効
- `Allow force pushes` が無効
- `Allow deletions` が無効
- `Require conversation resolution before merging` が有効

#### 設定後の受け入れ確認

- `main` 向けPRで `quality-and-security` が必須チェックとして表示される
- `stage` 向けPRで `quality-and-security` が必須チェックとして表示される
- 必須チェックが失敗している間はマージできない
- 必須チェック成功後にマージ可能になる

#### 参考コマンド

```bash
# ブランチ保護を自動適用（管理者トークンが必要）
export GH_TOKEN=<repo admin token>
./scripts/apply_branch_protection.sh

# main/stage の保護有効状態と必須チェック（quality-and-security）を確認
for b in main stage; do
    json=$(gh api -H "Accept: application/vnd.github+json" repos/terutaka-oda-ntt/ideas/branches/$b)
    protected=$(echo "$json" | jq -r '.protected')
    has_qs=$(echo "$json" | jq -r '(.protection.required_status_checks.contexts // []) | index("quality-and-security") != null')
    echo "$b protected=$protected status_check_quality-and-security=$has_qs"
done
```

### トリガ
コミット時（ローカルでコミットしたものをGitHubへプッシュ）。
コミットにより、GitHub ActionsやCircle CIなどが起動され、CIプロセスが実行される。

### ビルド
CIプロセスの最初の工程。CIフレームワークによりビルド環境が作成され、ビルドが行われる。
典型的には `make test` などが実行される（`make test` では通常、`make all` した後にテストが実行されるよう Makefile を構成する）。

### テスト
ビルドプロセスの最終工程。テスト自体は自動で行われ、結果がtapまたはxunit形式で出力される。
UIのテストについても結果をtapなどで出力する必要があるため、ウェブアプリなどでは開発フレームワークに応じたテストを利用してヘッドレスでテストすることが求められる。
自動テストを定義できないものでCIをしたい場合はビルドのみとなる。

### デプロイ
CIフレームワークはテストがOKだった場合にデプロイする。

- **自動デプロイの場合**: mainへのプルリクエストとしてチケット作成
- **手動デプロイの場合**: stageへのプルリクエストとしてチケットを作成

## CDのプロセス

mainへのプルリクエストのメタ情報をもとに、デリバリ方針が決まる。

### 自動デプロイの場合
プルリクエストは自動マージされ、その結果としてデプロイされる。

### 承認付デプロイの場合
（承認フローが必要な場合にここへ追記）

## ステージング環境とその意義

CIでとらえられない性質の不具合の有無を、人によるUIを通じて確認するための環境。
ロボットなどでテストするものはステージングとしては扱わない。

CI/CDの観点では、ステージングへ分岐するとパイプラインが分断される（ステップ駆動となる）。

**バージョンアップ種別ごとの規約例：**

| バージョン種別 | 要求条件 |
|---|---|
| マイクロ | 自動テストグリーン → 本番に直接デプロイ |
| マイナー | 自動テストグリーン → ステージングでビルドグリーン → 本番デプロイ |
| メジャー | 自動テストグリーン → ステージングで手動テスト → releaseコミット → デプロイボタン |

## Azure 開発・検証環境の全体像

ADE（Azure Deployment Environments）はプロジェクト・環境タイプ（dev/test/staging）ごとにテンプレートからリソースを一括作成し、タグ/RBAC/ポリシーでガバナンスを管理します。
DevTest Labsは開発者がセルフサービスでVMを迅速に払い出せる仕組み（コスト制御・自動停止・アーティファクトによる初期構成自動化）を提供します。

```mermaid
flowchart TB
    subgraph People["開発チーム／QAチーム／チームリーダー"]
        Devs(開発者)
        QA(QA/テスター)
        TL(チームリーダー)
    end

    subgraph SourceCtrl["ソース管理 & カタログ"]
        GH["GitHub / Azure Repos\n- アプリコード\n- IaC(Bicep/ARM)\n- ADEカタログ(テンプレート)"]
        ArtifactsRepo["Artifacts リポジトリ\n- DevTest Labs用アーティファクト"]
    end

    subgraph CI["CI/CD"]
        Actions["GitHub Actions / Azure Pipelines\n- ビルド/テスト/デプロイ"]
        SIG["Shared Image Gallery\n- ベース/カスタムイメージ格納"]
    end

    subgraph AzureEnv["Azure サブスクリプション（開発・検証）"]
        subgraph ADE["Azure Deployment Environments (ADE)"]
            Catalog["環境テンプレート(Bicep/ARM)\n- envType: dev/test/staging\n- RBAC/タグ/ポリシー"]
            ADEDeploy["環境作成/削除の自動化\n- プロジェクト/チーム単位"]
        end

        subgraph DTL["Azure DevTest Labs"]
            Lab["Lab設定\n- コスト上限/自動停止/許可サイズ"]
            DTLVM["Dev/Test VM群"]
        end

        subgraph Common["共通基盤/運用"]
            KV[Azure Key Vault]
            LA["Log Analytics / Azure Monitor"]
            Policy["Azure Policy"]
        end
    end

    Devs --> GH
    QA --> GH
    TL --> GH
    GH --> Actions
    Actions --> ADEDeploy
    Actions --> SIG
    Actions --> DTLVM
    Catalog --- GH
    ADEDeploy --> KV
    ADEDeploy --> Policy
    Lab --- SIG
    Lab --- ArtifactsRepo
    DTLVM --> LA
    DTLVM --> KV
    LA --> TL
```

### ネットワーク構成

Private EndpointでStorage/Key VaultへのアクセスをVNet内に閉じ、NSG/UDRでトラフィックを制御。
BastionによりRDP/SSHを公開せずVMへ安全にアクセスできます。

```mermaid
flowchart LR
    subgraph Perimeter["境界/アクセス"]
        Internet[(Internet)]
        WAF["App Gateway (WAF/SSL終端)"]
        Bastion[Azure Bastion]
    end

    Internet --> WAF
    Internet --> Bastion

    subgraph VNet["VNet（開発・検証用）"]
        snApp["App/Subnet"]
        snDTL["DevTestLabs/Subnet"]
        snSvc["Services/Subnet"]
    end

    subgraph Services["共通サービス"]
        KV[(Key Vault)]
        SA[(Storage Account)]
        LA["Log Analytics/Monitor"]
        Policy["Azure Policy"]
    end

    WAF --> snApp
    Bastion --> snDTL
    SA ---|Private Endpoint| snSvc
    KV ---|Private Endpoint| snSvc
```

## 参考：Azure サービス比較

| サービス | 用途 | 状態 |
|---|---|---|
| Azure DevTest Labs | 開発・テスト用VM払い出し、コスト管理、アーティファクト適用 | 利用可 |
| Windows 365 | フル機能クラウドPC、エンタープライズポリシー強制 | 利用可 |
| DevBox | 開発者向けクラウドPC | Windows 365へ吸収予定 |
