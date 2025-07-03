# Requirements Files Migration Guide

## Overview

As of the uv/Hatchling migration, all requirements files are now generated from `pyproject.toml` to ensure consistency and leverage uv's superior dependency resolution.

## What Changed

### Before
- Requirements files were manually maintained
- Potential for drift between `pyproject.toml` and requirements files
- Manual dependency management

### After
- All requirements files are generated from `pyproject.toml`
- Two types of requirements files:
  - **Full**: Include all transitive dependencies (~160 lines)
  - **Minimal**: Only direct dependencies (~30-40 lines)

## Requirements Files Structure

### Main Dependencies
- `requirements.txt` - Full with all transitive dependencies
- `requirements-minimal.txt` - Only direct dependencies from `pyproject.toml`

### Development Dependencies
- `requirements-dev.txt` - Full dev dependencies
- `requirements-dev-minimal.txt` - Minimal dev dependencies

### Test Dependencies
- `requirements-tests.txt` - Full test dependencies
- `requirements-test-minimal.txt` - Minimal test dependencies

### Documentation Dependencies
- `requirements-doc.txt` - Full docs dependencies
- `requirements-doc-minimal.txt` - Minimal docs dependencies

### CI Dependencies
- `requirements-dev-ci.txt` - Full dev + test dependencies
- `requirements-dev-ci-minimal.txt` - Minimal dev + test dependencies

## When to Use Which

### Use Full Requirements Files When:
- You need exact reproducibility
- Setting up production environments
- CI/CD pipelines requiring exact versions
- Debugging dependency conflicts

### Use Minimal Requirements Files When:
- Building Docker images (faster builds)
- New development environments
- When you want latest compatible versions
- Teaching/documentation purposes

## How to Regenerate

### Automatic (Recommended)
```bash
./regenerate_requirements.sh
```

### Manual
```bash
# Full requirements
uv export --no-hashes --no-annotate --format requirements-txt > requirements.txt
uv export --group dev --no-hashes --no-annotate --format requirements-txt > requirements-dev.txt

# Minimal requirements
uv run python generate_requirements.py
```

## Migration Steps

1. **Review current requirements files** - Check if you have local modifications
2. **Run regeneration script** - `./regenerate_requirements.sh`
3. **Update CI/CD** - Switch to appropriate requirements files
4. **Update documentation** - Reference the new workflow

## Benefits

- **Consistency**: Single source of truth in `pyproject.toml`
- **Speed**: uv's dependency resolution is much faster
- **Flexibility**: Choose between full and minimal requirements
- **Maintenance**: Automatic generation reduces manual errors
- **Modern**: Follows current Python packaging best practices
