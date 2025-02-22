.PHONY: help test test-unit test-integration lint coverage clean install dev-env

# Default target when just running 'make'
help:
	@echo "Available commands:"
	@echo "  make install           - Install Python dependencies"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make lint             - Run linting checks"
	@echo "  make coverage         - Run tests with coverage report"
	@echo "  make clean            - Remove Python file artifacts"
	@echo "  make dev-env          - Set up development environment"

# Install dependencies
install:
	pip install -r requirements.txt

# Run all tests
test:
	python -m pytest -v

# Run unit tests only
test-unit:
	python -m pytest tests/unit/ -v -m "not integration"

# Run integration tests only
test-integration:
	python -m pytest tests/integration/ -v -m integration

# Run linting
lint:
	flake8 . --max-line-length=88 --extend-ignore=E203,W503 --exclude=venv*,.venv,env,.env,.git,__pycache__,*.pyc,*.egg-info,build,dist --ignore=F401
	pylint --ignore=venv,env,.venv,.env,build,dist --disable=W0611,C0301 **/*.py

# Auto-fix linting issues where possible
lint-fix:
	black . --line-length 88
	isort . --profile black --line-length 88

# Run tests with coverage
coverage:
	python -m pytest --cov=. tests/ --cov-report=html

# Clean up Python artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Set up development environment
dev-env:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
