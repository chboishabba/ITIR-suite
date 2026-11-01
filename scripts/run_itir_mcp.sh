#!/usr/bin/env bash
set -a
if [[ -f /home/c/Documents/code/ITIR-suite/SensibLaw/.env ]]; then
  . /home/c/Documents/code/ITIR-suite/SensibLaw/.env
fi
set +a
exec /home/c/Documents/code/ITIR-suite/.venv/bin/python -m itir_mcp
