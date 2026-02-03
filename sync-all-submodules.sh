#!/bin/bash

# 1. Sync all submodules
# This loops through every submodule and runs the commands
git submodule foreach 'echo "Syncing $name..."; git add .; git commit -m "auto-sync" || echo "No changes"; git push'

# 2. Sync the base suite (to track the new submodule pointers)
echo "Syncing ITIR-suite base..."
git add .
git commit -m "auto-sync base" || echo "No changes"
git push
