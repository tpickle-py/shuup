# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
import json
import os
import subprocess

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None


def get_version(version, root, version_file):
    """
    Get version from pyproject.toml or from git or from version_file.

    This function provides version management with the following priority:
    1. If version does not contain 'dev', use as-is
    2. If in a Git checkout, try to get version with git describe
    3. Fall back to version from pyproject.toml
    4. Fall back to version_file if all else fails
    """
    # First try to get version from pyproject.toml
    pyproject_version = _get_version_from_pyproject(root)
    if pyproject_version and "dev" not in version:
        return pyproject_version

    # If version doesn't contain 'dev', use it as-is
    if "dev" not in version:
        return version

    git_repo_path = os.path.join(root, ".git")

    if os.path.exists(git_repo_path) and not os.path.isdir(git_repo_path):
        _remove_git_file_if_invalid(git_repo_path)

    # Try git describe for development versions
    if os.path.exists(git_repo_path):
        git_version = _get_version_from_git(version, root)
        if git_version:
            return git_version

    # Fall back to pyproject.toml version
    if pyproject_version:
        return pyproject_version

    # Final fallback to version file
    return _get_version_from_file(version_file, version) or version


def _get_version_from_pyproject(root):
    """
    Get version from pyproject.toml using uv.
    """
    try:
        result = subprocess.run(["uv", "version", "--short"], cwd=root, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fall back to manual TOML reading if uv is not available
        return _get_version_from_pyproject_fallback(root)


def _get_version_from_pyproject_fallback(root):
    """
    Fallback method to get version from pyproject.toml file manually.
    """
    if not tomllib:
        return None

    pyproject_path = os.path.join(root, "pyproject.toml")

    if not os.path.exists(pyproject_path):
        return None

    try:
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)

        project = pyproject_data.get("project", {})
        return project.get("version")
    except Exception:
        return None


def _remove_git_file_if_invalid(git_file_path):
    """
    Remove invalid .git file.

    This is needed, because .git file that points to non-existing
    directory will cause problems with build_resources, since some git
    commands are executed there and invalid .git file will cause them to
    fail with error like

      fatal: Not a git repository: ../.git/modules/shuup

    Invalid .git files are created when "pip install" copies shuup from
    a Git submodule to temporary build directory, for example.
    """
    with open(git_file_path, "rb") as fp:
        contents = fp.read(10000).decode("utf-8")
    if contents.startswith("gitdir: "):
        gitdir = contents.split(" ", 1)[1].rstrip()
        if not os.path.isabs(gitdir):
            gitdir = os.path.join(os.path.dirname(git_file_path), gitdir)
        if not os.path.exists(gitdir):
            os.remove(git_file_path)


def _get_version_from_git(version, root):
    tag_name = "v" + version.split(".post")[0].split(".dev")[0]
    describe_cmd = ["git", "describe", "--dirty", "--match", tag_name]
    try:
        described = subprocess.check_output(describe_cmd, cwd=root)
    except Exception:
        return None
    suffix = described.decode("utf-8")[len(tag_name) :].strip()
    cleaned_suffix = suffix[1:].replace("-g", "+g").replace("-dirty", ".dirty")
    return version + cleaned_suffix


def _get_version_from_file(version_file, version_prefix=""):
    verstr = ""
    if os.path.exists(version_file):
        with open(version_file) as fp:
            verstr = fp.read(100).strip()
    if verstr.startswith('__version__ = "' + version_prefix):
        return verstr.split('"', 2)[1]
    return None


def write_version_to_file(version, version_file, update_pyproject=True):
    """
    Write version to version file and optionally update pyproject.toml.
    """
    with open(version_file, "w") as fp:
        fp.write(f'__version__ = "{str(version)}"\n')

    # Also update pyproject.toml if requested
    if update_pyproject:
        root = os.path.dirname(os.path.dirname(version_file))
        write_version_to_pyproject(version, root)


def write_version_to_pyproject(version, root):
    """
    Write version to pyproject.toml using uv.
    """
    try:
        subprocess.run(["uv", "version", str(version)], cwd=root, check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fall back to manual TOML writing if uv is not available
        return _write_version_to_pyproject_fallback(version, root)


def _write_version_to_pyproject_fallback(version, root):
    """
    Fallback method to write version to pyproject.toml file manually.
    """
    pyproject_path = os.path.join(root, "pyproject.toml")

    if not os.path.exists(pyproject_path):
        return False

    try:
        # Write back to file using simple string replacement to preserve formatting
        with open(pyproject_path, encoding="utf-8") as f:
            content = f.read()

        # Find and replace the version line
        import re

        version_pattern = r'version\s*=\s*"[^"]*"'
        new_version_line = f'version = "{version}"'

        if re.search(version_pattern, content):
            content = re.sub(version_pattern, new_version_line, content)
        else:
            # If version line doesn't exist, add it after name in [project] section
            project_pattern = r'(\[project\][^\[]*name\s*=\s*"[^"]*")'
            if re.search(project_pattern, content):
                content = re.sub(project_pattern, r"\1\n" + new_version_line, content)

        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(content)

        return True
    except Exception:
        return False


def get_current_version(root):
    """
    Get the current version from pyproject.toml.
    """
    return _get_version_from_pyproject(root)


def update_version_in_pyproject(root, new_version):
    """
    Update version in pyproject.toml and return the new version.
    """
    if write_version_to_pyproject(new_version, root):
        return new_version
    return None


def bump_version(root, bump_type="patch"):
    """
    Bump version in pyproject.toml using uv's built-in version management.

    Args:
        root: Root directory of the project
        bump_type: Type of bump - 'major', 'minor', or 'patch'

    Returns:
        New version string or None if failed
    """
    if bump_type not in ["major", "minor", "patch"]:
        return None

    try:
        # Use uv's built-in version bumping
        _result = subprocess.run(
            ["uv", "version", "--bump", bump_type], cwd=root, capture_output=True, text=True, check=True
        )

        # Get the new version
        new_version_result = subprocess.run(
            ["uv", "version", "--short"], cwd=root, capture_output=True, text=True, check=True
        )

        return new_version_result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fall back to manual version bumping if uv is not available
        return _bump_version_fallback(root, bump_type)


def _bump_version_fallback(root, bump_type="patch"):
    """
    Fallback method to bump version manually when uv is not available.
    """
    current_version = get_current_version(root)
    if not current_version:
        return None

    try:
        # Parse current version
        parts = current_version.split(".")
        if len(parts) < 3:
            return None

        major, minor, patch = map(int, parts[:3])

        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            return None

        new_version = f"{major}.{minor}.{patch}"

        # Add any pre-release or build metadata from original version
        if len(parts) > 3:
            new_version += "." + ".".join(parts[3:])

        # Update pyproject.toml
        if write_version_to_pyproject(new_version, root):
            return new_version

        return None
    except (ValueError, IndexError):
        return None


def check_version_dry_run(root, bump_type="patch"):
    """
    Check what the new version would be without actually changing it.
    Uses uv's --dry-run functionality.

    Args:
        root: Root directory of the project
        bump_type: Type of bump - 'major', 'minor', or 'patch'

    Returns:
        Tuple of (current_version, new_version) or (None, None) if failed
    """
    if bump_type not in ["major", "minor", "patch"]:
        return None, None

    try:
        # Get current version
        current_result = subprocess.run(
            ["uv", "version", "--short"], cwd=root, capture_output=True, text=True, check=True
        )
        current_version = current_result.stdout.strip()

        # Check what the bump would produce
        bump_result = subprocess.run(
            ["uv", "version", "--bump", bump_type, "--dry-run"], cwd=root, capture_output=True, text=True, check=True
        )

        # Parse the output to get the new version
        # uv outputs something like "shuup 3.2.26 => 3.2.27"
        output = bump_result.stdout.strip()
        if " => " in output:
            new_version = output.split(" => ")[-1].strip()
            return current_version, new_version

        return current_version, None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, None


def get_version_info_json(root):
    """
    Get version information in JSON format using uv.

    Args:
        root: Root directory of the project

    Returns:
        Dict with version information or None if failed
    """
    try:
        result = subprocess.run(
            ["uv", "version", "--output-format", "json"], cwd=root, capture_output=True, text=True, check=True
        )

        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return None


def set_specific_version(root, version):
    """
    Set a specific version using uv.

    Args:
        root: Root directory of the project
        version: The version string to set

    Returns:
        True if successful, False otherwise
    """
    try:
        subprocess.run(["uv", "version", str(version)], cwd=root, check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
