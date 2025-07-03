# Shuup Makefile - Common development tasks
#
# This Makefile provides convenient shortcuts for common development tasks
# using the modern uv and hatchling workflow.

.PHONY: help install dev-install clean requirements build test lint format docs docker

# Default target
help:
	@echo "Shuup Development Commands:"
	@echo "  make install          - Install the package for development"
	@echo "  make dev-install      - Install development dependencies"
	@echo "  make requirements     - Regenerate all requirements files"
	@echo "  make clean           - Clean build artifacts"
	@echo "  make build           - Build the package (wheel and sdist)"
	@echo "  make test            - Run tests"
	@echo "  make lint            - Run linting (flake8, ruff, mypy)"
	@echo "  make format          - Format code (black, isort)"
	@echo "  make docs            - Build documentation"
	@echo "  make docker          - Build Docker images"
	@echo "  make pre-commit      - Install and run pre-commit hooks"

# Installation targets
install:
	uv pip install -e .

dev-install:
	uv pip sync requirements-dev.txt
	uv pip install -e .

# Requirements generation
requirements:
	@echo "Regenerating requirements files from pyproject.toml..."
	./regenerate_requirements.sh
	@echo "✓ Requirements files updated"

# Build targets
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

build: clean requirements
	@echo "Building package..."
	uv build
	@echo "✓ Package built successfully"

# Testing targets
test:
	uv run pytest shuup_tests -v --tb=short --cov=shuup --cov-report=html --cov-report=term

test-fast:
	uv run pytest shuup_tests -x --tb=short

# Code quality targets
lint:
	@echo "Running linting tools..."
	uv run flake8 . --max-line-length=120 --ignore=E203,W503,E501 --exclude=migrations,venv,.venv,.git,.tox,dist,doc,*egg,build,node_modules,shuup_tests
	uv run ruff check .
	uv run mypy shuup --ignore-missing-imports --follow-imports=silent
	@echo "✓ Linting completed"

format:
	@echo "Formatting code..."
	uv run black . --line-length=120 --exclude=migrations/
	uv run isort . --profile=black --line-length=120
	@echo "✓ Code formatted"

# Documentation targets
docs:
	@echo "Building documentation..."
	cd doc && uv run make html
	@echo "✓ Documentation built in doc/_build/html/"

# Docker targets
docker:
	@echo "Building Docker images..."
	docker build -t shuup:latest .
	docker build -f Dockerfile.uv -t shuup:uv .
	@echo "✓ Docker images built"

docker-dev:
	docker-compose -f docker-compose.uv.yml up --build

# Development setup targets
pre-commit:
	uv run pre-commit install
	uv run pre-commit run --all-files

setup-dev: dev-install pre-commit
	@echo "✓ Development environment set up"
	@echo "  - Dependencies installed"
	@echo "  - Pre-commit hooks installed"
	@echo "  - Ready for development!"

# Database targets (using Django tasks)
migrate:
	uv run shuup_workbench migrate --settings=shuup_workbench.settings.dev

makemigrations:
	uv run shuup_workbench makemigrations --settings=shuup_workbench.settings.dev

runserver:
	uv run shuup_workbench runserver 0.0.0.0:8000 --settings=shuup_workbench.settings.dev

shell:
	uv run shuup_workbench shell --settings=shuup_workbench.settings.dev

# Release preparation
check-release: requirements lint test build
	@echo "✓ Release checks passed"
	@echo "  - Requirements files are up-to-date"
	@echo "  - Code quality checks passed"
	@echo "  - Tests passed"
	@echo "  - Package builds successfully"

# CI/CD targets
ci-install:
	uv pip install -e .
	uv pip sync requirements-dev-ci.txt

ci-test: ci-install
	uv run pytest shuup_tests --tb=short --cov=shuup --cov-report=xml

ci-lint: ci-install
	uv run flake8 . --max-line-length=120 --ignore=E203,W503,E501 --exclude=migrations,venv,.venv,.git,.tox,dist,doc,*egg,build,node_modules,shuup_tests
	uv run ruff check .

ci-requirements-check:
	@echo "Checking if requirements files are up-to-date..."
	./regenerate_requirements.sh
	@if ! git diff --quiet requirements*.txt; then \
		echo "❌ Requirements files are out of date!"; \
		echo "Run 'make requirements' and commit the changes."; \
		git diff requirements*.txt; \
		exit 1; \
	fi
	@echo "✓ Requirements files are up-to-date"
