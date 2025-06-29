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
#  1. Update the Change Log (CHANGELOG.md)
#      - Make sure all relevant changes since last release are listed
#      - Remove the instruction bullet point ("List all changes after
#        x.x.x here...")
#      - Change the "Unreleased" header to appropriate version header.
#        See header of the last release for example.
#  2. Update VERSION variable here: Increase and drop .post0.dev suffix
#  4. Update version and release variables in doc/conf.py
#  5. Commit changes of steps 1--4
#  6. Tag the commit (of step 5) with
#        git tag -a -m "Shuup X.Y.Z" vX.Y.Z
#     where X.Y.Z is the new version number (must be same as VERSION
#     variable here)
#  7. Check the tag is OK and push it with
#        git push origin refs/tags/vX.Y.Z
#  8. Do a post-release commit:
#      - Add new "Unreleased" header and instruction bullet point to
#        Change Log
#      - Add ".post0.dev" suffix to VERSION variable here

NAME = "shuup"
VERSION = "3.2.25.post0.dev"
DESCRIPTION = "E-Commerce Platform"
AUTHOR = "Shuup Commerce Inc."
AUTHOR_EMAIL = "shuup@shuup.com"
URL = "http://shuup.com/"
DOWNLOAD_URL_TEMPLATE = (
    "https://github.com/tpickle-py/shuup/releases/download/"
    "v{version}/shuup-{version}-py3-none-any.whl"
)
LICENSE = "OSL-3.0"  # https://spdx.org/licenses/
CLASSIFIERS = """
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: Other/Proprietary License
Natural Language :: English
Natural Language :: Chinese (Simplified)
Natural Language :: Finnish
Natural Language :: Japanese
Natural Language :: Portuguese (Brazilian)
Programming Language :: JavaScript
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Topic :: Internet :: WWW/HTTP :: Dynamic Content
Topic :: Internet :: WWW/HTTP :: Site Management
Topic :: Office/Business
Topic :: Software Development :: Libraries :: Application Frameworks
Topic :: Software Development :: Libraries :: Python Modules
""".strip().splitlines()

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
    pyproject_path = os.path.join(TOPDIR, "pyproject.toml")
    if os.path.exists(pyproject_path):
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)

        dependencies = pyproject_data.get("project", {}).get("dependencies", [])
        if dependencies:
            return dependencies

    # Fallback to hardcoded list if pyproject.toml is not available or doesn't have dependencies
    return [
        "babel>=2.12.0",
        "bleach>=6.0.0",
        "django>=3.2,<4.3",
        "django-bootstrap3>=21.2",
        "django-countries>=7.5.0",
        "django-enumfields>=2.1.1",
        "django-filer>=2.2.0",
        "django-filter>=23.0",
        "django-jinja>=2.11.0",
        "django-mptt>=0.14.0",
        "django-parler>=2.3",
        "django-polymorphic>=3.1.0",
        "django-registration-redux>=2.11",
        "django-reversion>=5.0.0",
        "django-timezone-field>=5.0",
        "djangorestframework>=3.14.0",
        "factory-boy>=3.2.0",
        "Faker>=18.0.0",
        "Jinja2>=3.1.0",
        "jsonfield>=3.1.0",
        "keyring>=23",
        "keyrings.alt>=4",
        "lxml>=4.9.0",
        "Markdown>=3.4.0",
        "openpyxl>=3.1.0",
        "python-dateutil>=2.8",
        "shuup-mirage-field>=2.2.0,<3",
        "tomli>=2.0.0;python_version<'3.11'",
        "pytz>=2022.1",
        "requests>=2.28.0",
        "six>=1.16.0",
        "xlrd>=2.0.0",
        "setuptools>=75.3.2",
    ]


REQUIRES = get_requirements()

if __name__ == "__main__":
    if "upload" in sys.argv:
        raise EnvironmentError("Uploading is blacklisted")

    if HAS_SETUP_UTILS:
        version = utils.get_version(VERSION, TOPDIR, VERSION_FILE)
        utils.write_version_to_file(version, VERSION_FILE)
        long_description = utils.get_long_description(LONG_DESCRIPTION_FILE)
        packages = utils.find_packages(exclude=EXCLUDED_PACKAGES)
        cmdclass = utils.COMMANDS
    else:
        # Fallback when setup utils is not available
        version = VERSION
        try:
            with open(LONG_DESCRIPTION_FILE, "r", encoding="utf-8") as f:
                long_description = f.read()
        except:
            long_description = DESCRIPTION
        packages = setuptools.find_packages(exclude=EXCLUDED_PACKAGES)
        cmdclass = {}

    setuptools.setup(
        name=NAME,
        version=version,
        description=DESCRIPTION,
        long_description=long_description,
        url=URL,
        download_url=DOWNLOAD_URL_TEMPLATE.format(version=version),
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        license=LICENSE,
        classifiers=CLASSIFIERS,
        install_requires=REQUIRES,
        python_requires=">=3.8",
        packages=packages,
        include_package_data=True,
        cmdclass=cmdclass,
    )
