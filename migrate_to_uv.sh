#!/bin/bash
# Migration script to uv

echo "🚀 Migrating to uv..."

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

echo "📦 Creating virtual environment with uv..."
uv venv .venv --python 3.11

echo "📚 Installing dependencies..."
uv sync --dev

echo "🔧 Setting up pre-commit..."
uv run pre-commit install

echo "✅ Migration complete!"
echo ""
echo "To activate the environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To run commands with uv:"
echo "  uv run python -m shuup_workbench runserver"
echo "  uv run pytest"
echo "  uv run black ."
echo "  uv run isort ."
echo "  uv run flake8 ."
