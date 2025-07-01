#!/usr/bin/env bash
# Regenerate all requirements files from pyproject.toml
#
# This script creates both full (with all transitive dependencies) and minimal
# (only direct dependencies) versions of requirements files.

set -e

echo "🔄 Regenerating requirements files from pyproject.toml..."

# Generate full requirements files (includes all transitive dependencies)
echo "📦 Generating full requirements files..."
uv export --no-hashes --no-annotate --format requirements-txt > requirements.txt
uv export --group dev --no-hashes --no-annotate --format requirements-txt > requirements-dev.txt
uv export --group test --no-hashes --no-annotate --format requirements-txt > requirements-tests.txt
uv export --group docs --no-hashes --no-annotate --format requirements-txt > requirements-doc.txt
uv export --group dev --group test --no-hashes --no-annotate --format requirements-txt > requirements-dev-ci.txt

# Generate minimal requirements files (only direct dependencies)
echo "📋 Generating minimal requirements files..."
uv run python generate_requirements.py

echo "✅ All requirements files regenerated!"
echo ""
echo "📄 Full requirements files (with transitive dependencies):"
echo "   - requirements.txt ($(wc -l < requirements.txt) lines)"
echo "   - requirements-dev.txt ($(wc -l < requirements-dev.txt) lines)"
echo "   - requirements-tests.txt ($(wc -l < requirements-tests.txt) lines)"
echo "   - requirements-doc.txt ($(wc -l < requirements-doc.txt) lines)"
echo "   - requirements-dev-ci.txt ($(wc -l < requirements-dev-ci.txt) lines)"
echo ""
echo "📋 Minimal requirements files (direct dependencies only):"
echo "   - requirements-minimal.txt ($(wc -l < requirements-minimal.txt) lines)"
echo "   - requirements-dev-minimal.txt ($(wc -l < requirements-dev-minimal.txt) lines)"
echo "   - requirements-test-minimal.txt ($(wc -l < requirements-test-minimal.txt) lines)"
echo "   - requirements-doc-minimal.txt ($(wc -l < requirements-doc-minimal.txt) lines)"
echo "   - requirements-dev-ci-minimal.txt ($(wc -l < requirements-dev-ci-minimal.txt) lines)"
echo ""
echo "💡 Use minimal files for Docker/containers and full files for precise reproducibility."
