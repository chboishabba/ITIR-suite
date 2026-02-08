#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

git_root() {
  git -c "safe.directory=$ROOT_DIR" -C "$ROOT_DIR" "$@"
}

if ! git_root rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not inside a git repository: $ROOT_DIR" >&2
  exit 1
fi

if [[ ! -f .gitmodules ]]; then
  echo "No .gitmodules file found; nothing to sync."
  exit 0
fi

print_help() {
  cat <<'EOF'
Usage: ./sync-all-submodules.sh [--commit-super] [--push-super]

Default behavior:
- Fast-forward pull each clean submodule worktree (no auto-commit/push).
- Skip dirty or detached submodules.

Optional:
--commit-super  Commit submodule pointer updates in the superproject, but ONLY
                if the superproject has no other changes besides submodule
                gitlinks and (optionally) .gitmodules.
--push-super    Push the superproject after committing (implies --commit-super).

Notes:
- This script does NOT auto-commit changes inside submodules (too risky).
- If you need to commit inside a submodule, do it explicitly in that submodule.
EOF
}

COMMIT_SUPER=0
PUSH_SUPER=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --commit-super) COMMIT_SUPER=1 ;;
    --push-super) COMMIT_SUPER=1; PUSH_SUPER=1 ;;
    -h|--help) print_help; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      echo >&2
      print_help >&2
      exit 2
      ;;
  esac
  shift
done

extract_host() {
  local url="$1"
  if [[ "$url" =~ ^https?://([^/:]+) ]]; then
    echo "${BASH_REMATCH[1]}"
    return 0
  fi
  if [[ "$url" =~ ^git@([^:]+): ]]; then
    echo "${BASH_REMATCH[1]}"
    return 0
  fi
  if [[ "$url" =~ ^ssh://([^/@]+@)?([^/:]+) ]]; then
    echo "${BASH_REMATCH[2]}"
    return 0
  fi
  return 1
}

is_dirty() {
  local path="$1"
  ! git_safe "$path" diff --quiet --ignore-submodules HEAD -- || ! git_safe "$path" diff --cached --quiet --ignore-submodules
}

git_safe() {
  local path="$1"
  shift
  local abs_path
  abs_path="$(cd "$path" && pwd)"
  git -c "safe.directory=$abs_path" -C "$path" "$@"
}

echo "Syncing configured submodules (ff-only pulls; no auto-commit/push by default)..."
echo

mapfile -t CONFIG_LINES < <(git_root config -f .gitmodules --get-regexp '^submodule\..*\.path$' || true)
if [[ "${#CONFIG_LINES[@]}" -eq 0 ]]; then
  echo "No submodule path entries in .gitmodules; nothing to do."
  exit 0
fi

declare -A MODULE_PATHS=()
for line in "${CONFIG_LINES[@]}"; do
  key="${line%% *}"
  path="${line#* }"
  name="${key#submodule.}"
  name="${name%.path}"
  MODULE_PATHS["$path"]="$name"
done

mapfile -t TRACKED_GITLINKS < <(git_root ls-files -s | awk '$1=="160000"{print $4}')
for tracked_path in "${TRACKED_GITLINKS[@]}"; do
  if [[ -n "${MODULE_PATHS[$tracked_path]+x}" ]]; then
    continue
  fi
  echo "WARN: gitlink '$tracked_path' is tracked but not present in .gitmodules (skipping)."
done

success_count=0
skip_count=0
fail_count=0

for path in "${!MODULE_PATHS[@]}"; do
  name="${MODULE_PATHS[$path]}"
  echo "==> $name ($path)"

  if [[ ! -e "$path/.git" ]]; then
    echo "SKIP: submodule not initialized at '$path'."
    ((skip_count += 1))
    echo
    continue
  fi

  if ! git_safe "$path" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "SKIP: '$path' is not a valid git worktree."
    ((skip_count += 1))
    echo
    continue
  fi

  if is_dirty "$path"; then
    echo "SKIP: dirty worktree in '$path' (commit/stash first)."
    ((skip_count += 1))
    echo
    continue
  fi

  branch="$(git_safe "$path" symbolic-ref --short -q HEAD || true)"
  if [[ -z "$branch" ]]; then
    echo "SKIP: detached HEAD in '$path'."
    ((skip_count += 1))
    echo
    continue
  fi

  remote_url="$(git_root config -f .gitmodules --get "submodule.$name.url" || true)"
  host=""
  if [[ -n "$remote_url" ]]; then
    host="$(extract_host "$remote_url" || true)"
  fi
  if [[ -n "$host" ]] && ! getent hosts "$host" >/dev/null 2>&1; then
    echo "SKIP: cannot resolve host '$host' for '$name' (offline/DNS issue)."
    ((skip_count += 1))
    echo
    continue
  fi

  if git_safe "$path" pull --ff-only --no-rebase; then
    echo "OK: '$name' is synced on branch '$branch'."
    ((success_count += 1))
  else
    echo "FAIL: git pull failed for '$name'."
    ((fail_count += 1))
  fi
  echo
done

echo "Summary: ok=$success_count skip=$skip_count fail=$fail_count"
if [[ "$fail_count" -gt 0 ]]; then
  exit 1
fi

commit_superproject_pointers() {
  # Only allow committing submodule gitlinks and (optionally) .gitmodules.
  # Refuse if any other paths are modified/untracked in the superproject.
  mapfile -t DIRTY_PATHS < <(git_root status --porcelain=v1 | awk '{print $2}')
  if [[ "${#DIRTY_PATHS[@]}" -eq 0 ]]; then
    echo "Superproject is clean; no pointer updates to commit."
    return 0
  fi

  allowed=()
  disallowed=()
  for p in "${DIRTY_PATHS[@]}"; do
    if [[ "$p" == ".gitmodules" ]]; then
      allowed+=("$p")
      continue
    fi
    if [[ -n "${MODULE_PATHS[$p]+x}" ]]; then
      allowed+=("$p")
      continue
    fi
    disallowed+=("$p")
  done

  if [[ "${#disallowed[@]}" -gt 0 ]]; then
    echo "REFUSE: superproject has non-submodule changes; won't auto-commit pointers."
    echo "Disallowed paths:"
    for p in "${disallowed[@]}"; do
      echo "  - $p"
    done
    echo
    echo "Commit/stash these changes first, then re-run with --commit-super/--push-super."
    return 2
  fi

  echo "Committing superproject submodule pointers:"
  for p in "${allowed[@]}"; do
    echo "  - $p"
  done

  git_root add -- "${allowed[@]}"
  if git_root diff --cached --quiet; then
    echo "Nothing staged; no commit created."
    return 0
  fi

  msg="chore: sync submodules ($(date -u +%Y-%m-%d))"
  git_root commit -m "$msg"

  if [[ "$PUSH_SUPER" -eq 1 ]]; then
    git_root push
  fi
}

if [[ "$COMMIT_SUPER" -eq 1 ]]; then
  echo
  commit_superproject_pointers
fi
exit 0
