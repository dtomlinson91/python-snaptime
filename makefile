.PHONY: lint test changelog

lint:
	@echo "Linting the code"
	@echo "Fixing lint errors with Ruff"
	uv run ruff check --fix ./python_snaptime ./tests
	@echo "Formatting with Ruff"
	uv run ruff format ./python_snaptime ./tests

test:
	@echo "Running tests"
	uv run pytest --cov=python_snaptime
	uv run coverage html

changelog:
	@echo "Generating changelog"
	git cliff > CHANGELOG.md
