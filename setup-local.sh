#!/bin/bash

echo "🚀 Setting up Missing Person Finder for local development..."

# Check if Python 3.8+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.8+ is required but not installed."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Open VSCode: code missing-person-finder.code-workspace"
echo "2. Or open the folder in VSCode: code ."
echo "3. Press F5 or run 'Run Missing Person Finder' from the debug panel"
echo "4. Open http://127.0.0.1:8000 in your browser"
echo ""
echo "💡 Available commands:"
echo "   • Ctrl+Shift+P → 'Tasks: Run Task' → 'Run Server'"
echo "   • F5 to debug the application"
echo "   • Ctrl+Shift+P → 'Python: Select Interpreter' (should auto-detect .venv)"
