# Version Management Migration to UV

This document describes the migration of Shuup's version management system from custom git-based versioning to leveraging `uv`'s built-in version management capabilities.

## Overview

The `shuup_setup_utils/versions.py` module has been updated to use `uv`'s native version management commands while maintaining backward compatibility with existing workflows.

## Key Changes

### 1. Primary Version Source
- **Before**: Git tags and manual pyproject.toml parsing
- **After**: `uv version` commands with fallback to manual parsing

### 2. Version Reading
```python
# Uses uv's built-in version reading
def _get_version_from_pyproject(root):
    result = subprocess.run(["uv", "version", "--short"], cwd=root, ...)
    return result.stdout.strip()
```

### 3. Version Writing
```python
# Uses uv's built-in version setting
def write_version_to_pyproject(version, root):
    subprocess.run(["uv", "version", str(version)], cwd=root, ...)
```

### 4. Version Bumping
```python
# Uses uv's semantic version bumping
def bump_version(root, bump_type="patch"):
    subprocess.run(["uv", "version", "--bump", bump_type], cwd=root, ...)
```

## New Features

### Dry Run Support
```python
# Check what a version bump would produce without changing anything
current_ver, new_ver = check_version_dry_run('/app', 'patch')
print(f"Would change: {current_ver} -> {new_ver}")
```

### JSON Version Info
```python
# Get detailed version information in JSON format
version_info = get_version_info_json('/app')
# Returns: {'package_name': 'shuup', 'version': '3.2.26', 'commit_info': None}
```

### Direct Version Setting
```python
# Set a specific version directly
set_specific_version('/app', '3.2.27')
```

## Usage Examples

### Check Current Version
```bash
# Using uv directly
uv version

# Using Python API
from shuup_setup_utils.versions import get_current_version
version = get_current_version('/path/to/project')
```

### Bump Version
```bash
# Using uv directly
uv version --bump patch   # 3.2.26 -> 3.2.27
uv version --bump minor   # 3.2.26 -> 3.3.0
uv version --bump major   # 3.2.26 -> 4.0.0

# Using Python API
from shuup_setup_utils.versions import bump_version
new_version = bump_version('/path/to/project', 'patch')
```

### Dry Run (Test Changes)
```bash
# Using uv directly
uv version --bump patch --dry-run

# Using Python API
from shuup_setup_utils.versions import check_version_dry_run
current, new = check_version_dry_run('/path/to/project', 'patch')
```

## Backward Compatibility

The updated module maintains full backward compatibility:

1. **Existing API**: All existing functions (`get_version`, `write_version_to_file`, etc.) work as before
2. **Fallback Support**: If `uv` is not available, the system falls back to manual TOML parsing
3. **Git Integration**: Git-based development versioning is still supported
4. **Legacy Support**: Version files (`_version.py`) are still supported for distribution packages

## Benefits

1. **Standardization**: Uses the modern Python packaging standard tool (`uv`)
2. **Reliability**: Leverages well-tested, community-maintained version management
3. **Features**: Gains access to dry-run, JSON output, and other uv features
4. **Maintenance**: Reduces custom code maintenance burden
5. **Integration**: Better integration with modern Python development workflows

## Migration Path

No changes required for existing code. The migration is transparent:

- Existing `setup.py` continues to work
- Development workflows remain the same
- CI/CD processes are unaffected
- Version files are still generated for backward compatibility

## Commands Reference

### UV Commands
```bash
uv version                    # Show current version
uv version --short            # Show version only
uv version --bump patch       # Bump patch version
uv version --bump minor       # Bump minor version
uv version --bump major       # Bump major version
uv version --dry-run          # Test without changing
uv version "3.2.27"          # Set specific version
uv version --output-format json # JSON output
```

### Python API
```python
from shuup_setup_utils.versions import (
    get_current_version,
    bump_version,
    check_version_dry_run,
    set_specific_version,
    get_version_info_json
)

# Get current version
version = get_current_version('/app')

# Bump version
new_version = bump_version('/app', 'patch')

# Test version bump
current, new = check_version_dry_run('/app', 'minor')

# Set specific version
set_specific_version('/app', '3.2.27')

# Get detailed info
info = get_version_info_json('/app')
```
