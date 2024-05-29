SOURCE_DIR = ./crawlinsta

.PHONY: clean help

help:
	clear;
	@echo "================= Usage =================";
	@echo "clean                  : Remove autogenerated folders";
	@echo "clean-pyc              : Remove python artifacts."
	@echo "clean-build            : Remove build artifacts."
	@echo "install                : Install all dependencies and the package itself."
	@echo "bandit                 : Run bandit security analysis.";
	@echo "mypy                   : Run mypy type checking.";
	@echo "flake8                 : Run flake8 linting.";
	@echo "test                   : Run tests and generate coverage report.";
	@echo "unit_test              : Run unit tests and generate coverage report.";
	@echo "build                  : Build a python wheel package.";

# Clean the folder from build/test related folders
clean: clean-build clean-pyc
	rm -rf .mypy_cache/ .pytest_cache/
	rm -f .coverage

clean-pyc:
	find . \( -name '*.pyc' -o -name '*.pyo' \) -exec rm -rf {} +

clean-build:
	rm -rf build/ dist/ *.egg-info

# Install development dependencies
install:
	poetry install --with dev,test,docs

# Install and run bandit security analysis
bandit:
	poetry run bandit -r $(SOURCE_DIR)

# Install and run mypy type checking
mypy:
	poetry run mypy $(SOURCE_DIR)

# Install and run flake8 linting
flake8:
	poetry run flake8 $(SOURCE_DIR)

# Install requirements for testing and run tests
test:
	poetry run pytest

# Install requirements for testing and run unit tests
unit_test:
	poetry run pytest tests/unit_tests

# build wheel package
build:
	poetry build -f wheel