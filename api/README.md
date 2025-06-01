# FastAPIアプリケーション

このディレクトリには、AWS FargateにデプロイされるFastAPIアプリケーションのコードが含まれています。
S3へのファイルアップロード機能と、DynamoDBへのアイテム保存・取得機能を持っています。

## ファイル説明

- `main.py`: FastAPIアプリケーションの主要なコードです。ルートエンドポイント、ファイルアップロードエンドポイント、DynamoDB連携エンドポイントが含まれます。
- `requirements.txt`: このFastAPIアプリケーションが依存するPythonパッケージのリストです。
- `Dockerfile`: アプリケーションをDockerコンテナとしてビルドするための定義ファイルです。

## ローカルでの実行

開発目的で、Dockerなしでローカル環境でFastAPIアプリケーションを直接実行することができます。

### 前提条件

- Python 3.9+

### セットアップ

1.  このディレクトリに移動します。
    ```bash
    cd api
    ```

2.  Pythonの仮想環境を作成し、依存関係をインストールします。
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

### 実行

1.  仮想環境をアクティブ化します。
    ```bash
    source .venv/bin/activate
    ```

2.  Uvicornを使ってFastAPIアプリケーションを起動します。
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8080
    ```
    `--reload` オプションは、コード変更時に自動的にサーバーを再起動します。

3.  ブラウザで `http://localhost:8080` にアクセスすると、FastAPIの動作を確認できます。

### Dockerを使ったローカル実行 (オプション)

Dockerがインストールされていれば、コンテナとしてローカルで実行することもできます。

1.  このディレクトリにいることを確認します。
    ```bash
    pwd # `api` ディレクトリであることを確認
    ```

2.  Dockerイメージをビルドします。
    ```bash
    docker build -t fastapi-app:latest .
    ```

3.  Dockerコンテナを実行します。
    S3やDynamoDBとの連携部分は、ローカル実行では直接動作しない可能性があります。
    ```bash
    docker run -p 8000:80 fastapi-app:latest
    ```

4.  ブラウザで `http://localhost:8000` にアクセスすると、FastAPIの動作を確認できます。