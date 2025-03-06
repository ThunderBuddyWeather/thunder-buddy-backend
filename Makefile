.PHONY: help test test-unit test-integration test-regression lint coverage clean install dev-env yamlint yamlint-fix swagger setup start stop restart rebuild rebuild-dev start-dev restart-dev

# Platform detection
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
    SHELL_EXT := bat
else
    DETECTED_OS := $(shell uname -s)
    ifeq ($(DETECTED_OS),Darwin)
        DETECTED_OS := MacOS
    endif
    ifeq ($(DETECTED_OS),Linux)
        DETECTED_OS := Linux
    endif
    SHELL_EXT := sh
endif

# Default target when just running 'make'
help:
	@echo "Available commands:"
	@echo "  make install           - Install Python dependencies"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-regression  - Run regression tests only"
	@echo "  make lint             - Run linting checks"
	@echo "  make coverage         - Run tests with coverage report"
	@echo "  make clean            - Remove Python file artifacts"
	@echo "  make dev-env          - Set up development environment"
	@echo "  make setup            - Run the setup.py script to configure the development environment"
	@echo "  make yamlint          - Run YAML linting"
	@echo "  make yamlint-fix      - Auto-fix YAML formatting issues"
	@echo "  make swagger          - Generate Swagger/OpenAPI specification"
	@echo "  make start            - Start the application"
	@echo "  make stop             - Stop the application"
	@echo "  make restart          - Restart the application"
	@echo "  make start-dev        - Start in development mode"
	@echo "  make restart-dev      - Restart the application in development mode"
	@echo "  make rebuild          - Rebuild and start the application"
	@echo "  make rebuild-dev      - Rebuild and start in development mode"
	@echo ""
	@echo "Detected OS: $(DETECTED_OS)"

# Install dependencies
install:
	pip install -r requirements.txt

# Run all tests
test:
	@echo "Checking if database is running..."
	@if ! docker ps | grep -q thunder-buddy-db; then \
		echo "Starting database container for integration tests..."; \
		docker-compose up -d db; \
		echo "Waiting for database to be ready..."; \
		sleep 5; \
	else \
		echo "Database container is already running."; \
	fi
	@echo "Running tests with DATABASE_URL set for integration tests..."
	PYTHONPATH=. DATABASE_URL="postgresql://thunderbuddy:localdev@localhost:5432/thunderbuddy" python -m pytest -v

# Run unit tests only
test-unit:
	PYTHONPATH=. python -m pytest tests/unit/ -v -m "not integration"

# Run integration tests only
test-integration:
	@echo "Checking if database is running..."
	@if ! docker ps | grep -q thunder-buddy-db; then \
		echo "Starting database container for integration tests..."; \
		docker-compose up -d db; \
		echo "Waiting for database to be ready..."; \
		sleep 5; \
	else \
		echo "Database container is already running."; \
	fi
	@echo "Running integration tests with DATABASE_URL set..."
	PYTHONPATH=. DATABASE_URL="postgresql://thunderbuddy:localdev@localhost:5432/thunderbuddy" python -m pytest tests/integration/ -v -m integration

# Run regression tests only
test-regression:
	@echo "Checking if database is running..."
	@if ! docker ps | grep -q thunder-buddy-db; then \
		echo "Starting database container for regression tests..."; \
		docker-compose up -d db; \
		echo "Waiting for database to be ready..."; \
		sleep 5; \
	else \
		echo "Database container is already running."; \
	fi
	@echo "Running regression tests..."
	PYTHONPATH=. DATABASE_URL="postgresql://thunderbuddy:localdev@localhost:5432/thunderbuddy" python -m pytest -v -m regression

# Run linting
lint:
	flake8 --config=.flake8 .
	pylint --ignore=venv,env,.venv,.env,build,dist --rcfile=.pylintrc **/*.py

# Auto-fix linting issues where possible
lint-fix:
	black . --line-length 88
	isort . --profile black --line-length 88

# Run tests with coverage
coverage:
	@echo "Checking if database is running..."
	@if ! docker ps | grep -q thunder-buddy-db; then \
		echo "Starting database container for tests..."; \
		docker-compose up -d db; \
		echo "Waiting for database to be ready..."; \
		sleep 5; \
	else \
		echo "Database container is already running."; \
	fi
	@echo "Running tests with coverage report..."
	PYTHONPATH=. DATABASE_URL="postgresql://thunderbuddy:localdev@localhost:5432/thunderbuddy" python -m pytest --cov=app --cov=run tests/ --cov-report=html

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

# Run the setup.py script to configure the development environment
setup:
	python setup.py

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

# Cross-platform app management targets
start:
	@echo "Starting application on $(DETECTED_OS)..."
	@if [ "$(DETECTED_OS)" = "Windows" ]; then \
		bin/start.bat; \
	else \
		./bin/start.sh; \
	fi

stop:
	@echo "Stopping application on $(DETECTED_OS)..."
	@if [ "$(DETECTED_OS)" = "Windows" ]; then \
		bin/stop.bat; \
	else \
		./bin/stop.sh; \
	fi

restart:
	@echo "Restarting application on $(DETECTED_OS)..."
	@if [ "$(DETECTED_OS)" = "Windows" ]; then \
		bin/restart.bat; \
	else \
		./bin/restart.sh; \
	fi

start-dev:
	@echo "Starting development mode on $(DETECTED_OS)..."
	@if [ "$(DETECTED_OS)" = "Windows" ]; then \
		bin/start-dev.bat; \
	else \
		./bin/start-dev.sh; \
	fi

restart-dev:
	@echo "Restarting application in development mode on $(DETECTED_OS)..."
	@if [ "$(DETECTED_OS)" = "Windows" ]; then \
		bin/restart-dev.bat; \
	else \
		./bin/restart-dev.sh; \
	fi

rebuild:
	@echo "Rebuilding application on $(DETECTED_OS)..."
	@if [ "$(DETECTED_OS)" = "Windows" ]; then \
		bin/rebuild.bat; \
	else \
		./bin/rebuild.sh; \
	fi

rebuild-dev:
	@echo "Rebuilding and starting development mode on $(DETECTED_OS)..."
	@if [ "$(DETECTED_OS)" = "Windows" ]; then \
		bin/rebuild-dev.bat; \
	else \
		./bin/rebuild-dev.sh; \
	fi
