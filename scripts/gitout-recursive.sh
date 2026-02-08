#!/usr/bin/env bash
set -euo pipefail

# Recursive "git add/commit/push" for the superproject + all submodules.
# Intended to match: git add . && git commit -m "auto" && git push
# but uses add -A and skips clean/detached repos.

MSG="auto"
NO_VERIFY=0

print_help() {
  cat <<'EOF'
Usage: scripts/gitout-recursive.sh [--message MSG] [--no-verify]

Runs, for the superproject and every (initialized) submodule recursively:
  git add -A
  git commit -m MSG
  git push

Skips:
- clean repos (nothing staged after add)
- detached HEAD repos

Notes:
- Uses `git -c safe.directory=...` per repo to avoid "dubious ownership" blocks.
- If push fails (non-ff, auth, etc.), the script continues to the next repo.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --message|-m)
      shift
      MSG="${1:-}"
      if [[ -z "$MSG" ]]; then
        echo "ERROR: --message requires an argument" >&2
        exit 2
      fi
      ;;
    --no-verify)
      NO_VERIFY=1
      ;;
    -h|--help)
      print_help
      exit 0
      ;;
    *)
      # Convenience: first bare arg is message.
      MSG="$1"
      ;;
  esac
  shift
done

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT_DIR"

git_root() {
  git -c "safe.directory=$ROOT_DIR" -C "$ROOT_DIR" "$@"
}

if ! git_root rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not inside a git repository: $ROOT_DIR" >&2
  exit 1
fi

collect_repos() {
  local -a repos=()
  repos+=("$ROOT_DIR")

  # If submodules aren't initialized, `git submodule status --recursive` won't list them.
  # That's fine; we only operate on actual worktrees on disk.
  local -a subs=()
  mapfile -t subs < <(git_root submodule status --recursive 2>/dev/null | awk '{print $2}' || true)
  for p in "${subs[@]}"; do
    [[ -n "$p" ]] || continue
    if [[ -e "$ROOT_DIR/$p/.git" ]]; then
      repos+=("$ROOT_DIR/$p")
    fi
  done

  printf '%s\n' "${repos[@]}" | awk '!seen[$0]++'
}

gitout_one() {
  local repo="$1"
  local abs
  abs="$(cd "$repo" && pwd)"

  g() { git -c "safe.directory=$abs" -C "$repo" "$@"; }

  if ! g rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "SKIP: not a git worktree: $repo"
    return 0
  fi

  local branch=""
  branch="$(g symbolic-ref --short -q HEAD || true)"
  if [[ -z "$branch" ]]; then
    echo "SKIP: detached HEAD: $repo"
    return 0
  fi

  echo "==> $repo ($branch)"

  g add -A
  if g diff --cached --quiet; then
    echo "SKIP: clean"
    echo
    return 0
  fi

  local -a commit_args=()
  commit_args+=(commit -m "$MSG")
  if [[ "$NO_VERIFY" -eq 1 ]]; then
    commit_args+=(--no-verify)
  fi

  if ! g "${commit_args[@]}"; then
    echo "FAIL: commit failed (leaving index as-is)"
    echo
    return 1
  fi

  if ! g push; then
    echo "FAIL: push failed (commit kept locally)"
    echo
    return 1
  fi

  echo "OK"
  echo
  return 0
}

fail=0
while IFS= read -r repo; do
  if ! gitout_one "$repo"; then
    fail=1
  fi
done < <(collect_repos)

exit "$fail"

