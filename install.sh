#!/bin/bash
# mgit - One-Line Installer
# Usage: curl -sSL https://raw.githubusercontent.com/PrajsRamteke/mgit/main/install.sh | bash

set -e

echo "🚀 Installing mgit..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required. Please install Python 3.8+ first."
    exit 1
fi

# Try pipx first (recommended for CLI tools)
if command -v pipx &> /dev/null; then
    echo "📦 Using pipx..."
    pipx install git+https://github.com/PrajsRamteke/mgit.git
elif command -v pip3 &> /dev/null; then
    echo "📦 Using pip3..."
    pip3 install --user git+https://github.com/PrajsRamteke/mgit.git
elif command -v pip &> /dev/null; then
    echo "📦 Using pip..."
    pip install --user git+https://github.com/PrajsRamteke/mgit.git
else
    echo "❌ pip or pipx not found. Please install pip first."
    exit 1
fi

echo ""
echo "✅ mgit installed successfully!"
echo ""
echo "🚀 Quick start:"
echo "   mgit add YourGitHubUsername -d    # Add your first account"
echo "   mgit key YourGitHubUsername       # Get SSH key to add to GitHub"
echo "   mgit ls                           # List all accounts"
echo ""
