#!/usr/bin/env bash
# mgit - One-Line Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/PrajsRamteke/mgit/main/install.sh | bash

set -euo pipefail

MGIT_SOURCE="${MGIT_SOURCE:-git+https://github.com/PrajsRamteke/mgit.git}"
MGIT_INSTALL_DIR="${MGIT_INSTALL_DIR:-$HOME/.local/share/mgit}"
MGIT_BIN_DIR="${MGIT_BIN_DIR:-$HOME/.local/bin}"
MGIT_VENV_DIR="$MGIT_INSTALL_DIR/venv"

print_error() {
    echo "ERROR: $1" >&2
}

require_command() {
    local cmd="$1"
    local help_text="$2"
    if ! command -v "$cmd" >/dev/null 2>&1; then
        print_error "$help_text"
        exit 1
    fi
}

install_with_pipx() {
    echo "Using pipx..."
    pipx ensurepath >/dev/null 2>&1 || true
    pipx install --force "$MGIT_SOURCE"
}

install_with_venv() {
    echo "Using isolated virtualenv (no system pip changes)..."
    mkdir -p "$MGIT_INSTALL_DIR" "$MGIT_BIN_DIR"

    if [ ! -d "$MGIT_VENV_DIR" ]; then
        python3 -m venv "$MGIT_VENV_DIR"
    fi

    # Best-effort pip bootstrap; continue with bundled pip if upgrade fails.
    "$MGIT_VENV_DIR/bin/python" -m ensurepip --upgrade >/dev/null 2>&1 || true
    "$MGIT_VENV_DIR/bin/python" -m pip install --upgrade pip >/dev/null 2>&1 || true
    "$MGIT_VENV_DIR/bin/python" -m pip install --upgrade "$MGIT_SOURCE"

    ln -sf "$MGIT_VENV_DIR/bin/mgit" "$MGIT_BIN_DIR/mgit"
}

echo "Installing mgit..."
echo ""

require_command "python3" "Python 3.8+ is required. Install Python and retry."
require_command "git" "Git is required to install from GitHub. Install git and retry."

if command -v pipx >/dev/null 2>&1; then
    install_with_pipx
else
    install_with_venv
fi

echo ""
echo "mgit installed successfully."

if ! command -v mgit >/dev/null 2>&1; then
    case ":${PATH}:" in
        *":$MGIT_BIN_DIR:"*)
            ;;
        *)
            echo ""
            echo "Add this to your shell profile, then restart your shell:"
            echo "  export PATH=\"$MGIT_BIN_DIR:\$PATH\""
            ;;
    esac
fi

echo ""
echo "Quick start:"
echo "  mgit add YourGitHubUsername -d    # Add your first account"
echo "  mgit key YourGitHubUsername       # Get SSH key to add to GitHub"
echo "  mgit ls                           # List all accounts"
