.PHONY: help install test test-cov test-verbose lint format type-check clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install package with dev dependencies"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make test-verbose - Run tests with verbose output"
	@echo "  make lint         - Run linting (flake8)"
	@echo "  make format       - Format code with black"
	@echo "  make format-check - Check code formatting"
	@echo "  make type-check   - Run type checking (mypy)"
	@echo "  make clean        - Clean up generated files"
	@echo "  make ci           - Run all CI checks locally"

install:
	pip install -e ".[dev]"

test:
	pytest

test-cov:
	pytest --cov=playlist_transfer --cov-report=html --cov-report=term-missing
	@echo "\nCoverage report generated in htmlcov/index.html"

test-verbose:
	pytest -v

lint:
	flake8 playlist_transfer tests

format:
	black playlist_transfer tests

format-check:
	black --check playlist_transfer tests

type-check:
	mypy playlist_transfer --ignore-missing-imports

clean:
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

ci: format-check lint type-check test-cov
	@echo "\n✅ All CI checks passed!"
