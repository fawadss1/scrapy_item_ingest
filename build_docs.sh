#!/bin/bash
# Build script for Scrapy Item Ingest documentation

set -e

echo "🔧 Setting up documentation build environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install documentation requirements
echo "📦 Installing documentation dependencies..."
pip install -r docs/requirements.txt

# Install the project in development mode
pip install -e .

echo "📚 Building documentation..."

# Clean previous builds
rm -rf docs/_build

# Build HTML documentation
cd docs
make html

echo "✅ Documentation built successfully!"
echo "📖 Open docs/_build/html/index.html to view the documentation"

# Optional: Start local server
if [ "$1" = "--serve" ]; then
    echo "🌐 Starting local documentation server..."
    cd _build/html
    python -m http.server 8000
fi
