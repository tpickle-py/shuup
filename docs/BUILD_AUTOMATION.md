# Requirements Generation During Build Process

## Overview

Shuup's requirements files are automatically generated from `pyproject.toml` during various build processes to ensure they're always up-to-date and synchronized with the dependency definitions.

## When Requirements Are Generated

### 1. Pre-commit Hooks
- **Trigger**: When `pyproject.toml` is modified
- **Action**: Automatically runs `./regenerate_requirements.sh`
- **Result**: Updated requirements files are staged for commit
- **Setup**: `pre-commit install` (included in `make setup-dev`)

### 2. Make Commands
```bash
make requirements    # Generate requirements files only
make build          # Clean, generate requirements, then build package
make check-release  # Full release preparation including requirements
```

### 3. CI/CD Pipeline (GitHub Actions)
- **On PR**: Checks if requirements files are up-to-date
- **On push to main**: Automatically updates requirements files if needed
- **Manual trigger**: `workflow_dispatch` event

### 4. Manual Generation
```bash
./regenerate_requirements.sh                              # Shell script
python -m shuup_setup_utils generate_requirements        # Python command
make requirements                                         # Make target
```

## Generated Files

### Full Requirements (with transitive dependencies)
- `requirements.txt` - Core dependencies
- `requirements-dev.txt` - Development dependencies
- `requirements-tests.txt` - Testing dependencies
- `requirements-doc.txt` - Documentation dependencies
- `requirements-dev-ci.txt` - Combined dev + test for CI

### Minimal Requirements (direct dependencies only)
- `requirements-minimal.txt` - Core dependencies
- `requirements-dev-minimal.txt` - Development dependencies
- `requirements-test-minimal.txt` - Testing dependencies
- `requirements-doc-minimal.txt` - Documentation dependencies
- `requirements-dev-ci-minimal.txt` - Combined dev + test for CI

## Benefits

1. **Single Source of Truth**: All dependencies defined in `pyproject.toml`
2. **Automatic Synchronization**: Requirements files always match pyproject.toml
3. **Build Optimization**: Minimal files for faster Docker builds
4. **Developer Experience**: No manual requirements file management
5. **CI/CD Integration**: Automatic validation and updates

## Implementation Details

### Pre-commit Hook
```yaml
- repo: local
  hooks:
    - id: generate-requirements
      name: Generate requirements files
      entry: ./regenerate_requirements.sh
      language: script
      files: ^pyproject\.toml$
      pass_filenames: false
```

### Makefile Integration
```makefile
requirements:
    ./regenerate_requirements.sh

build: clean requirements
    uv build
```

### GitHub Actions
- Validates requirements files are up-to-date on PRs
- Auto-commits updated requirements on main branch pushes
- Tests installation of generated requirements files

This automation ensures that:
- Requirements files are never forgotten or out-of-sync
- Docker builds use optimized minimal dependencies
- CI/CD processes validate the complete dependency chain
- Contributors focus on dependency management in pyproject.toml only
