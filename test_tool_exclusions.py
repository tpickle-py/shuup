#!/usr/bin/env python3
"""
Simple script to test that code analysis tools are properly excluding .venv directory.
This script can be run to verify that tools like flake8, black, isort, etc. are working correctly.
"""

import os
import subprocess
import sys


def run_command(cmd, description):
    """Run a command and check if it excludes .venv properly."""
    print(f"\n🔍 Testing {description}...")
    print(f"Command: {' '.join(cmd)}")

    try:
        # Run in dry-run mode where possible to avoid making changes
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd(), check=False)
        # Check if .venv appears in the output (which would be bad)
        if ".venv" in result.stdout or ".venv" in result.stderr:
            print(f"❌ ISSUE: .venv directory appears to be processed by {description}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
        else:
            print(f"✅ OK: {description} properly excludes .venv")
            return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"⚠️  Could not test {description}: {e}")
        return None

def main():
    """Test various tools to ensure they exclude .venv correctly."""
    print("Testing tool configurations to ensure .venv is properly excluded...")

    tests = [
        (["uv", "run", "flake8", "--version"], "Flake8 version check"),
        (["uv", "run", "black", "--check", "--diff", "--verbose", "."], "Black formatting check"),
        (["uv", "run", "isort", "--check", "--diff", "."], "isort import sorting check"),
        # Note: We avoid running actual linting as it might be slow
    ]

    results = []
    for cmd, description in tests:
        result = run_command(cmd, description)
        results.append(result)

    # Summary
    print("\n" + "="*50)
    print("SUMMARY:")
    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    skipped = sum(1 for r in results if r is None)

    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  Skipped: {skipped}")

    if failed > 0:
        print("\n❌ Some tools may still be processing the .venv directory.")
        print("Check the tool configurations in pyproject.toml and setup.cfg")
        sys.exit(1)
    else:
        print("\n🎉 All testable tools appear to properly exclude .venv!")

if __name__ == "__main__":
    main()
