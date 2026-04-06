#!/usr/bin/env bash
# One-time setup for gmail-cleanup
# Works on macOS, Linux, and Windows (Git Bash / WSL)
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Find Python 3
find_python() {
    # Check common locations in priority order
    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then
            # Verify it's Python 3
            if "$cmd" -c "import sys; assert sys.version_info >= (3, 9)" 2>/dev/null; then
                echo "$cmd"
                return 0
            fi
        fi
    done

    # macOS Homebrew paths
    for p in /opt/homebrew/bin/python3 /usr/local/bin/python3; do
        if [ -x "$p" ]; then
            echo "$p"
            return 0
        fi
    done

    return 1
}

PY=$(find_python) || {
    echo "Error: Python 3.9+ not found."
    echo ""
    echo "Install Python:"
    echo "  macOS:   brew install python"
    echo "  Ubuntu:  sudo apt install python3 python3-venv"
    echo "  Fedora:  sudo dnf install python3"
    echo "  Windows: https://www.python.org/downloads/"
    exit 1
}

echo "Using Python: $PY ($($PY --version))"

# Create venv if missing
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PY -m venv venv
fi

# Activate and install — handle Windows vs Unix venv layout
if [ -f "venv/Scripts/pip" ]; then
    PIP="venv/Scripts/pip"
elif [ -f "venv/bin/pip" ]; then
    PIP="venv/bin/pip"
else
    echo "Error: venv created but pip not found. Try deleting venv/ and re-running."
    exit 1
fi

echo "Installing dependencies..."
$PIP install -q -r requirements.txt

echo ""
echo "Setup complete."
echo ""

# Check for credentials
if [ ! -f "credentials.json" ]; then
    echo "NEXT STEP: You need credentials.json from Google Cloud Console."
    echo "Run /gmail-cleanup in Claude Code — it will walk you through it."
    echo ""
else
    echo "credentials.json found. Ready to go."
fi
