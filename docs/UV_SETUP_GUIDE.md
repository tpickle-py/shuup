# UV Setup Guide for Shuup

This guide explains how to set up and use UV (the fast Python package manager) with the Shuup project.

## What is UV?

UV is a fast Python package installer and resolver written in Rust, designed to be a drop-in replacement for pip and pip-tools. It's significantly faster than traditional Python package managers.

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

### 1. Create Virtual Environment

```bash
# Create a virtual environment with Python 3.9
uv venv .venv --python 3.9

# Activate the virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies

```bash
# Install all dependencies from requirements-dev.txt
uv pip sync requirements-dev.txt

# Install Shuup in development mode
uv pip install -e .
```

### 3. Install Additional Development Tools

```bash
# Install development tools
uv pip install black isort flake8 pylint mypy pytest pytest-cov pytest-django
```

## Daily Development Workflow

### Using UV with Virtual Environment

```bash
# Activate virtual environment
source .venv/bin/activate

# Install new package
uv pip install package-name

# Install package for development
uv pip install -e .

# Sync all dependencies (similar to pip-sync)
uv pip sync requirements-dev.txt

# Upgrade all packages
uv pip install --upgrade-strategy eager
```

### Running Common Tasks

```bash
# Start development server
python manage.py runserver --settings=shuup_workbench.settings.dev

# Run tests
pytest shuup_tests

# Format code
black .
isort .

# Lint code
flake8 .
pylint shuup

# Type checking
mypy shuup
```

## VS Code Integration

The project is configured to work seamlessly with UV:

### Settings
- `python.packageManager` is set to `"uv"`
- `python.defaultInterpreterPath` points to `./.venv/bin/python`
- Python linting and formatting tools are configured

### Tasks
Use the Command Palette (Ctrl+Shift+P) to run:
- `Tasks: Run Task` → `UV: Create Virtual Environment`
- `Tasks: Run Task` → `UV: Install Dependencies`
- `Tasks: Run Task` → `Django: Run Development Server`

### DevContainer
The devcontainer automatically:
- Installs UV
- Creates virtual environment
- Installs all dependencies
- Sets up Django database
- Configures VS Code settings

## Benefits of Using UV

1. **Speed**: UV is 10-100x faster than pip for many operations
2. **Reliability**: Better dependency resolution
3. **Compatibility**: Drop-in replacement for pip
4. **Memory Efficiency**: Lower memory usage
5. **Better Error Messages**: More informative error reporting

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
# Remove and recreate virtual environment
rm -rf .venv
uv venv .venv --python 3.9
source .venv/bin/activate
uv pip sync requirements-dev.txt
```

### Dependency Conflicts
```bash
# Force reinstall all packages
uv pip install --force-reinstall -r requirements-dev.txt
```

## Migration from pip

If you're migrating from pip:

1. Replace `pip install` with `uv pip install`
2. Replace `pip-sync` with `uv pip sync`
3. Use `uv venv` instead of `python -m venv`
4. All other commands remain the same

## Additional Resources

- [UV Documentation](https://github.com/astral-sh/uv)
- [UV vs pip Performance](https://github.com/astral-sh/uv#performance)
- [Shuup Documentation](https://shuup.readthedocs.io/)
