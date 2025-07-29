#!/bin/bash
# Linting and code quality script

set -e

echo "🔍 Running Code Quality Checks"
echo "=============================="

# Install dev dependencies
pip install -e .[dev] > /dev/null 2>&1

echo ""
echo "🖤 Running Black (code formatting)..."
black embl_ebi_protein_mcp/ tests/ --check --diff

echo ""
echo "📏 Running Flake8 (linting)..."
flake8 embl_ebi_protein_mcp/ tests/

echo ""
echo "🔍 Running MyPy (type checking)..."
mypy embl_ebi_protein_mcp/

echo ""
echo "✅ All code quality checks passed!"