.PHONY: setup app help

.DEFAULT_GOAL := help

setup:
	pip install pre-commit
	pre-commit install

app-setup:
	cd app && poetry install

app-run:
	cd app && make run

app-format:
	cd app && make format

app-lint:
	cd app && make lint
