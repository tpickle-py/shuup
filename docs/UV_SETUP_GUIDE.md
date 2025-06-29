# UV Setup Guide for Shuup

This guide explains how to set up the development environment using `uv`, a fast Python package installer and resolver.

## What is UV?

UV is a fast Python package installer and resolver written in Rust, designed to be a drop-in replacement for pip and pip-tools. It's significantly faster than traditional Python package managers and provides better dependency resolution.

## Prerequisites

- Python 3.8 or newer (Python 3.11 recommended)
- Git

## Installation

### Install UV

```bash
# Install UV using the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv

# Or using homebrew (macOS)
brew install uv
# UV Setup Guide for Shuup

This guide explains how to set up the development environment using `uv`, a fast Python package installer and resolver.

## What is UV?

UV is a fast Python package installer and resolver written in Rust, designed to be a drop-in replacement for pip and pip-tools. It's significantly faster than traditional Python package managers and provides better dependency resolution.

## Prerequisites

- Python 3.8 or newer (Python 3.11 recommended)
- Git

## Installation

### Install UV

```bash
# Install UV using the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv

# Or using homebrew (macOS)
brew install uv
```

### Verify Installation

```bash
uv --version
```

## Project Setup with UV

### Quick Setup

Run the migration script for automated setup:

```bash
./migrate_to_uv.sh
```

### Manual Setup

If you prefer manual setup:

```bash
# Create virtual environment with Python 3.11
uv venv .venv --python 3.11

# Install all dependencies including dev dependencies
uv sync --dev

# Optional: Activate the environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

## Development Commands

Use `uv run` to execute commands without activating the virtual environment:

```bash
# Run the development server
uv run shuup_workbench runserver 0.0.0.0:8000 --settings=shuup_workbench.settings.dev

# Run tests
uv run pytest shuup_tests -v --tb=short

# Code formatting and linting
uv run black .
uv run isort .
uv run flake8 .
uv run mypy shuup

# Run specific Django commands
uv run shuup_workbench makemigrations
uv run shuup_workbench migrate
uv run shuup_workbench collectstatic --noinput
uv run shuup_workbench shell
```

## VS Code Integration

The project includes VS Code tasks that use `uv`:

### Tasks

Use the Command Palette (Ctrl+Shift+P) to run:

- `Tasks: Run Task` → `UV: Create Virtual Environment`
- `Tasks: Run Task` → `UV: Install Dependencies`
- `Tasks: Run Task` → `Django: Run Development Server`
- `Tasks: Run Task` → `Django: Run Tests`

### Settings

The workspace is configured with:

- `python.packageManager` set to `"uv"`
- `python.defaultInterpreterPath` points to `./.venv/bin/python`
- Linting and formatting tools are configured

## Pre-commit Hooks

Set up pre-commit hooks to automatically format and lint code:

```bash
uv run pre-commit install
```

Now your code will be automatically formatted and checked before each commit.

## Dependency Management

### Adding Dependencies

```bash
# Add a runtime dependency
uv add package-name

# Add a development dependency  
uv add --dev package-name

# Add to a specific dependency group
uv add --group test pytest-mock
```

### Updating Dependencies

```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add package-name@latest

# Sync only production dependencies
uv sync --no-dev
```

### Dependency Groups

The project uses dependency groups defined in `pyproject.toml`:

- `dev`: All development tools (linting, formatting, testing, docs)
- `test`: Testing-specific dependencies
- `docs`: Documentation generation tools

Install specific groups:

```bash
uv sync --group dev
uv sync --group test
uv sync --group docs
```

## Python Version Management

The project supports Python 3.8-3.12. The default version is set in `.python-version`.

To use a different Python version:

```bash
uv venv .venv --python 3.10
uv sync --dev
```

## Benefits of UV

1. **Speed**: 10-100x faster than pip for many operations
2. **Reliability**: Consistent dependency resolution with lock files
3. **Modern**: Uses modern Python packaging standards (pyproject.toml)
4. **Compatible**: Works with existing requirements.txt files
5. **Isolation**: Better virtual environment management
6. **Memory Efficient**: Lower memory usage than pip

## Troubleshooting

### UV Command Not Found

```bash
# Add UV to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Or reinstall UV
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Virtual Environment Issues

```bash
# Clear cache and recreate environment
uv cache clean
rm -rf .venv
uv venv .venv --python 3.11
uv sync --dev
```

### Dependency Conflicts

```bash
# Force reinstall all packages
uv sync --reinstall

# Check installed packages
uv pip list
```

### Export Requirements (for deployment)

```bash
# Export production requirements
uv pip compile pyproject.toml -o requirements.txt

# Export dev requirements
uv pip compile pyproject.toml --extra dev -o requirements-dev.txt
```

## Migration from pip

If you were previously using pip:

1. Your existing `requirements*.txt` files are still supported
2. `uv sync` replaces `pip install -r requirements-dev.txt`
3. `uv add` replaces `pip install`
4. `uv run` eliminates the need to activate virtual environments
5. All your existing development workflows continue to work

## GitHub Actions Integration

The project's CI/CD pipeline uses UV for faster builds:

- Installs UV using `astral-sh/setup-uv@v4`
- Tests against Python 3.8, 3.9, 3.10, 3.11, and 3.12
- Uses `uv sync --dev` for dependency installation
- Runs all commands with `uv run`

This results in significantly faster CI/CD builds compared to pip.

## Additional Resources

- [UV Documentation](https://github.com/astral-sh/uv)
- [UV vs pip Performance](https://github.com/astral-sh/uv#performance)
- [Shuup Documentation](https://shuup.readthedocs.io/)
