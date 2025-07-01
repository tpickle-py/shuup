#!/usr/bin/env python3
"""
Generate minimal requirements files from pyproject.toml
Only includes direct dependencies, not transitive ones.
"""

import tomllib


def load_pyproject():
    """Load pyproject.toml file."""
    with open("pyproject.toml", "rb") as f:
        return tomllib.load(f)


def write_requirements_file(filename, packages, description=""):
    """Write a requirements file with the given packages."""
    with open(filename, "w") as f:
        f.write(f"# Generated from pyproject.toml - {description}\n")
        f.write("# Install in editable mode\n")
        f.write("-e .\n\n")

        if packages:
            f.write("# Direct dependencies\n")
            for package in sorted(packages):
                f.write(f"{package}\n")


def main():
    """Generate all requirements files."""
    pyproject = load_pyproject()

    # Main dependencies are in project.dependencies
    main_deps = pyproject.get("project", {}).get("dependencies", [])

    # Development dependencies are in dependency-groups
    dep_groups = pyproject.get("dependency-groups", {})

    dev_deps = dep_groups.get("dev", [])
    test_deps = dep_groups.get("test", [])
    docs_deps = dep_groups.get("docs", [])

    # Write minimal requirements files (direct dependencies only)
    write_requirements_file("requirements-minimal.txt", main_deps, "Main dependencies only")

    write_requirements_file("requirements-dev-minimal.txt", dev_deps, "Development dependencies only")

    write_requirements_file("requirements-test-minimal.txt", test_deps, "Test dependencies only")

    write_requirements_file("requirements-doc-minimal.txt", docs_deps, "Documentation dependencies only")

    # Combined CI requirements (dev + test)
    ci_deps = list(set(dev_deps + test_deps))
    write_requirements_file("requirements-dev-ci-minimal.txt", ci_deps, "Development and test dependencies")

    print("Generated minimal requirements files:")
    print("- requirements-minimal.txt (main dependencies)")
    print("- requirements-dev-minimal.txt (dev dependencies)")
    print("- requirements-test-minimal.txt (test dependencies)")
    print("- requirements-doc-minimal.txt (docs dependencies)")
    print("- requirements-dev-ci-minimal.txt (dev + test dependencies)")


if __name__ == "__main__":
    main()
