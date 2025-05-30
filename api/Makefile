.PHONY: run dev format lint check install clean help

# デフォルトのターゲット
.DEFAULT_GOAL := help

# 変数定義
PORT ?= 8000
HOST ?= 127.0.0.1
RELOAD ?= --reload
APP_MODULE = src.factify:app

run:
	poetry run uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT) $(RELOAD)

prod:
	poetry run uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT)

format:
	poetry run ruff format src/ tests/

lint:
	poetry run ruff check src/ tests/

fix:
	poetry run ruff check --fix src/ tests/

install:
	poetry install
	# pre-commitフックはルートディレクトリで管理されています

# pycacheファイルなどをクリーン
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
