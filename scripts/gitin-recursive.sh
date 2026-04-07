#!/usr/bin/env bash
set -euo pipefail

# Recursive "git pull" for the superproject plus submodule refresh.
# Intended for consumer/user-side sync where we want to:
# 1. fast-forward the superproject first
# 2. sync submodule URLs from .gitmodules
# 3. align submodules to the superproject's recorded gitlinks
# 4. report branch-attached submodules that are ahead/behind/diverged
#
# Safe defaults:
# - skips dirty repos for the root pull
# - uses `git submodule update --init --recursive` for detached/pinned submodules
# - does not auto-merge or auto-rebase branch-attached submodules
# - reports branch-attached divergence explicitly instead of changing it

DRY_RUN=0

print_help() {
  cat <<'EOF'
Usage: scripts/gitin-recursive.sh [--dry-run]

Runs:
  git pull --ff-only              (superproject only)
  git submodule sync --recursive
  git submodule update --init --recursive

Behavior:
- Pulls the superproject first.
- Runs `git submodule sync --recursive` after the superproject step.
- Aligns submodules to the commits recorded by the superproject.
- Reports branch-attached submodules that are ahead/behind/diverged.

Skips:
- dirty superproject worktree
- branch-attached submodules with local dirt when reporting status

Notes:
- Detached submodules are normal consumer state; they are updated via
  `git submodule update`, not `git pull`.
- Branch-attached submodules are inspected and reported, not rewritten.
- This script does not auto-merge, auto-rebase, commit, or push.
- Use --dry-run to inspect what would be attempted without changing anything.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      ;;
    -h|--help)
      print_help
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      echo >&2
      print_help >&2
      exit 2
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

git_safe() {
  local repo="$1"
  shift
  local abs
  abs="$(cd "$repo" && pwd)"
  git -c "safe.directory=$abs" -C "$repo" "$@"
}

maybe_pull_ff_only() {
  local repo="$1"
  local counts ahead behind

  if ! git_safe "$repo" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' >/dev/null 2>&1; then
    echo "SKIP: no upstream configured"
    return 0
  fi

  counts="$(git_safe "$repo" rev-list --left-right --count HEAD...@{upstream} 2>/dev/null || true)"
  ahead="${counts%%$'\t'*}"
  behind="${counts##*$'\t'}"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    if [[ -n "${ahead:-}" && -n "${behind:-}" ]]; then
      echo "DRY-RUN: would pull --ff-only (ahead=${ahead:-?} behind=${behind:-?})"
    else
      echo "DRY-RUN: would pull --ff-only"
    fi
    return 0
  fi

  if git_safe "$repo" pull --ff-only --no-rebase; then
    echo "OK: pulled"
    return 0
  fi

  if [[ -n "${ahead:-}" && -n "${behind:-}" && "$ahead" =~ ^[0-9]+$ && "$behind" =~ ^[0-9]+$ ]]; then
    if [[ "$ahead" -gt 0 && "$behind" -gt 0 ]]; then
      echo "FAIL: branch has diverged from upstream (ahead=$ahead behind=$behind)"
      echo "INFO: resolve with an explicit rebase or merge in '$repo', then rerun."
      return 1
    fi
  fi

  echo "FAIL: pull --ff-only failed"
  return 1
}

root_is_dirty() {
  ! git_root diff --quiet --ignore-submodules HEAD -- || \
    ! git_root diff --cached --quiet --ignore-submodules
}

collect_repos() {
  local -a subs=()
  mapfile -t subs < <(git_root submodule status --recursive 2>/dev/null | awk '{print $2}' || true)

  local -a repos=()
  for p in "${subs[@]}"; do
    [[ -n "$p" ]] || continue
    if [[ -e "$ROOT_DIR/$p/.git" ]]; then
      repos+=("$ROOT_DIR/$p")
    fi
  done

  printf '%s\n' "${repos[@]}" | awk '!seen[$0]++'
}

fail=0

echo "==> $ROOT_DIR ($(git_root symbolic-ref --short -q HEAD || echo detached))"
if root_is_dirty; then
  echo "SKIP: dirty worktree"
  echo
else
  if ! maybe_pull_ff_only "$ROOT_DIR"; then
    fail=1
  fi
  echo
fi

echo "==> $ROOT_DIR (submodule sync/update)"
if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "DRY-RUN: would run git submodule sync --recursive"
  echo "DRY-RUN: would run git submodule update --init --recursive"
else
  git_root submodule sync --recursive
  git_root submodule update --init --recursive || fail=1
fi
echo

while IFS= read -r repo; do
  [[ -n "$repo" ]] || continue
  if ! git_safe "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    continue
  fi

  local_branch="$(git_safe "$repo" symbolic-ref --short -q HEAD || true)"
  if [[ -z "$local_branch" ]]; then
    continue
  fi

  echo "==> $repo ($local_branch)"
  if ! git_safe "$repo" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' >/dev/null 2>&1; then
    echo "INFO: branch-attached submodule with no upstream configured"
    echo
    continue
  fi

  counts="$(git_safe "$repo" rev-list --left-right --count HEAD...@{upstream} 2>/dev/null || true)"
  ahead="${counts%%$'\t'*}"
  behind="${counts##*$'\t'}"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "DRY-RUN: branch-attached status ahead=${ahead:-?} behind=${behind:-?}"
    echo
    continue
  fi

  if [[ -n "${ahead:-}" && -n "${behind:-}" && "$ahead" =~ ^[0-9]+$ && "$behind" =~ ^[0-9]+$ ]]; then
    if [[ "$ahead" -eq 0 && "$behind" -eq 0 ]]; then
      echo "OK: branch-attached submodule already aligned with upstream"
    elif [[ "$ahead" -gt 0 && "$behind" -eq 0 ]]; then
      echo "INFO: branch-attached submodule is ahead of upstream (ahead=$ahead)"
    elif [[ "$ahead" -eq 0 && "$behind" -gt 0 ]]; then
      echo "INFO: branch-attached submodule is behind upstream (behind=$behind)"
    else
      echo "INFO: branch-attached submodule has diverged (ahead=$ahead behind=$behind)"
    fi
  else
    echo "INFO: unable to compute branch-attached ahead/behind status"
  fi
  echo
done < <(collect_repos)

exit "$fail"
