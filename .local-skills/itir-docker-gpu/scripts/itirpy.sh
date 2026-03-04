#!/usr/bin/env bash
set -euo pipefail

# Run container Python (always /Whisper-WebUI/venv/bin/python) inside ITIR.

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/itir-exec.sh" /Whisper-WebUI/venv/bin/python "$@"

