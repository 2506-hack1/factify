.PHONY: setup app help

# デフォルトのターゲット
.DEFAULT_GOAL := help

# セットアップ
setup: ## pre-commitフックをインストールします
	pip install pre-commit
	pre-commit install

# アプリ関連のコマンド
app-setup: ## アプリケーションの依存関係をインストールします
	cd app && poetry install

app-run: ## アプリケーションを実行します
	cd app && make run

app-format: ## アプリケーションのコードをフォーマットします
	cd app && make format

app-lint: ## アプリケーションのコードをリントします
	cd app && make lint

# ヘルプ
help: ## このヘルプメッセージを表示します
	@echo "使用方法:"
	@echo "  make [target]"
	@echo ""
	@echo "利用可能なターゲット:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'
