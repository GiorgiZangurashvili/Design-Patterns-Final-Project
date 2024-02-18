.PHONY: help
.DEFAULT_GOAL := help

help:
	python -m bitcoin_wallet --help

install: ## Install requirements
	pip install -r requirements.txt

format: ## Run code formatters
	isort bitcoin_wallet
	black bitcoin_wallet

lint: ## Run code linters
	isort --check bitcoin_wallet
	black --check bitcoin_wallet
	flake8 bitcoin_wallet
	mypy bitcoin_wallet
