.DEFAULT_GOAL := help

HOST ?= 127.0.0.1
PORT ?= 8000

run: ## Run the application using uvicorn with provided arguments or defaults
	poetry run uvicorn main:app --host $(HOST) --port $(PORT) --reload

migrations: ## Make migrations using alembic
	@echo "Make migrations $(MESSAGE)"
	alembic revision --autogenerate -m "$(MESSAGE)"

migrate: ## Apply migrations using alembic
	@echo "Migrations apply"
	alembic upgrade head

help: ## Show this help message
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands: "
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $1, $2}'