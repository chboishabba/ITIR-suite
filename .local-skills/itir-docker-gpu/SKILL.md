---
name: itir-docker-gpu
description: Run commands inside the docker container named "ITIR" (RX580 GPU-enabled) with the repo mounted at /home/c/Documents/code/ITIR-suite. Use when a command needs GPU/ROCm acceleration or the container environment, or when running Python must use /Whisper-WebUI/venv/bin/python instead of the host interpreter. Use for running training/inference, Whisper/ML workflows, or any Python CLI/scripts that must execute in the ITIR container.
---

# ITIR Docker GPU

## Overview

Standardize how to run commands in the `ITIR` docker container, using the container Python interpreter at `/Whisper-WebUI/venv/bin/python`, with the repo available at `/home/c/Documents/code/ITIR-suite` inside the container.

## Quick Start

- Prefer the wrappers in this skill's `scripts/` (they handle workdir and TTY flags):

```bash
# Adjust if the skill folder lives elsewhere on your machine.
SKILL_DIR="/home/c/.codex/skills/itir-docker-gpu"

# Run arbitrary command in the container (workdir set to /home/c/Documents/code/ITIR-suite)
"$SKILL_DIR/scripts/itir-exec.sh" bash -lc 'pwd && ls'

# Run Python inside the container (always uses /Whisper-WebUI/venv/bin/python)
"$SKILL_DIR/scripts/itirpy.sh" -c 'import sys; print(sys.executable)'

# Run pip/pytest the safe way (via python -m ...)
"$SKILL_DIR/scripts/itirpy.sh" -m pip -V
"$SKILL_DIR/scripts/itirpy.sh" -m pytest -q
```

## Workflow Decision

- If the command is Python (scripts, CLIs, tests) and the requirement is "use `/Whisper-WebUI/venv/bin/python`": run it in the container via `scripts/itirpy.sh`.
- If the command needs GPU acceleration (ROCm / AMD RX580): run it in the container via `scripts/itir-exec.sh` (or `scripts/itirpy.sh` if it's Python).
- If the task is pure text manipulation (editing files, `rg`, `sed`, etc.) and does not need Python/GPU: run on the host.

## Sandbox / Permission Note

- In this Codex environment, running `docker` (including `docker exec`) may require an escalated exec permission prompt. Approve that prompt or the wrappers will fail.

## Command Patterns

### Run a Python script in the repo

```bash
"$SKILL_DIR/scripts/itirpy.sh" path/to/script.py --help
```

### Run a module / CLI entrypoint

```bash
"$SKILL_DIR/scripts/itirpy.sh" -m some_module --arg value
```

### Run bash with venv active

Use this when you need shell features or multiple commands:

```bash
"$SKILL_DIR/scripts/itir-exec.sh" bash -lc 'source /Whisper-WebUI/venv/bin/activate && python -V && which python'
```

### Set container/workdir

Wrappers support:

- `ITIR_CONTAINER`: container name (default `ITIR`)
- `ITIR_WORKDIR`: workdir inside container (default `/home/c/Documents/code/ITIR-suite`)
- `ITIR_USER`: optional `docker exec -u` value (only set if you know the container user setup)

## Troubleshooting

- If docker commands fail with `permission denied` for the docker socket: you likely need the user to run the command, or to use `sudo docker ...` (if available).
- If the container is not running: start it (outside this skill), then re-run `"$SKILL_DIR/scripts/itir-check.sh"`.
- If relative paths behave unexpectedly: confirm the workdir with `"$SKILL_DIR/scripts/itir-exec.sh" pwd` (it should be `/home/c/Documents/code/ITIR-suite`).
