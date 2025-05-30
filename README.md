# factify

## setup
開発開始時に必ず行ってください。

### 依存関係をインストールする
```sh
# 依存関係のインストール
poetry install

# pre-commitフックをインストールする
poetry run pre-commit install
```

## formatting
### 手動でRuffを実行する

```sh
# コードをフォーマットする
poetry run ruff format src/ tests/

# リンティングを実行する
poetry run ruff check src/ tests/

# 自動修正可能な問題を修正する
poetry run ruff check --fix src/ tests/
```
