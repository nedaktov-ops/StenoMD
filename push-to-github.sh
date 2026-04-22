#!/bin/bash
# Push script for StenoMD repository

echo "StenoMD - GitHub Push Helper"
echo "==========================="
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "Installing GitHub CLI..."
    sudo apt update
    sudo apt install -y gh
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo "Not authenticated with GitHub."
    echo "Run: gh auth login"
    echo ""
    echo "Or use GitHub Personal Access Token:"
    echo "  1. Go to: https://github.com/settings/tokens"
    echo "  2. Create new token (repo scope)"
    echo "  3. Run: git remote set-url https://TOKEN@github.com/nedaktov-ops/StenoMD.git"
    echo "  4. Then run: git push -u origin master"
    exit 1
fi

# Push
echo "Pushing to GitHub..."
cd "$(dirname "$0")"
git push -u origin master

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to https://github.com/nedaktov-ops/StenoMD"
else
    echo "❌ Push failed"
    exit 1
fi