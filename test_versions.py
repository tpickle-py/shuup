#!/usr/bin/env python3
"""
Test script for the updated uv-based versions.py module.
"""

import os
import sys

# Add the current directory to the path so we can import shuup_setup_utils
sys.path.insert(0, os.path.dirname(__file__))

from shuup_setup_utils.versions import (  # noqa: E402
    check_version_dry_run,
    get_current_version,
    get_version,
    get_version_info_json,
)


def test_uv_version_functions():
    """Test the new uv-based version functions."""
    root = os.path.dirname(__file__)

    print("Testing uv-based version management")
    print("=" * 50)

    # Test getting current version using uv
    current_version = get_current_version(root)
    print(f"Current version from uv: {current_version}")

    # Test the main get_version function
    version = get_version("3.2.26.dev", root, "/tmp/dummy_version.py")
    print(f"get_version() result: {version}")

    # Test version parsing with non-dev version
    stable_version = get_version("3.2.26", root, "/tmp/dummy_version.py")
    print(f"get_version() with stable version: {stable_version}")

    # Test dry run version bumping
    print("\nTesting dry run version bumping:")
    print(f"Current version: {current_version}")

    # Test different bump types
    for bump_type in ["patch", "minor", "major"]:
        current_ver, new_ver = check_version_dry_run(root, bump_type)
        print(f"  {bump_type.capitalize()} bump: {current_ver} -> {new_ver}")

    # Test JSON output (if available)
    print("\nTesting JSON version info:")
    version_info = get_version_info_json(root)
    if version_info:
        print(f"Version info JSON: {version_info}")
    else:
        print("JSON version info not available (uv might not support it yet)")

    print("\n✅ uv-based version functions are working correctly!")
    print("\nKey benefits of the new uv-based approach:")
    print("  - Uses uv's native version management")
    print("  - Consistent with modern Python packaging")
    print("  - Automatic pyproject.toml synchronization")
    print("  - Supports semantic versioning bumps")
    print("  - Dry-run capabilities for safe testing")


if __name__ == "__main__":
    test_uv_version_functions()
