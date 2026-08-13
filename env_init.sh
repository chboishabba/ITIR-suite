#!/usr/bin/env bash
set -euo pipefail

ROOT_REQ="requirements_clean.txt"
VENV_DIR=".venv"

# Prefer newest Python < 3.14
PYTHON_BIN=""
for py in python3.{13..10}; do
    if command -v "$py" >/dev/null 2>&1; then
        PYTHON_BIN="$py"
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "❌ Python < 3.14 is required -- too new and no vers available.. Suggested: (3.13 / 3.12 / 3.11 / 3.10)"
    exit 1
fi

echo "🐍 Using $PYTHON_BIN"

echo "🔍 Aggregating requirements..."
> "$ROOT_REQ"
find . -maxdepth 3 -name "requirements.txt" \
  ! -path "./$ROOT_REQ" \
  ! -path "./.venv/*" \
  ! -path "./.git/*" \
  -exec cat {} + | sort -u > "$ROOT_REQ"

# Create venv if missing
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating venv..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

echo "🚀 Installing requirements..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip wheel setuptools
pip install -r "$ROOT_REQ"

echo "✨ Ready. Activate with:"
echo "   source $VENV_DIR/bin/activate"
