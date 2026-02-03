#!/bin/bash

# Define where your original, populated projects live
ORIGINAL_PROJECTS_DIR=".."
ROOT_DIR=$(pwd)
FINAL_REQ="$ROOT_DIR/requirements.txt"

echo "# Combined Requirements from External Folders - $(date)" > "$FINAL_REQ"

# List of folder names to check in the parent directory
PROJECTS=("SensibLaw" "SL-reasoner" "tircorder-JOBBIE" "WhisperX-WebUI" "reverse-engineered-chatgpt")

for proj in "${PROJECTS[@]}"; do
    TARGET="$ORIGINAL_PROJECTS_DIR/$proj"
    echo "📂 Auditing $TARGET..."
    
    if [ -d "$TARGET" ]; then
        found=0
        # Check common venv names in the original folders
        for venv in ".venv" "venv" "env"; do
            if [ -d "$TARGET/$venv" ]; then
                echo "  🐍 Found $venv! Freezing..."
                (
                    source "$TARGET/$venv/bin/activate"
                    echo "# From original $proj ($venv)" >> "$FINAL_REQ"
                    pip freeze | grep -v "pkg-resources" >> "$FINAL_REQ"
                    echo "" >> "$FINAL_REQ"
                )
                found=1
                break
            fi
        done
        
        if [ $found -eq 0 ]; then
            echo "  ⚠️ No venv found in $TARGET. Checking for requirements.txt..."
            if [ -f "$TARGET/requirements.txt" ]; then
                cat "$TARGET/requirements.txt" >> "$FINAL_REQ"
                echo "  📄 Copied raw requirements.txt instead."
            fi
        fi
    else
        echo "  ❌ Directory $TARGET not found."
    fi
done

# Deduping for a clean list
grep -v '^#' "$FINAL_REQ" | grep -v '^$' | sort -u > "$ROOT_DIR/requirements_clean.txt"

echo "--------------------------------------"
echo "✅ Done! Master list: requirements_clean.txt"
