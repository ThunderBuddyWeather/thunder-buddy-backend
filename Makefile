.PHONY: help test test-unit test-integration lint coverage clean install dev-env yamlint yamlint-fix swagger

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
	@echo "  make yamlint          - Run YAML linting"
	@echo "  make yamlint-fix      - Auto-fix YAML formatting issues"
	@echo "  make swagger          - Generate Swagger/OpenAPI specification"

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
	flake8 .
	pylint --ignore=venv,env,.venv,.env,build,dist --rcfile=.pylintrc **/*.py

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

# Run YAML linting
yamlint:
	pip install yamllint
	yamllint .

# Auto-fix YAML formatting (macOS compatible)
yamlint-fix:
	pip install yamllint
	# First, ensure all YAML files end with newline
	find . -name "*.yml" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./env/*" -not -path "./node_modules/*" -exec sh -c 'printf "%s\n" "$$(cat "{}")" > "{}"' \;
	# Remove trailing spaces
	find . -name "*.yml" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./env/*" -not -path "./node_modules/*" -exec sed -i '' -E 's/[[:space:]]*$$//' {} \;
	# Add document start marker if missing
	find . -name "*.yml" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./env/*" -not -path "./node_modules/*" -exec sh -c 'if ! grep -q "^---" "{}"; then printf -- "---\n%s" "$$(cat "{}")" > "{}"; fi' \;
	# Run yamllint to check remaining issues
	yamllint -f parsable .

# Generate Swagger/OpenAPI specification
swagger:
	@echo "Generating Swagger specification..."
	@mkdir -p static
	@if [ -f .env.local ]; then \
		echo "Using .env.local for configuration"; \
	else \
		echo "Warning: .env.local not found, using default .env"; \
	fi
	@# Check if we're in a virtual environment already (CI environments often are)
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		echo "Using active virtual environment"; \
		python scripts/generate_swagger.py; \
	elif [ -f venv/bin/activate ]; then \
		echo "Activating local virtual environment"; \
		. venv/bin/activate && python scripts/generate_swagger.py; \
	else \
		echo "No virtual environment found, running directly"; \
		python scripts/generate_swagger.py; \
	fi
