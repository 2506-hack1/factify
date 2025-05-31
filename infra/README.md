# AWS CDKインフラストラクチャ
このディレクトリには、FastAPIアプリケーションをAWSにデプロイするためのインフラストラクチャ定義が含まれています。AWS CDK (Python) を使用して、ECS Fargate、S3、DynamoDB、API GatewayなどのAWSリソースをプロビジョニングします。

## 環境変数
CDKはAWSアカウントIDとリージョンを環境変数から取得します。明示的に指定しない場合、AWS CLIのデフォルト設定が使用されます。
`cdk bootstrap` 前に `export` でセットしてください。

- `CDK_DEFAULT_ACCOUNT`: AWSアカウントID
- `CDK_DEFAULT_REGION`: AWSリージョン (default: `ap-northeast-1`)

## セットアップ

1.  このディレクトリに移動し、仮想環境をセットアップします。
    ```bash
    cd infra
    python -m venv .venv
    ```

2.  Pythonの仮想環境をアクティブ化します。
    ```bash
    source .venv/bin/activate
    ```
    （まだ仮想環境をセットアップしていない場合は、プロジェクトルートの `README.md` を参照してください。）

## CDKコマンド

仮想環境をアクティブ化した状態で、以下のCDKコマンドを実行できます。

-   **CloudFormationテンプレートの生成**
    ```bash
    cdk synth
    ```
    これは、CDKコードからAWS CloudFormationテンプレートを生成します。

-   **デプロイする変更点の確認 (差分)**
    ```bash
    cdk diff
    ```
    現在デプロイされているスタックと、ローカルコードの差分を表示します。

-   **スタックのデプロイ**
    ```bash
    cdk deploy --require-approval never
    ```
    CloudFormationテンプレートをAWSにデプロイし、AWSリソースをプロビジョニングします。`--require-approval never` は対話的な確認をスキップします。

-   **スタックの削除**
    ```bash
    cdk destroy
    ```
    デプロイされたすべてのAWSリソースを削除します。**注意: この操作は元に戻せません。**

-   **スタックの出力の表示**
    ```bash
    cdk outputs
    ```
    デプロイされたスタックによってエクスポートされた値（例: API GatewayのURL）を表示します。