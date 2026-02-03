#!/bin/bash

ROOT_REQ="requirements.txt"
VENV_DIR=".venv"

echo "🔍 Aggregating requirements from submodules..."

# Clear existing root requirements (or create it)
> "$ROOT_REQ"

# Find all requirements.txt in submodules and append to root
# Sort/Uniq removes duplicate libraries across projects
find . -maxdepth 2 -name "requirements.txt" ! -path "./$ROOT_REQ" -exec cat {} + | sort -u > "$ROOT_REQ"

echo "✅ Compiled unique requirements into $ROOT_REQ"

# Setup Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

echo "🚀 Installing requirements..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$ROOT_REQ"

echo "✨ Environment is ready! Run 'source $VENV_DIR/bin/activate' to begin."
