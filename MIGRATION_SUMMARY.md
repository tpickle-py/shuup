# Migration to UV and Python 3.8+ - Summary

## Changes Made

### 1. GitHub Actions Workflow (`.github/workflows/shuup.yml`)

**Updated Python Versions:**
- **Before:** Python 3.6, 3.7, 3.8
- **After:** Python 3.8, 3.9, 3.10, 3.11, 3.12

**Updated Actions:**
- **Before:** `actions/checkout@v2`, `actions/setup-python@v1`
- **After:** `actions/checkout@v4`, `astral-sh/setup-uv@v4`

**Updated Commands:**
- **Before:** `pip install -r requirements-*.txt`, `py.test`
- **After:** `uv sync --dev`, `uv run pytest`

**Benefits:**
- ✅ Faster CI builds (10-100x faster dependency installation)
- ✅ More reliable dependency resolution
- ✅ Up-to-date with latest GitHub Actions
- ✅ Better caching and security

### 2. Project Configuration (`pyproject.toml`)

**Added Python 3.12 Support:**
- Updated classifiers and tool configurations
- Added Python 3.12 to Black target versions

**Modernized Dependency Groups:**
- Replaced basic dev dependencies with comprehensive groups:
  - `dev`: All development tools
  - `test`: Testing dependencies
  - `docs`: Documentation tools

**Enhanced Tool Configuration:**
- Added Ruff configuration as modern alternative to flake8
- Updated pytest with XML coverage output and better options
- Added UV-specific configuration sections

**Updated Tool Versions:**
- Black >= 24.0.0
- pytest >= 8.0.0
- mypy >= 1.8.0
- All other tools to latest compatible versions

### 3. Additional Files Created

**`.python-version`**
- Sets default Python version to 3.11

**`.pre-commit-config.yaml`**
- Modern pre-commit hooks including Ruff
- Automatic code formatting and linting

**`migrate_to_uv.sh`**
- Automated migration script
- Sets up environment with one command

**Updated `docs/UV_SETUP_GUIDE.md`**
- Comprehensive guide for UV usage
- Development workflow documentation
- Troubleshooting section

## Recommendations for Good Build Hygiene

### 1. **Adopt UV Fully**
```bash
# Replace all pip commands with uv
uv sync --dev        # Instead of pip install -r requirements-dev.txt
uv add package-name  # Instead of pip install package-name
uv run pytest       # No need to activate virtual environment
```

### 2. **Use Dependency Groups**
```toml
[dependency-groups]
dev = ["black>=24.0.0", "pytest>=8.0.0", ...]
test = ["pytest>=8.0.0", "coverage>=7.4.0", ...]
docs = ["sphinx>=7.2.0", ...]
```

### 3. **Leverage Lock Files**
- UV automatically creates `uv.lock` for reproducible builds
- Commit this file to version control
- CI/CD will use exact same dependency versions

### 4. **Set Up Pre-commit Hooks**
```bash
uv run pre-commit install
```
- Prevents bad code from being committed
- Automatic formatting and linting
- Consistent code style across team

### 5. **Pin Python Version**
- Use `.python-version` file
- Ensures consistent Python version across environments
- UV automatically respects this file

### 6. **Modern Linting with Ruff**
- Ruff is 10-100x faster than flake8
- Combined linting and formatting
- Compatible with existing flake8 configuration

### 7. **Comprehensive Testing**
```bash
uv run pytest --cov=shuup --cov-report=xml --cov-report=html
```
- XML coverage for CI integration
- HTML coverage for local development
- Configurable coverage thresholds

### 8. **Environment Isolation**
```bash
uv run command  # No need to activate virtual environment
```
- Eliminates "forgot to activate venv" issues
- Cleaner development workflow
- Better CI/CD integration

## Next Steps

1. **Run the migration script:**
   ```bash
   ./migrate_to_uv.sh
   ```

2. **Update your development workflow:**
   ```bash
   uv run shuup_workbench runserver
   uv run pytest
   uv run black .
   ```

3. **Set up pre-commit hooks:**
   ```bash
   uv run pre-commit install
   ```

4. **Update documentation for team members**
5. **Consider deprecating old requirements.txt files** (optional)

## Breaking Changes

⚠️ **For Team Members:**
- Need to install UV: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Change from `pip` commands to `uv` commands
- Python 3.8+ now required (was 3.6+)

⚠️ **For CI/CD:**
- GitHub Actions now use UV (already updated)
- Faster builds but may need adjustment of timeouts
- Different caching strategy (UV handles this automatically)

## Benefits Summary

- 🚀 **10-100x faster** dependency resolution and installation
- 🔒 **More reliable** builds with lock files
- 🛡️ **Better security** with updated GitHub Actions
- 🎯 **Modern tooling** (Ruff, latest pytest, etc.)
- 📦 **Simplified workflow** with `uv run`
- 🔄 **Better CI/CD** with consistent environments
- 📈 **Future-proof** with Python 3.8-3.12 support
