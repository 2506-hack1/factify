
# Factify インフラストラクチャ

このプロジェクトはAWS CDKを使用してFactifyのインフラを管理します。

## セットアップ
```bash
# 依存関係のインストール
poetry install
```

### Makefileを使用する場合

```bash
# 依存関係のインストール
make install

# テストの実行
make test

# CloudFormationテンプレートの合成
make synth

# スタックのデプロイ
make deploy

# スタックの削除
make destroy
```

### 環境変数のカスタマイズ

```bash
# AWS プロファイルを指定
make deploy PROFILE=myprofile

# AWS リージョンを指定
make deploy REGION=us-west-2

# スタック名を指定
make deploy STACK_NAME=my-stack

# 追加のCDKオプションを指定
make deploy CDK_OPTS="--require-approval never"
```

## 便利なコマンド

 * `make list`        すべてのスタックをリストアップ
 * `make synth`       CloudFormationテンプレートを生成
 * `make deploy`      スタックをデプロイ
 * `make diff`        デプロイされたスタックと現在の状態を比較
 * `make destroy`     スタックを削除
 * `make bootstrap`   CDK環境をブートストラップ
