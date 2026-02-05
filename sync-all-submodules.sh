#!/bin/bash

# 1. Sync all submodules
git submodule foreach '
    echo "Syncing $name..."
    git pull
    git add .
    # Only commit if there are changes
    if ! git diff-index --quiet HEAD --; then
        git commit -m "auto-sync: updates and docs"
        # Only attempt push if you have write access (or ignore failure)
        git push origin $(git rev-parse --abbrev-ref HEAD) || echo "Push failed for $name - check permissions/forks"
    else
        echo "No changes in $name"
    fi
'

# 2. Sync the base suite
echo "Syncing ITIR-suite base..."
git add .
git commit -m "chore: update submodule pointers and base files" || echo "No changes in base"
git push
