#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${ITIR_CONTAINER:-ITIR}"
WORKDIR="${ITIR_WORKDIR:-/home/c/Documents/code/ITIR-suite}"

echo "[check] docker version:"
docker --version

echo "[check] container exists and is running:"
docker ps --format '{{.Names}}' | grep -qx "${CONTAINER}"
echo "  OK: ${CONTAINER} is running"

echo "[check] workdir exists in container:"
docker exec "${CONTAINER}" test -d "${WORKDIR}"
echo "  OK: ${WORKDIR}"

echo "[check] python exists in container:"
docker exec "${CONTAINER}" test -x /Whisper-WebUI/venv/bin/python
echo "  OK: /Whisper-WebUI/venv/bin/python"
