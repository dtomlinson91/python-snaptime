.PHONY: lint test

lint:
	@echo "Linting the code"
	@echo "Formatting with isort"
	poetry run isort ./python_snaptime
	@echo "Formatting with Ruff"
	poetry run ruff format ./python_snaptime
	@echo "Cleaning with pycln"
	poetry run pycln --all ./python_snaptime

test:
	@echo "Running tests"
	poetry run pytest --cov=python_snaptime
	poetry run coverage html
