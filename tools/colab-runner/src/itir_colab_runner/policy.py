from __future__ import annotations

from pathlib import Path
import re

from .model import ProverJob, ALLOWED_REPOSITORIES, ALLOWED_OPERATIONS

TARGET_RE = re.compile(r"^[A-Za-z0-9_.:/+-]+$")


def validate_job_policy(job: ProverJob) -> None:
    if job.repository not in ALLOWED_REPOSITORIES:
        raise ValueError("repository is not allowed")
    if job.operation not in ALLOWED_OPERATIONS:
        raise ValueError("operation is not allowed")
    if job.toolchain_policy != "repo_pinned":
        raise ValueError("toolchain policy must be repo_pinned")


def validate_relative_source_path(checkout: Path, relative_path: str, suffix: str) -> Path:
    p = Path(relative_path)
    if p.is_absolute() or ".." in p.parts or p.suffix != suffix:
        raise ValueError("invalid repository-relative source path")
    root = checkout.resolve()
    resolved = (checkout / p).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("source path escapes checkout") from exc
    if not resolved.exists() or not resolved.is_file():
        raise ValueError("source path does not exist as a file")
    return resolved


def _relative_arg(checkout: Path, path: Path) -> str:
    return path.relative_to(checkout.resolve()).as_posix()


def build_argv(job: ProverJob, checkout: Path) -> list[str]:
    validate_job_policy(job)
    args = job.arguments
    if job.operation == "lake_build":
        if set(args) != {"target"} or not isinstance(args.get("target"), str):
            raise ValueError("lake_build requires exactly one target")
        target = args["target"]
        if not TARGET_RE.fullmatch(target):
            raise ValueError("invalid Lake target")
        return ["lake", "build", target]
    if job.operation == "lake_env_lean":
        if set(args) != {"path"} or not isinstance(args.get("path"), str):
            raise ValueError("lake_env_lean requires exactly one path")
        path = validate_relative_source_path(checkout, args["path"], ".lean")
        return ["lake", "env", "lean", _relative_arg(checkout, path)]
    if job.operation == "agda_module":
        if set(args) != {"path", "profile"} or args.get("profile") != "repo" or not isinstance(args.get("path"), str):
            raise ValueError("agda_module requires path and profile=repo")
        path = validate_relative_source_path(checkout, args["path"], ".agda")
        return ["agda", _relative_arg(checkout, path)]
    raise ValueError("unsupported operation")
