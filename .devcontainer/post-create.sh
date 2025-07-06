#!/bin/bash
# DevContainer Post-Create Script for Shuup

set -e

echo "🚀 Setting up Shuup development environment..."

# Install UV if not available
if ! command -v uv &> /dev/null; then
    echo "📦 Installing UV (fast Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment with UV
if [ ! -d ".venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    uv venv .venv --python 3.9
else
    echo "🐍 Virtual environment already exists, skipping creation."
fi

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies with UV
echo "📦 Installing Python dependencies with UV..."
uv sync --dev

# Install Shuup in development mode
echo "🛠️  Installing Shuup in development mode..."
uv pip install -e .


# Install Node.js dependencies
if [ -f "package.json" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Set up pre-commit hooks (if available)
if command -v pre-commit &> /dev/null; then
    echo "🔗 Setting up pre-commit hooks..."

    pre-commit install
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Django settings
DJANGO_SETTINGS_MODULE=shuup_workbench.settings.dev
DEBUG=1
SECRET_KEY=dev-secret-key-please-change-in-production

# Database (SQLite for development)
DATABASE_URL=sqlite:///./shuup.sqlite3

# Cache
CACHE_URL=locmem://

# Media and Static files
MEDIA_URL=/media/
STATIC_URL=/static/

# Email (Console backend for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Logging
LOG_LEVEL=DEBUG
EOF
fi

# Create Django media and static directories
mkdir -p media static

# Run initial Django setup
echo "🗄️  Setting up Django database..."
uv run shuup_workbench migrate --settings=shuup_workbench.settings.dev

# Collect static files
echo "📁 Collecting static files..."
uv run shuup_workbench collectstatic --noinput --settings=shuup_workbench.settings.dev


echo "✅ Shuup development environment setup complete!"
echo ""
echo "🎯 Quick start commands:"
echo "  - Start development server: uv run shuup_workbench runserver 0.0.0.0:8000"
echo "  - Run tests: pytest"
echo "  - Access admin: http://localhost:8000/admin (admin/admin)"
echo ""
echo "🛠️  Makefile shortcuts (run with 'make <target>'):"
echo "  make install         - Install the package for development"
echo "  make dev-install     - Install development dependencies"
echo "  make requirements    - Regenerate all requirements files"
echo "  make clean           - Clean build artifacts"
echo "  make build           - Build the package (wheel and sdist)"
echo "  make test            - Run tests"
echo "  make lint            - Run linting (flake8, ruff, mypy)"
echo "  make format          - Format code (black, isort)"
echo "  make docs            - Build documentation"
echo "  make docker          - Build Docker images"
echo "  make pre-commit      - Install and run pre-commit hooks"
echo "  make migrate         - Run Django migrations"
echo "  make makemigrations  - Create new Django migrations"
echo "  make runserver       - Start Django development server"
echo "  make shell           - Open Django shell"
