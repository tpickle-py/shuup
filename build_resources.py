#!/usr/bin/env python3
"""
Build script for Shuup static resources.
This replaces the setup.py build_resources command.
"""

from shuup_setup_utils import build_resources
from shuup_setup_utils.resource_building import Options

if __name__ == "__main__":
    options = Options()
    options.ci = True  # Running in CI environment
    build_resources(options)
