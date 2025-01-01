.PHONY: lint test

lint:
	@echo "Linting the code"
	@echo "Formatting with isort"
	poetry run isort ./python_snaptime ./tests
	@echo "Formatting with Ruff"
	poetry run ruff format ./python_snaptime ./tests
	@echo "Cleaning with pycln"
	poetry run pycln --all ./python_snaptime ./tests

test:
	@echo "Running tests"
	poetry run pytest --cov=python_snaptime
	poetry run coverage html
