#!/bin/bash
# DevContainer Post-Start Script for Shuup

set -e

echo "🔄 Running post-start setup..."

# Activate virtual environment
source .venv/bin/activate

# Update PATH to include UV
export PATH="$HOME/.cargo/bin:$PATH"

# Check if database needs migration
echo "🗄️  Checking database migrations..."
if python manage.py showmigrations --plan --settings=shuup_workbench.settings.dev | grep -q '\[ \]'; then
    echo "🔄 Running pending migrations..."
    python manage.py migrate --settings=shuup_workbench.settings.dev
else
    echo "✅ Database is up to date"
fi

# Start background services (if needed)
# Uncomment the following if you need background services

# echo "🚀 Starting background services..."
# python manage.py runserver 0.0.0.0:8000 --settings=shuup_workbench.settings.dev &

echo "✅ Post-start setup complete!"
echo "🎯 Development server ready at http://localhost:8000"
