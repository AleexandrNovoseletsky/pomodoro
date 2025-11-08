.DEFAULT_GOAL := help

HOST ?= 127.0.0.1
PORT ?= 8000

run: ## Run the application using uvicorn with provided arguments or defaults
	poetry run uvicorn app.main:app --host $(HOST) --port $(PORT) --reload

migrations: ## Make migrations using alembic
	@echo "Make migrations $(MESSAGE)"
	alembic revision --autogenerate -m "$(MESSAGE)"

migrate: ## Apply migrations using alembic
	@echo "Migrations apply"
	alembic upgrade head

structure: ## Save project structure to a file using tree
	@echo "Save project structure to structure.txt"
	poetry run tree -L 3 -I ".git|.__*|__pycache__|.venv|alembic/versions" > structure.txt

help: ## Show this help message
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands: "
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $1, $2}'

e2e: ## Run e2e smoke tests (requires app running and DB migrated)
	PYTHONPATH=. python scripts/e2e.py