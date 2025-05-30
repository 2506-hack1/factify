.PHONY: install test synth deploy destroy bootstrap help

# デフォルトのターゲット
.DEFAULT_GOAL := help

# 環境変数
CDK_OPTS ?=
PROFILE ?=
REGION ?= ap-northeast-1
STACK_NAME ?= factify-stack

# プロファイル設定がある場合は追加
ifdef PROFILE
	PROFILE_OPT = --profile $(PROFILE)
else
	PROFILE_OPT =
endif

# リージョン設定
REGION_OPT = --region $(REGION)

# インストール
install: ## 依存関係をインストールする
	poetry install

# テスト
test: ## ユニットテストを実行する
	poetry run pytest

# CDKコマンド
synth: ## CloudFormation テンプレートを合成する
	poetry run cdk synth $(STACK_NAME) $(CDK_OPTS) $(PROFILE_OPT) $(REGION_OPT)

deploy: ## スタックをデプロイする
	poetry run cdk deploy $(STACK_NAME) $(CDK_OPTS) $(PROFILE_OPT) $(REGION_OPT)

destroy: ## スタックを削除する
	poetry run cdk destroy $(STACK_NAME) $(CDK_OPTS) $(PROFILE_OPT) $(REGION_OPT)

bootstrap: ## CDK環境をブートストラップする
	poetry run cdk bootstrap $(PROFILE_OPT) $(REGION_OPT)

list: ## スタック一覧を表示する
	poetry run cdk list $(PROFILE_OPT) $(REGION_OPT)

diff: ## デプロイされるスタックの変更点を表示する
	poetry run cdk diff $(STACK_NAME) $(PROFILE_OPT) $(REGION_OPT)

# ヘルプ
help: ## このヘルプメッセージを表示する
	@echo "使用方法:"
	@echo "  make [target] [options]"
	@echo ""
	@echo "オプション:"
	@echo "  PROFILE=profile-name  AWS CLIプロファイルを指定する"
	@echo "  REGION=region-name    AWSリージョンを指定する (デフォルト: ap-northeast-1)"
	@echo "  STACK_NAME=name       スタック名を指定する (デフォルト: factify-stack)"
	@echo "  CDK_OPTS=\"options\"    CDKコマンドに追加オプションを渡す"
	@echo ""
	@echo "利用可能なターゲット:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'
