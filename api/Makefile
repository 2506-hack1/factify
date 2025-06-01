# Makefile for FastAPI Application
# Basic commands for development workflow

# Variables
VENV = .venv
PYTHON = python3
PIP = pip
UVICORN = uvicorn
APP = main:app
PORT = 8001
HOST = 0.0.0.0

# Default target
.PHONY: help
help:
	@echo "利用可能なコマンド:"
	@echo "  make setup        - 仮想環境を作成し、依存関係をインストールします"
	@echo "  make install      - 依存関係をインストールします"
	@echo "  make start        - 開発サーバーを起動します (ポート: $(PORT))"
	@echo "  make dev          - 開発サーバーをホットリロードモードで起動します"
	@echo "  make clean        - 仮想環境とキャッシュファイルを削除します"
	@echo "  make test-upload  - サンプルファイルをアップロードするテストを実行します"
	@echo "  make test-list    - ファイル一覧を取得するテストを実行します"

# Setup virtual environment and install dependencies
.PHONY: setup
setup:
	@echo "仮想環境をセットアップしています..."
	$(PYTHON) -m venv $(VENV)
	@echo "依存関係をインストールしています..."
	. $(VENV)/bin/activate && $(PIP) install -r requirements.txt
	@echo "セットアップ完了！"

# Install dependencies
.PHONY: install
install:
	@echo "依存関係をインストールしています..."
	$(PIP) install -r requirements.txt
	@echo "インストール完了！"

# Start development server
.PHONY: start
start:
	@echo "サーバーを起動しています..."
	$(UVICORN) $(APP) --host $(HOST) --port $(PORT)

# Start development server with hot reload
.PHONY: dev
dev:
	@echo "開発サーバーを起動しています（ホットリロード有効）..."
	$(UVICORN) $(APP) --host $(HOST) --port $(PORT) --reload

# Clean up virtual environment and cache files
.PHONY: clean
clean:
	@echo "キャッシュファイルを削除しています..."
	rm -rf __pycache__
	rm -rf .pytest_cache
	@echo "仮想環境を削除しています..."
	rm -rf $(VENV)
	@echo "クリーンアップ完了！"

# Test uploading a sample file
.PHONY: test-upload
test-upload:
	@echo "サンプルファイルをアップロードしています..."
	@if [ ! -f "../sample.txt" ]; then \
		echo "sample.txt が見つかりません。作成します..."; \
		echo "これはサンプルテキストファイルです。\n\nFactifyプロジェクトのテスト用に作成されました。" > ../sample.txt; \
	fi
	curl -X POST "http://$(HOST):$(PORT)/upload/file" \
		-H "Content-Type: multipart/form-data" \
		-F "file=@../sample.txt;type=text/plain" \
		-F "title=サンプルテキスト" \
		-F "description=テスト用のサンプルファイル"

# Test listing all files
.PHONY: test-list
test-list:
	@echo "ファイル一覧を取得しています..."
	curl -X GET "http://$(HOST):$(PORT)/files/"

# Run the debug scripts
.PHONY: debug-api
debug-api:
	@echo "APIデバッグツールを実行しています..."
	python3 debug/api_test.py

.PHONY: debug-s3-dynamo
debug-s3-dynamo:
	@echo "S3/DynamoDBデバッグツールを実行しています..."
	python3 debug/s3_dynamodb_debug.py
