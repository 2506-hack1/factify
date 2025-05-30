
# Factify インフラストラクチャ

このプロジェクトはAWS CDKを使用してFactifyのインフラを管理します。

## セットアップ

### Poetry を使用したセットアップ (推奨)

このプロジェクトはPoetryを使用して依存関係を管理しています。まだPoetryがインストールされていない場合は、[Poetry公式サイト](https://python-poetry.org/docs/#installation)の手順に従ってインストールしてください。

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

## 従来の方法（非推奨）

以前は `pip` と `requirements.txt` を使用していましたが、現在はPoetryに移行しています。
従来の方法を使用する場合は以下のコマンドを実行できます（ただし、今後は非推奨となります）：

```bash
# 仮想環境の作成と有効化
python3 -m venv .venv
source .venv/bin/activate  # Windowsの場合: .venv\Scripts\activate.bat

# 依存関係のインストール
pip install -r requirements.txt
pip install -r requirements-dev.txt

# CloudFormationテンプレートの合成
cdk synth
```

## 便利なコマンド

 * `make list`        すべてのスタックをリストアップ
 * `make synth`       CloudFormationテンプレートを生成
 * `make deploy`      スタックをデプロイ
 * `make diff`        デプロイされたスタックと現在の状態を比較
 * `make destroy`     スタックを削除
 * `make bootstrap`   CDK環境をブートストラップ
