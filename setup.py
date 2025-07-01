# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import os
import sys

import setuptools

try:
    import tomllib
except ImportError:
    import tomli as tomllib

try:
    import shuup_setup_utils as utils

    HAS_SETUP_UTILS = True
except ImportError:
    HAS_SETUP_UTILS = False
    utils = None

TOPDIR = os.path.abspath(os.path.dirname(__file__))
LONG_DESCRIPTION_FILE = os.path.join(TOPDIR, "README.rst")
VERSION_FILE = os.path.join(TOPDIR, "shuup", "_version.py")

# Release instructions
#
# Version and dependencies are now managed in pyproject.toml.
# For releases:
#  1. Update the Change Log (CHANGELOG.md)
#  2. Update version in pyproject.toml using: uv version --bump [patch|minor|major]
#  3. Update version and release variables in doc/conf.py
#  4. Commit changes
#  5. Tag the commit: git tag -a -m "Shuup X.Y.Z" vX.Y.Z
#  6. Push tag: git push origin refs/tags/vX.Y.Z
#  7. Do a post-release commit (add new "Unreleased" header to changelog)


def get_project_metadata():
    """Read project metadata from pyproject.toml"""
    pyproject_path = os.path.join(TOPDIR, "pyproject.toml")

    if not os.path.exists(pyproject_path):
        raise FileNotFoundError("pyproject.toml not found. This is required for modern Python packaging.")

    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)

    project = pyproject_data.get("project", {})

    return {
        "name": project.get("name", "shuup"),
        "version": project.get("version"),
        "description": project.get("description", "E-Commerce Platform"),
        "dependencies": project.get("dependencies", []),
        "requires_python": project.get("requires-python", ">=3.9"),
        "license": project.get("license", "OSL-3.0"),
        "authors": project.get("authors", []),
        "classifiers": project.get("classifiers", []),
    }


EXCLUDED_PACKAGES = [
    "shuup_tests",
    "shuup_tests.*",
]

if HAS_SETUP_UTILS:
    utils.add_exclude_patters(
        [
            "build",
            "doc",
            "var",
            "LC_MESSAGES",
            "local_settings.py",
        ]
    )


def get_requirements():
    """Read requirements from pyproject.toml"""
    metadata = get_project_metadata()
    return metadata["dependencies"]


if __name__ == "__main__":
    if "upload" in sys.argv:
        raise OSError("Uploading is blacklisted")

    # Get project metadata from pyproject.toml
    metadata = get_project_metadata()

    # Extract author information
    authors = metadata["authors"]
    author_name = authors[0]["name"] if authors else "Shuup Commerce Inc."
    author_email = authors[0]["email"] if authors else "shuup@shuup.com"

    if HAS_SETUP_UTILS:
        # Use setup utils for development builds with dynamic versioning
        version = utils.get_version(metadata["version"], TOPDIR, VERSION_FILE)
        utils.write_version_to_file(version, VERSION_FILE)
        long_description = utils.get_long_description(LONG_DESCRIPTION_FILE)
        packages = utils.find_packages(exclude=EXCLUDED_PACKAGES)
        cmdclass = utils.COMMANDS
    else:
        # Fallback when setup utils is not available - use static version from pyproject.toml
        version = metadata["version"]
        if not version:
            raise ValueError("Version not found in pyproject.toml")

        try:
            with open(LONG_DESCRIPTION_FILE, encoding="utf-8") as f:
                long_description = f.read()
        except Exception:
            long_description = metadata["description"]
        packages = setuptools.find_packages(exclude=EXCLUDED_PACKAGES)
        cmdclass = {}

    setuptools.setup(
        name=metadata["name"],
        version=version,
        description=metadata["description"],
        long_description=long_description,
        long_description_content_type="text/x-rst",
        url="http://shuup.com/",
        download_url=f"https://github.com/shuup/shuup/releases/download/v{version}/shuup-{version}-py3-none-any.whl",
        author=author_name,
        author_email=author_email,
        license=metadata["license"],
        classifiers=metadata["classifiers"],
        install_requires=get_requirements(),
        python_requires=metadata["requires_python"],
        packages=packages,
        include_package_data=True,
        cmdclass=cmdclass,
    )
