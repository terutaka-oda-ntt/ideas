## やりたいこと
### 開発・検証ワークフローの近代化をしたい
AIではなく、AI以前の開発ワークフローに追いつきたい。
MCP活用した支援や「仕様書ベース開発」は、AI以前のワークフローの延長にあると思われるため、
まずはAI以前に追いつくことが大事。

今時の開発環境は以下のものが必要
- ハードウェア(PC等)
- 開発ツール(VSCode, plugins)
- 規約とそれを強制するツール・環境
- デプロイまでのワークフロールールとそれを強制するツール・環境

つまり、単なるハード、ソフトウェアツールのみならず、規約とそれを
強制する環境も用意する必要がある。
そしてそれらを実現するためのサービスがAzureには用意されている（しかも複数）。

## CI/CDの実際
テストを書くことが必須。
テストとは（自動テストとも記述する）、
- 正常性を確認するためのシェルスクリプト等で、tapまたはxunit形式で出力されるもの

UIのテストについても、結果をtapなどで出力する必要があるため、ウェブアプリなどでは、開発フレームワークに応じた
テストを利用するなどヘッドレスでテストすることが求められる

## ステージング(stagingあるいはproduction like)環境とその意義
CIでとらえられない性質の不具合の有無を人によるUIを通じて確認するためのもの（手動テストとも記述する）として定義する。
ロボットなどでテストするのはステージングとしては扱わないことにする。
CI/CDの観点では、ステージングへ分岐するということは、パイプラインが分断されることを意味する。（ステップ駆動となる）

例えば、規約として以下のようになっていたとする
1. マイクロバージョンアップの場合、自動テストグリーンを要求する
2. マイナーバージョンアップの場合、ステージングでのビルドグリーンを要求する
3. メジャーバージョンアップの場合、ステージングを経由して、手動テストを要求する。

1.のケースだと、コミットされたら自動テストが動き、グリーンなら、そのまま本番にデプロイされる。
2.のケースだと、自動テストグリーン後、本番ではなく、ステージングでのビルドを行う。ステージングのビルドがグリーンなら、そのまま本番にデプロイされる。
3.のケースだと、自動テストグリーン後、ステージングでビルドする。人が手動テストをステージングで行ったのち、
  テスト結果を、releaseファイルなどとして、コミットすることで、あらたなコミットを作成し、
  そのコミットに対してデプロイボタンを押すイメージ。

## DevTest Labsで確認したいこと

以下のサービスのうちDevTest Labsをテストしたい。本来はほしい機能と各サービスの機能・費用比較で
決定するべきだが、それぞれ膨大な機能を持つサービスであり、それぞれが関連するほかのサービスへの
依存も持っているため、全貌がよくわからない。
また、終了予定のAzure Labの後継DevBoxですらWindows 265へ吸収されるなど、サービスの整理も盛んであるため、
調査もむつかしい。

#### DevTest Labs
開発・テストのためのラボで、ARMやADEを使ってAtricactを適用させた仮想PCや、サービスの集合体である
環境自体を提供できる模様。
また、ユーザ管理(EntraIDユーザ以外も可能)もこの中で可能(Microsoftアカウントが必要)。
#### Windows 365
フル機能のクラウドPCで、チームやエンタープライズのルールを強制できる。
#### DevBox
DeBoxはWindows 365に吸収予定。

## ワークフロー全体像
ADEは、プロジェクトや環境タイプ（dev/test 等）ごとにテンプレートからリソースを一括作成し、タグ/RBAC/ポリシーでガバナンスを利かせます。
DevTest Labsは、開発者がセルフサービスでVM を迅速に払い出しできる仕組み。コスト制御（自動停止、サイズ制限）やアーティファクトで初期構成自動化。
Shared Image Galleryでベース/カスタムイメージを共有し、ADE の VM/Scale SetやDevTest Labs の VMで共用できます。
**監視/ログ（Log Analytics/Azure Monitor）とセキュリティ（Key Vault, Policy）**は共通化して、プロジェクト横断の標準運用に寄せます。

```mermaid
flowchart TB
    %% 人・コード・環境の関係を上から下へ
    subgraph People["開発チーム／QAチーム／チームリーダー"]
        Devs(開発者)
        QA(QA/テスター)
        TL(チームリーダー)
    end

    subgraph SourceCtrl["ソース管理 & カタログ"]
        GH["GitHub / Azure Repos- アプリコード - IaC(Bicep/ARM)- ADEカタログ(テンプレート)"]
        ArtifactsRepo["Artifacts リポジトリ- DevTest Labs用アーティファクト(スクリプト/ツール)"]
    end

    subgraph CI["CI/CD"]
        Actions["GitHub Actions / Azure Pipelines- ビルド/テスト/デプロイ"]
        SIG["Shared Image Gallery- ベース/カスタムイメージ格納"]
    end

    subgraph AzureEnv["Azure サブスクリプション（開発・検証）"]
        subgraph ADE["Azure Deployment Environments (ADE)"]
            Catalog["環境テンプレート(Bicep/ARM)- envType: dev/test/staging- RBAC/タグ/ポリシー"]
            ADEDeploy["環境作成/削除の自動化- プロジェクト/チーム単位"]
        end

        subgraph DTL["Azure DevTest Labs"]
            Lab["Lab(ラボ)設定- コスト上限/自動停止/許可サイズ"]
            Formulas["Formulas(定義済みVMレシピ)"]
            CustomImages["Custom Images"]
            DTLVM["Dev/Test VM群"]
        end

        subgraph Common["共通基盤/運用"]
            VNet["VNet & Subnets"]
            Bastion["Azure Bastion"]
            KV[Azure Key Vault]
            SA["Storage Account(Artifacts/ログ/一時ファイル)"]
            LA["Log Analytics / Azure Monitor(監視/メトリック/ログ)"]
            Policy["Azure Policy(タグ/セキュリティ/コスト管理)"]
        end
    end

    %% 関係線
    Devs --> GH
    QA --> GH
    TL --> GH

    GH --> Actions
    Actions --> ADEDeploy
    Actions --> SIG
    Actions --> DTLVM

    Catalog --- GH
    ADEDeploy --> VNet
    ADEDeploy --> SA
    ADEDeploy --> KV
    ADEDeploy --> Policy

    Lab --- SIG
    Lab --- ArtifactsRepo
    Formulas --> DTLVM
    CustomImages --> DTLVM
    DTLVM --> VNet
    DTLVM --> Bastion
    DTLVM --> LA
    DTLVM --> KV

    %% 運用まわり
    Policy --> DTLVM
    Policy --> ADEDeploy
    LA --> TL
    LA --> Devs

```

Private Endpointで Storage/Key Vault へのアクセスを VNet 内に閉じ、NSG/UDR で東西/南北トラフィックを制御。
Bastionを使うことで、RDP/SSH を公開せず安全に VM へアクセス。
Azure Policyでサブスクリプション横断のタグ付与、許可リージョン/SKU、不要な公開 IP 禁止などを一括適用。
Log Analytics/Azure Monitorで VM/サービスのメトリック・ログを収集し、アラート/ダッシュボードを標準化。

```mermaid

flowchart LR
    subgraph Perimeter["境界/アクセス(japaneastなど)"]
        Internet[(Internet)]
        WAF["App Gateway (WAF/SSL終端)"]
        Bastion[Azure Bastion]
    end

    Internet --> WAF
    Internet --> Bastion

    subgraph VNet["VNet（開発・検証用）"]
        subgraph Subnets["サブネット"]
            snApp["App/Subnet<br/>- ADEデプロイのPaaS/VM"]
            snDTL["DevTestLabs/Subnet<br/>- DTL VM群"]
            snSvc["Services/Subnet<br/>- Key Vault/Storage PE/Monitor"]
            snJump["Jump/Subnet<br/>- 管理/踏み台(必要時)"]
        end
        NSGApp["NSG(App)"]
        NSGDTL["NSG(DTL)"]
        NSGSvc["NSG(Services)"]
        UDR["ユーザ定義ルート(必要時)"]
    end

    WAF --> snApp
    Bastion --> snDTL
    Bastion --> snJump

    %% サービス連携
    subgraph Services["共通サービス"]
        KV[(Key Vault)]
        SA[(Storage Account)]
        LA["(Log Analytics/Monitor)"]
        SIG["(Shared Image Gallery)"]
        Policy["(Azure Policy)"]
    end

    %% Private Endpoints
    SA ---|Private Endpoint| snSvc
    KV ---|Private Endpoint| snSvc

    %% 相互接続
    snApp --> NSGApp
    snDTL --> NSGDTL
    snSvc --> NSGSvc
    NSGApp --> UDR
    NSGDTL --> UDR
    NSGSvc --> UDR

    %% デプロイ主体
    subgraph ADE["Azure Deployment Environments"]
        ADETpl["ADEテンプレート(Bicep/ARM)"]
        ADEOps["環境作成/破棄/タグ/RBAC"]
    end
    ADETpl --> ADEOps
    ADEOps --> snApp
    ADEOps --> snSvc
    ADEOps --> Policy
    ADEOps --> LA

    subgraph DTL["Azure DevTest Labs"]
        Lab["Lab設定(コスト上限/自動停止)"]
        Formulas["Formula/Artifacts"]
        DTLVMs[DTL VM群]
    end
    Lab --> DTLVMs
    Formulas --> DTLVMs
    DTLVMs --> snDTL
    DTLVMs --> LA
    DTLVMs --> KV

    SIG --> ADEOps

```

ガバナンス統一：ADE テンプレートに「タグ（CostCenter/Owner/Project）」「RBAC ロール」「ポリシー割り当て」を組み込み、環境作成＝標準適用の形にします。
コスト最適化：DevTest Labs のスケジュール自動停止と許可 VM サイズで無駄を抑制。ADE でも Auto-shutdown をリソースに適用。
初期構成自動化：Artifacts を使い、VM 作成時にエージェント導入（Monitor/Defender）やツール配布を自動化。
イメージ戦略：Shared Image Gallery にOS パッチ済み・ミドルウェア同梱イメージを置き、ADE/DTL のどちらからも参照。
ネットワーク分離：App/Subnet と DTL/Subnet を分離し、NSG と UDR でテスト用 VM の影響がアプリ側に波及しないように。

## セキュアドPC（端末暗号化）前提でのソフトウェア開発環境の在り方

[詳細はこちら](./secure-pc-development-environment.md)



