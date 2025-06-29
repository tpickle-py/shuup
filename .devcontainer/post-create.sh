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
echo "🐍 Creating Python virtual environment with UV..."
uv venv .venv --python 3.9

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip and install UV in venv
echo "📦 Installing UV in virtual environment..."
uv pip install uv

# Install Python dependencies with UV
echo "📦 Installing Python dependencies with UV..."
uv pip sync requirements-dev.txt

# Install Shuup in development mode
echo "🛠️  Installing Shuup in development mode..."
uv pip install -e .

# Install additional development tools
echo "🔧 Installing additional development tools..."
uv pip install \
    black \
    isort \
    flake8 \
    pylint \
    mypy \
    pytest \
    pytest-cov \
    pytest-django \
    pylint-django \
    django-debug-toolbar \
    django-extensions

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
python manage.py migrate --settings=shuup_workbench.settings.dev

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --settings=shuup_workbench.settings.dev

# Create superuser (optional)
echo "👤 Creating Django superuser (admin/admin)..."
python manage.py shell --settings=shuup_workbench.settings.dev << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print("Superuser 'admin' created with password 'admin'")
else:
    print("Superuser 'admin' already exists")
EOF

echo "✅ Shuup development environment setup complete!"
echo ""
echo "🎯 Quick start commands:"
echo "  - Start development server: python manage.py runserver 0.0.0.0:8000"
echo "  - Run tests: pytest"
echo "  - Access admin: http://localhost:8000/admin (admin/admin)"
echo "  - Format code: black ."
echo "  - Sort imports: isort ."
echo "  - Lint code: flake8 ."
