#!/usr/bin/env python
"""
Custom Hatchling build hook to generate requirements files during build.

This hook will run during the build process to automatically generate
requirements files from pyproject.toml, ensuring they're always up-to-date
when creating distributions.
"""

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from hatchling.plugin import hookimpl


class RequirementsGeneratorHook:
    """Build hook to generate requirements files during build."""

    PLUGIN_NAME = "requirements-generator"

    def __init__(self, root: str, config: Dict[str, Any]) -> None:
        self.root = Path(root)
        self.config = config

    def initialize(self, version: str, build_data: Dict[str, Any]) -> None:
        """Initialize the hook - generate requirements files."""
        print("Generating requirements files from pyproject.toml...")

        try:
            # Generate full requirements files using uv
            self._generate_uv_requirements()

            # Generate minimal requirements files using our custom script
            self._generate_minimal_requirements()

            print("✓ Requirements files generated successfully")

        except Exception as e:
            print(f"Warning: Failed to generate requirements files: {e}")
            # Don't fail the build, just warn

    def _generate_uv_requirements(self) -> None:
        """Generate full requirements files using uv export."""
        requirements_map = {
            "requirements.txt": [],
            "requirements-dev.txt": ["--group", "dev"],
            "requirements-tests.txt": ["--group", "test"],
            "requirements-doc.txt": ["--group", "docs"],
        }

        for filename, extra_args in requirements_map.items():
            cmd = ["uv", "export", "--format", "requirements-txt"] + extra_args

            try:
                result = subprocess.run(cmd, cwd=self.root, capture_output=True, text=True, check=True)

                with open(self.root / filename, "w") as f:
                    f.write(result.stdout)

            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to generate {filename}: {e}")

    def _generate_minimal_requirements(self) -> None:
        """Generate minimal requirements files using our custom script."""
        script_path = self.root / "generate_requirements.py"

        if script_path.exists():
            try:
                subprocess.run([sys.executable, str(script_path)], cwd=self.root, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Warning: Failed to generate minimal requirements: {e}")


@hookimpl
def hatch_register_build_hook():
    """Register the requirements generator build hook."""
    return RequirementsGeneratorHook
