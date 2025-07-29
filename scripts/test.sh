#!/bin/bash
# Test runner script for EMBL-EBI Protein MCP Server

set -e

echo "🧬 Running EMBL-EBI Protein MCP Server Tests"
echo "============================================"

# Check if we're in a virtual environment
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo "⚠️  Warning: Not in a virtual environment"
    echo "   Consider running: source venv/bin/activate"
    echo ""
fi

# Install test dependencies if not already installed
echo "📦 Installing test dependencies..."
pip install -e .[dev] > /dev/null 2>&1

echo ""
echo "🧪 Running unit tests..."
pytest tests/ -m "unit" -v

echo ""
echo "🔗 Running integration tests (with mocked APIs)..."
pytest tests/ -m "integration" -v

echo ""
echo "📊 Running all tests with coverage..."
pytest tests/ -v --cov=embl_ebi_protein_mcp --cov-report=term-missing --cov-report=html

echo ""
echo "✅ All tests completed!"
echo "📋 Coverage report available in htmlcov/index.html"