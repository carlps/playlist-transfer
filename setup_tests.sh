#!/bin/bash

# Test Suite First Run Script
# This script helps you get started with the test suite

set -e  # Exit on error

echo "🎵 Playlist Transfer - Test Suite Setup"
echo "========================================"
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "   Found Python $python_version"

# Check if Python version is >= 3.8
if ! python -c "import sys; assert sys.version_info >= (3, 8)" 2>/dev/null; then
    echo "   ❌ Python 3.8+ required. Please upgrade Python."
    exit 1
fi
echo "   ✅ Python version OK"
echo ""

# Install dev dependencies
echo "2️⃣  Installing development dependencies..."
pip install -e ".[dev]" --quiet
echo "   ✅ Dependencies installed"
echo ""

# Run tests
echo "3️⃣  Running test suite..."
pytest
echo ""

# Run with coverage
echo "4️⃣  Running tests with coverage..."
pytest --cov=playlist_transfer --cov-report=term-missing
echo ""

# Check formatting
echo "5️⃣  Checking code formatting..."
black --check playlist_transfer tests 2>/dev/null && echo "   ✅ Code formatting OK" || {
    echo "   ⚠️  Code needs formatting. Run: make format"
}
echo ""

# Check linting
echo "6️⃣  Checking code style..."
flake8 playlist_transfer tests 2>/dev/null && echo "   ✅ Code style OK" || {
    echo "   ⚠️  Linting issues found. Run: make lint"
}
echo ""

echo "✨ Test suite setup complete!"
echo ""
echo "📚 Next steps:"
echo "   • Read TESTING_QUICKSTART.md for quick reference"
echo "   • Read TESTING.md for comprehensive guide"
echo "   • Run 'make help' to see available commands"
echo "   • Run 'make ci' before committing code"
echo ""
echo "🚀 Happy testing!"
