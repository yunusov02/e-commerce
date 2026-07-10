PYTHON := uv run

.PHONY: format lint lint-fix type-check check

format:
	$(PYTHON) black .

lint:
	$(PYTHON) ruff check .

lint-fix:
	$(PYTHON) ruff check . --fix

type-check:
	$(PYTHON) mypy .

check: formatlint type-check



run:
	uvicorn app.main:app --reload --host localhost --port 8000




