.. image:: https://travis-ci.org/shuup/shuup.svg?branch=master
    :target: https://travis-ci.org/shuup/shuup
.. image:: https://coveralls.io/repos/github/shuup/shuup/badge.svg?branch=master
   :target: https://coveralls.io/github/shuup/shuup?branch=master
.. image:: https://img.shields.io/pypi/v/shuup.svg
   :alt: PyPI
   :target: https://github.com/shuup/shuup
.. image:: https://snyk.io/test/github/shuup/shuup/badge.svg
   :alt: Known Vulnerabilities
   :target: https://snyk.io/test/github/shuup/shuup

Shuup
=====

Shuup is an Open Source E-Commerce Platform based on Django and Python.

https://shuup.com/

Copyright
---------

Copyright (c) 2012-2021 by Shuup Commerce Inc. <support@shuup.com>

Shuup is International Registered Trademark & Property of Shuup Commerce Inc.,
Business ID: BC1126729,
Business Address: 1500 West Georgia Suite 1300, Vancouver, BC, V6G-2Z6, Canada.

CLA
---

Contributor License Agreement is required for any contribution to this
project.  Agreement is signed as a part of pull request process.  See
the CLA.rst file distributed with Shuup.

License
-------

Shuup is published under Open Software License version 3.0 (OSL-3.0).
See the LICENSE file distributed with Shuup.

Some external libraries and contributions bundled with Shuup may be
published under other compatible licenses. For these, please
refer to VENDOR-LICENSES.md file in the source code tree or the licenses
included within each package.

Chat
----

We have a Gitter chat room for Shuup.  Come chat with us!  |Join chat|

.. |Join chat| image:: https://badges.gitter.im/Join%20Chat.svg
   :target: https://gitter.im/shuup/shuup

Docker quick start
------------------

Fastest way to get Shuup up and running is to use `Docker <https://www.docker.com>`_.

**Modern setup with uv (recommended):**

.. code-block:: shell

   docker-compose -f docker-compose.uv.yml up

**Traditional setup:**

.. code-block:: shell

   docker-compose up

Open `localhost:8000/sa <http://localhost:8000/sa>`_ in a browser,
log in with username: ``admin`` password: ``admin``

For development with live code reloading:

.. code-block:: shell

   docker-compose -f docker-compose-dev.yml up

Full Shuup installation guide
-----------------------------

See `Getting Started
<http://shuup.readthedocs.io/en/latest/howto/getting_started.html>`__.

For simple project example see our `Django-project template <https://github.com/shuup/shuup-project-template>`__.

Getting Started with Shuup development
--------------------------------------

See `Getting Started with Shuup Development
<http://shuup.readthedocs.io/en/latest/howto/getting_started_dev.html>`__.

Modern Development Setup (Recommended)
######################################

Shuup now uses `uv <https://docs.astral.sh/uv/>`_ for fast dependency management and `Hatchling <https://hatch.pypa.io/>`_ as the build backend:

.. code:: sh

    # Install uv (if not already installed)
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Clone and setup the project
    git clone https://github.com/shuup/shuup.git
    cd shuup
    
    # Create virtual environment and install dependencies
    uv sync
    
    # Run the development server
    uv run shuup_workbench runserver 0.0.0.0:8000 --settings=shuup_workbench.settings.dev
    
    # Run tests
    uv run pytest shuup_tests -v
    
    # Build static resources
    uv run shuup-build-resources

Requirements Files Management
#############################

Shuup uses **pyproject.toml** as the single source of truth for all dependencies. All requirements*.txt files are automatically generated from pyproject.toml.

**Automatic Generation:**

The requirements files are automatically generated in several scenarios:

1. **Pre-commit hooks** - When pyproject.toml changes, pre-commit automatically regenerates requirements
2. **Make commands** - Running ``make build`` or ``make requirements`` updates all requirements files  
3. **CI/CD pipeline** - GitHub Actions automatically checks and updates requirements files
4. **Manual generation** - Use ``./regenerate_requirements.sh`` or ``python -m shuup_setup_utils generate_requirements``

**Available Requirements Files:**

.. code:: sh

    # Regenerate all requirements files
    ./regenerate_requirements.sh
    
    # Or use make
    make requirements

This creates both full (with transitive dependencies) and minimal (direct dependencies only) versions:

- **Full files**: ``requirements.txt``, ``requirements-dev.txt``, etc. - Include all transitive dependencies
- **Minimal files**: ``requirements-minimal.txt``, ``requirements-dev-minimal.txt``, etc. - Only direct dependencies

**For Contributors:**

Never edit requirements*.txt files directly! Instead:

1. Add dependencies to pyproject.toml in the appropriate section
2. Run ``make requirements`` to regenerate all requirements files  
3. Commit both pyproject.toml and the updated requirements*.txt files

**For Docker/Containers:**

Use minimal files for Docker builds and full files for exact reproducibility:

.. code:: dockerfile

    # Use minimal requirements for faster builds
    COPY requirements-minimal.txt .
    RUN uv pip install -r requirements-minimal.txt

Version Management
##################

Use uv for semantic versioning:

.. code:: sh

    uv version                    # Show current version
    uv version --bump patch       # Bump patch version
    uv version --bump minor       # Bump minor version  
    uv version --bump major       # Bump major version

Legacy Setup
############

For projects not yet ready to migrate to uv, the traditional setup still works:

.. code:: sh

    pip install -r requirements-dev.txt
    python setup.py build_resources

Contributing to Shuup
---------------------

Interested in contributing to Shuup? Please see our `Contribution Guide
<https://www.shuup.com/contributions/>`__.

Documentation
-------------

Shuup documentation is available online at `Read the Docs
<http://shuup.readthedocs.org/>`__.

Documentation is built with `Sphinx <http://sphinx-doc.org/>`__.

Build documentation using uv:

.. code:: sh

    uv sync --group docs
    cd doc && uv run make html

Or using traditional pip:

.. code:: sh

    pip install -r requirements-doc.txt
    cd doc && make html

To update the API documentation rst files, e.g. after adding new
modules, use command:

.. code:: sh

    ./generate_apidoc.py

Roadmap
-------

v3 (Q4 2021)
###############

* Initial Django 3.x support
* Latest Jinja support
* Deprecate theme folders under Shuup front which are used to override
  individual macros in macro folders. This does not work well with latest
  Jinja and adds extra complexity.

v4 (Q1 2022)
#############

* Move Shuup front, xtheme and theming features to own addons. This so that
  projects not ready for updating theme or front can still get latest Shuup.
* Introduce new default theme and overhaul templates structure to be more
  simple (likely Bootstrap 5 will be used).
* Bump admin Bootstrap version to match with the new front
* Move various other not essential apps in this repository to addons for
  better version management.

Additional Material
-------------------

* `Django-project template <https://github.com/shuup/shuup-project-template>`__. Django-project template.
* `Provides system <https://shuup.readthedocs.io/en/latest/ref/provides.html>`__.
* `Core settings <https://shuup.readthedocs.io/en/latest/api/shuup.core.html#module-shuup.core.settings>`__.
* `Front settings <https://shuup.readthedocs.io/en/latest/api/shuup.front.html#module-shuup.front.settings>`__.
* `Admin settings <https://shuup.readthedocs.io/en/latest/api/shuup.admin.html#module-shuup.admin.settings>`__.
* `Extending Shuup <https://shuup.readthedocs.io/en/latest/#extending-shuup>`__.


Admin Preview
-------------

.. image:: doc/_static/admin_shop_product.png
    :target: doc/_static/admin_shop_product.png
    :height: 300px

.. image:: doc/_static/admin_order_detail.png
    :target: doc/_static/admin_order_detail.png
    :height: 300px
