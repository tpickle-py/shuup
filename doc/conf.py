#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
"""
Shuup documentation build configuration file
"""

import os
import sys
import warnings
from importlib import metadata
from pathlib import Path

import django

from packaging.version import Version

# Suppress pkg_resources deprecation warnings during documentation build
warnings.filterwarnings("ignore", message="pkg_resources is deprecated", category=UserWarning)

# -- Python path ----------------------------------------------------------

DOC_PATH = Path(__file__).parent.absolute()
sys.path.insert(0, str(DOC_PATH / "_ext"))
sys.path.insert(0, str(DOC_PATH.parent))


# -- Initialize Django ----------------------------------------------------


def initialize_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shuup_workbench.settings.dev")
    try:
        import django
        from django.conf import settings

        # Set USE_I18N=False to avoid warnings from import-time ugettext calls
        if hasattr(settings, "USE_I18N"):
            settings.USE_I18N = False

        # Configure Django apps explicitly for documentation
        if not settings.configured:
            settings.configure()

        django.setup()

        # Try to validate the Django setup
        from django.core.management import execute_from_command_line

    except Exception as e:
        warnings.warn(f"Django setup failed: {e}")
        # Continue anyway - docs can still be built without full Django setup


initialize_django()


# -- Monkey patch some property descriptors to allow introspection


def patch_for_introspection():
    """
    Apply patches for better Sphinx introspection of Django model fields.

    This patches django-countries CountryField and jsonfield to prevent
    Sphinx warnings when generating documentation for models that use these fields.
    """
    try:
        import shuup_introspection_helper

        shuup_introspection_helper.enable_patches()
    except ImportError:
        # If the introspection helper isn't available, continue without it
        # Modern Sphinx versions may not need these patches
        pass


# Only apply patches if we're actually using the fields that need them
try:
    # Check if we have the problematic dependencies
    import django_countries.fields
    import jsonfield.subclassing

    patch_for_introspection()
except ImportError:
    # If the dependencies aren't available, we don't need the patches
    pass

# -- General configuration ------------------------------------------------

project = "Shuup"
copyright = "2012-2025, Shuup Commerce Inc."

extensions = [
    # Core Sphinx extensions that work reliably with modern versions
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",  # For Google/NumPy style docstrings
]

# Note: djangodocs and django_sphinx have been removed due to
# incompatibility with modern Sphinx versions (8.x+)

# templates_path = ['_templates']
source_suffix = ".rst"
source_encoding = "utf-8"
master_doc = "index"

# -- Version handling ---------------------------------------------------------


def get_version() -> str:
    """Get version string using semantic versioning best practices."""
    try:
        # Try to get version from installed package (preferred method)
        version = metadata.version("shuup")
        return version if version else "0.0.0"
    except metadata.PackageNotFoundError:
        pass

    # Fallback to reading from pyproject.toml if package not installed
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib  # Fallback for older Python versions
        except ImportError:
            # Ultimate fallback - parse pyproject.toml manually
            import re

            pyproject_path = DOC_PATH.parent / "pyproject.toml"
            try:
                content = pyproject_path.read_text(encoding="utf-8")
                match = re.search(r'version\s*=\s*"([^"]+)"', content)
                return match.group(1) if match else "0.0.0"
            except (FileNotFoundError, OSError):
                return "0.0.0"
    else:
        pyproject_path = DOC_PATH.parent / "pyproject.toml"
        try:
            pyproject_data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
            return pyproject_data["project"]["version"]
        except (FileNotFoundError, OSError, KeyError):
            return "0.0.0"

    return "0.0.0"  # Final fallback


# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.

version_string = get_version()
try:
    parsed_version = Version(version_string)
except Exception:
    # Fallback to a basic version if parsing fails
    parsed_version = Version("0.0.0")

# The short X.Y version for display
version = f"{parsed_version.major}.{parsed_version.minor}"
if parsed_version.is_prerelease or parsed_version.is_devrelease:
    version += "+"

# The full version, including alpha/beta/rc tags
release = str(parsed_version)

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
language = "en"

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#   today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = "%Y-%m-%d"

# Default role for pure backticked references without interpreted text role
default_role = "obj"

# Insert both the class’ and the __init__ method’s docstring into the
# main body of an autoclass directive
autoclass_content = "both"

autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "inherited-members": False,
    "special-members": "__init__",
}

# Generate autosummary stubs
autosummary_generate = True
autosummary_imported_members = True

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = [
    "_build",
    # Skip problematic modules that don't exist or have import issues
    "**/shuup/testing/service_forms*",
    "**/shuup/testing/simple_checkout_phase*",
    "**/shuup/testing/supplier_pricing/pricing*",
    "**/shuup/testing/supplier_pricing/supplier_strategy*",
    "**/shuup/discounts/management*",
    "**/shuup/discounts/signal_handers*",  # Note: this is a typo in the original
]

# Configure autodoc to skip modules that cause import errors
autodoc_mock_imports = [
    "shuup.testing.service_forms",
    "shuup.testing.simple_checkout_phase",
    "shuup.testing.supplier_pricing.pricing",
    "shuup.testing.supplier_pricing.supplier_strategy",
    "shuup.discounts.management",
    "shuup.discounts.signal_handers",
]

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = False

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# A list of ignored prefixes for module index sorting.
modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
keep_warnings = True

todo_include_todos = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": (
        "https://docs.djangoproject.com/en/4.2/",
        "https://docs.djangoproject.com/en/4.2/objects.inv",
    ),
    "djpolymorph": ("https://django-polymorphic.readthedocs.io/en/latest/", None),
}

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
try:
    import sphinx_rtd_theme

    html_theme = "sphinx_rtd_theme"
    html_theme_path = []
except ImportError:
    # Fallback to default alabaster theme
    html_theme = "alabaster"
    html_theme_path = []

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
# html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = ["_theme"]  # Now set dynamically above

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
# html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
# html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
# html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = "Shuupdoc"


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    # 'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    ("index", "Shuup.tex", "Shuup Documentation", "Shuup Commerce Inc.", "manual"),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [("index", "shuup", "Shuup Documentation", ["Shuup Commerce Inc."], 1)]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        "index",
        "Shuup",
        "Shuup Documentation",
        "Shuup Commerce Inc.",
        "Shuup",
        "One line description of project.",
        "Miscellaneous",
    ),
]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
# texinfo_no_detailmenu = False
