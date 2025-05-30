.PHONY: setup app infra help

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

infra-setup:
	cd infra && poetry install

infra-test:
	cd infra && make test

infra-synth:
	cd infra && make synth

infra-deploy:
	cd infra && make deploy

infra-destroy:
	cd infra && make destroy
