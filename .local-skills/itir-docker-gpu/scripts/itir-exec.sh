#!/usr/bin/env bash
set -euo pipefail

# Run an arbitrary command inside the ITIR container, with the repo workdir set.
#
# Environment variables:
# - ITIR_CONTAINER: container name (default: ITIR)
# - ITIR_WORKDIR: container workdir (default: /home/c/Documents/code/ITIR-suite)
# - ITIR_USER: optional docker exec -u value (unset by default)
#
# Note: Adds -t only when attached to a TTY, so this works in non-interactive runs too.

CONTAINER="${ITIR_CONTAINER:-ITIR}"
WORKDIR="${ITIR_WORKDIR:-/home/c/Documents/code/ITIR-suite}"

tty_args=()
# Allocate stdin/tty only when this process is attached to a TTY.
if [ -t 0 ]; then
  tty_args+=("-i")
fi
if [ -t 0 ] && [ -t 1 ]; then
  tty_args+=("-t")
fi

user_args=()
if [ "${ITIR_USER:-}" != "" ]; then
  user_args+=("-u" "${ITIR_USER}")
fi

exec docker exec "${tty_args[@]}" -w "${WORKDIR}" "${user_args[@]}" "${CONTAINER}" "$@"
