#!/bin/bash
# N5OS Ode Installer
# Moves repo contents to workspace root and cleans up

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="/home/workspace"

echo "🚀 N5OS Ode Installer"
echo "====================="
echo ""

# Check if we're inside the cloned repo
if [[ ! -f "$SCRIPT_DIR/BOOTLOADER.prompt.md" ]]; then
    echo "❌ Error: Run this script from inside the n5os-ode directory"
    exit 1
fi

# Check if already at workspace root
if [[ "$SCRIPT_DIR" == "$WORKSPACE_ROOT" ]]; then
    echo "✅ Already at workspace root. Nothing to move."
    echo "   Run: @BOOTLOADER.prompt.md to complete setup"
    exit 0
fi

echo "📂 Moving N5OS Ode contents to workspace root..."
echo "   From: $SCRIPT_DIR"
echo "   To:   $WORKSPACE_ROOT"
echo ""

# List of directories/files to move
ITEMS=(
    "N5"
    "Knowledge"
    "Lists"
    "Prompts"
    "Records"
    "templates"
    "docs"
    "scripts"
    "BOOTLOADER.prompt.md"
    "PERSONALIZE.prompt.md"
    "CHANGELOG.md"
    "README.md"
)

# Move each item, merging if directory exists
for item in "${ITEMS[@]}"; do
    src="$SCRIPT_DIR/$item"
    dst="$WORKSPACE_ROOT/$item"
    
    if [[ ! -e "$src" ]]; then
        continue
    fi
    
    if [[ -d "$src" ]]; then
        if [[ -d "$dst" ]]; then
            echo "   📁 Merging $item/ (directory exists)"
            cp -rn "$src"/* "$dst"/ 2>/dev/null || cp -r "$src"/* "$dst"/
        else
            echo "   📁 Moving $item/"
            mv "$src" "$dst"
        fi
    else
        if [[ -f "$dst" ]]; then
            echo "   📄 Skipping $item (already exists)"
        else
            echo "   📄 Moving $item"
            mv "$src" "$dst"
        fi
    fi
done

# Clean up the now-empty repo directory
REPO_NAME="$(basename "$SCRIPT_DIR")"
echo ""
echo "🧹 Cleaning up $REPO_NAME/ directory..."

# Remove remaining files (LICENSE, .git, etc)
cd "$WORKSPACE_ROOT"
rm -rf "$SCRIPT_DIR"

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Open a new Zo conversation"
echo "  2. Run: @BOOTLOADER.prompt.md"
echo "  3. Then: @PERSONALIZE.prompt.md"
echo ""
