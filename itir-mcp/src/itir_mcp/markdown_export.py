from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from re import DOTALL, escape, sub
from typing import Any, Mapping, Sequence


MARKDOWN_EXPORT_VERSION = "itir.markdown_export.v1"
DEFAULT_REFRESHED_AT = "unspecified"

DOCSTORE_STATUS_VERSION = "itir.docstore.status.v1"
OPEN_QUESTIONS_VERSION = "itir.docstore.open_questions.v1"
OBSIDIAN_SCAN_VERSION = "itir.obsidian.vault_scan.v1"


@dataclass(frozen=True)
class MarkdownProjection:
    """Generated Markdown page plus metadata needed for deterministic refresh."""

    block_id: str
    relative_path: Path
    payload_version: str
    title: str
    block_text: str
    page_text: str


def render_markdown_projection(
    response: Mapping[str, Any],
    *,
    refreshed_at: str = DEFAULT_REFRESHED_AT,
    source_label: str = "MCP response",
    max_items: int = 50,
) -> MarkdownProjection:
    """Render a raw or MCP-wrapped response into a replaceable Markdown projection."""

    payload, wrapper_meta = _unwrap_response(response)
    version = str(payload.get("version") or "unknown")
    block_id = _block_id(version)
    title = _title_for_version(version)
    relative_path = _relative_path_for_version(version)
    body_lines = _front_matter_lines(version, refreshed_at, source_label, wrapper_meta)
    body_lines.extend(_body_lines(payload, version, max_items=max_items))
    body = "\n".join(body_lines).rstrip() + "\n"
    block_text = "\n".join([_begin_marker(block_id), body.rstrip(), _end_marker(block_id), ""])
    page_text = f"# {title}\n\n{block_text}"
    return MarkdownProjection(
        block_id=block_id,
        relative_path=relative_path,
        payload_version=version,
        title=title,
        block_text=block_text,
        page_text=page_text,
    )


def write_markdown_projection(
    response: Mapping[str, Any],
    *,
    output_root: str | Path,
    refreshed_at: str = DEFAULT_REFRESHED_AT,
    source_label: str = "MCP response",
    max_items: int = 50,
) -> Path:
    """Write a generated page under an explicit root and replace only its generated block."""

    root = _explicit_root(output_root)
    projection = render_markdown_projection(
        response,
        refreshed_at=refreshed_at,
        source_label=source_label,
        max_items=max_items,
    )
    target = (root / projection.relative_path).resolve()
    _assert_inside(target, root.resolve())
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        existing = target.read_text(encoding="utf-8", errors="replace")
        text = replace_generated_block(existing, projection)
    else:
        text = projection.page_text
    target.write_text(text, encoding="utf-8")
    return target


def replace_generated_block(existing_text: str, projection: MarkdownProjection) -> str:
    """Replace the projection block in existing Markdown or create a generated page."""

    begin = _begin_marker(projection.block_id)
    end = _end_marker(projection.block_id)
    pattern = rf"{escape(begin)}\n.*?{escape(end)}\n?"
    if begin in existing_text and end in existing_text:
        return sub(pattern, projection.block_text, existing_text, count=1, flags=DOTALL)
    if not existing_text.strip():
        return projection.page_text
    raise ValueError(f"refusing to overwrite Markdown without generated markers: {projection.relative_path}")


def stable_projection_path(response: Mapping[str, Any]) -> Path:
    """Return the deterministic generated path for a raw or wrapped MCP response."""

    payload, _wrapper_meta = _unwrap_response(response)
    return _relative_path_for_version(str(payload.get("version") or "unknown"))


def _unwrap_response(response: Mapping[str, Any]) -> tuple[Mapping[str, Any], dict[str, str]]:
    wrapper_meta: dict[str, str] = {}
    current: Mapping[str, Any] = response
    if current.get("ok") is True and isinstance(current.get("result"), Mapping):
        wrapper_meta["mcp_ok"] = "true"
        current = current["result"]  # type: ignore[index]
    if isinstance(current.get("decision"), str) and isinstance(current.get("result"), Mapping):
        wrapper_meta["guard_decision"] = str(current.get("decision"))
        current = current["result"]  # type: ignore[index]
    return current, wrapper_meta


def _front_matter_lines(
    version: str,
    refreshed_at: str,
    source_label: str,
    wrapper_meta: Mapping[str, str],
) -> list[str]:
    lines = [
        "> Warning: This is generated observer/projector output. It is not an authority record, source note, or mutation request.",
        "",
        "- Projection version: `" + MARKDOWN_EXPORT_VERSION + "`",
        "- Payload version: `" + _inline_code(version) + "`",
        "- Refreshed at: `" + _inline_code(refreshed_at or DEFAULT_REFRESHED_AT) + "`",
        "- Source: `" + _inline_code(source_label) + "`",
        "- Refresh policy: replace only the matching `ITIR-GENERATED` block.",
    ]
    for key in sorted(wrapper_meta):
        lines.append(f"- {key.replace('_', ' ').title()}: `{_inline_code(wrapper_meta[key])}`")
    lines.append("")
    return lines


def _body_lines(payload: Mapping[str, Any], version: str, *, max_items: int) -> list[str]:
    if version == DOCSTORE_STATUS_VERSION:
        return _status_lines(payload, max_items=max_items)
    if version == OPEN_QUESTIONS_VERSION:
        return _open_question_lines(payload, max_items=max_items)
    if version == OBSIDIAN_SCAN_VERSION:
        return _obsidian_lines(payload, max_items=max_items)
    return _unknown_payload_lines(payload)


def _status_lines(payload: Mapping[str, Any], *, max_items: int) -> list[str]:
    lines = ["## Docstore Status", ""]
    lines.extend(
        _kv_lines(
            (
                ("Artifact count", payload.get("artifact_count")),
                ("State count", payload.get("state_count")),
            )
        )
    )
    lines.append("")
    lines.extend(_counts_section("Producer Counts", payload.get("producer_counts")))
    lines.extend(_counts_section("Role Counts", payload.get("role_counts")))
    lines.extend(_counts_section("Authority Counts", payload.get("authority_counts")))
    lines.extend(_counts_section("Unresolved Pressure Counts", payload.get("unresolved_pressure_counts")))
    lines.extend(_nested_counts_section("Open Question Counts", payload.get("open_question_counts")))

    latest = _sequence_of_mappings(payload.get("latest_artifacts"))[:max_items]
    if latest:
        lines.extend(
            [
                "## Latest Artifacts",
                "",
                _table(
                    ("Artifact ID", "Role", "Source", "Status"),
                    [
                        (
                            item.get("artifact_id"),
                            item.get("artifact_role"),
                            item.get("source_system"),
                            item.get("unresolved_pressure_status"),
                        )
                        for item in latest
                    ],
                ),
                "",
            ]
        )
    lines.extend(_sources_lines(payload.get("sources"), max_items=max_items))
    return lines


def _open_question_lines(payload: Mapping[str, Any], *, max_items: int) -> list[str]:
    questions = _sequence_of_mappings(payload.get("questions"))
    lines = ["## Open Questions", ""]
    lines.extend(
        _kv_lines(
            (
                ("Total emitted", len(questions)),
                ("Truncated upstream", payload.get("truncated")),
            )
        )
    )
    lines.append("")
    lines.extend(_nested_counts_section("Question Counts", payload.get("counts")))
    if questions:
        rows = []
        for item in questions[:max_items]:
            rows.append(
                (
                    item.get("source_system"),
                    item.get("pressure_kind"),
                    item.get("status"),
                    item.get("promotion_level"),
                    item.get("question_text_or_reason"),
                    item.get("next_action"),
                    _provenance_summary(item.get("provenance_refs")),
                )
            )
        lines.extend(
            [
                "## Questions",
                "",
                _table(("Source", "Kind", "Status", "Promotion", "Question/Reason", "Next Action", "Provenance"), rows),
                "",
            ]
        )
        if len(questions) > max_items:
            lines.extend([f"_Showing {max_items} of {len(questions)} questions._", ""])
    lines.extend(_sources_lines(payload.get("sources"), max_items=max_items))
    return lines


def _obsidian_lines(payload: Mapping[str, Any], *, max_items: int) -> list[str]:
    notes = _sequence_of_mappings(payload.get("notes"))
    candidates = _sequence_of_mappings(payload.get("candidates"))
    lines = ["## Obsidian Vault Scan", ""]
    lines.extend(
        _kv_lines(
            (
                ("Authority class", payload.get("authority_class")),
                ("Notes scanned", len(notes)),
                ("Candidate hints", len(candidates)),
            )
        )
    )
    lines.append("")
    lines.extend(_nested_counts_section("Candidate Counts", payload.get("counts")))
    if candidates:
        rows = []
        for item in candidates[:max_items]:
            rows.append(
                (
                    item.get("source_system"),
                    item.get("pressure_kind"),
                    item.get("status"),
                    item.get("promotion_level"),
                    item.get("question_text_or_reason"),
                    item.get("next_action"),
                    _provenance_summary(item.get("provenance_refs")),
                )
            )
        lines.extend(
            [
                "## Candidate Hints",
                "",
                _table(("Source", "Kind", "Status", "Promotion", "Question/Reason", "Next Action", "Provenance"), rows),
                "",
            ]
        )
    if notes:
        rows = []
        for item in notes[:max_items]:
            rows.append(
                (
                    item.get("note_id_hash"),
                    item.get("vault_id_hash"),
                    item.get("event"),
                    item.get("authority_class"),
                )
            )
        lines.extend(
            [
                "## Notes",
                "",
                _table(("Note ID Hash", "Vault ID Hash", "Event", "Authority"), rows),
                "",
            ]
        )
    lines.extend(_sources_lines(payload.get("sources"), max_items=max_items))
    return lines


def _unknown_payload_lines(payload: Mapping[str, Any]) -> list[str]:
    lines = ["## Payload Summary", ""]
    for key in sorted(payload):
        value = payload[key]
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f"- {key}: `{_inline_code(value)}`")
    lines.append("")
    return lines


def _counts_section(title: str, value: Any) -> list[str]:
    if not isinstance(value, Mapping) or not value:
        return []
    lines = [f"## {title}", ""]
    for key in sorted(value, key=str):
        lines.append(f"- `{_inline_code(key)}`: {value[key]}")
    lines.append("")
    return lines


def _nested_counts_section(title: str, value: Any) -> list[str]:
    if not isinstance(value, Mapping) or not value:
        return []
    lines = [f"## {title}", ""]
    for key in sorted(value, key=str):
        nested = value[key]
        if isinstance(nested, Mapping):
            lines.append(f"### {key.replace('_', ' ').title()}")
            lines.append("")
            for nested_key in sorted(nested, key=str):
                lines.append(f"- `{_inline_code(nested_key)}`: {nested[nested_key]}")
            lines.append("")
        else:
            lines.append(f"- {key}: `{_inline_code(nested)}`")
    if lines[-1] != "":
        lines.append("")
    return lines


def _sources_lines(value: Any, *, max_items: int) -> list[str]:
    sources = _sequence_of_mappings(value)[:max_items]
    if not sources:
        return []
    rows = []
    for source in sources:
        rows.append(
            (
                source.get("kind"),
                source.get("count", source.get("record_count", source.get("obligation_count", ""))),
                source.get("path", source.get("vault_id_hash", "")),
            )
        )
    return ["## Provenance Sources", "", _table(("Kind", "Count", "Reference"), rows), ""]


def _kv_lines(items: Sequence[tuple[str, Any]]) -> list[str]:
    return [f"- {label}: `{_inline_code(value)}`" for label, value in items if value is not None]


def _provenance_summary(value: Any) -> str:
    refs = _sequence_of_mappings(value)
    if not refs:
        return ""
    parts: list[str] = []
    for ref in refs[:3]:
        label_parts = []
        for key in ("kind", "artifact_id", "note_id_hash", "vault_id_hash", "line_no", "path"):
            if ref.get(key):
                label_parts.append(f"{key}={ref[key]}")
        if label_parts:
            parts.append(", ".join(label_parts))
    return "; ".join(parts)


def _table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    header = "| " + " | ".join(_table_cell(item) for item in headers) + " |"
    divider = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(_table_cell(item) for item in row) + " |" for row in rows]
    return "\n".join([header, divider, *body])


def _table_cell(value: Any) -> str:
    text = _plain_text(value)
    text = text.replace("|", "\\|").replace("\n", " ")
    return _truncate(text, 240)


def _inline_code(value: Any) -> str:
    return _truncate(_plain_text(value).replace("`", "'"), 240)


def _plain_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return " ".join(str(value).split())


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _sequence_of_mappings(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (bytes, bytearray, str)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _relative_path_for_version(version: str) -> Path:
    if version == DOCSTORE_STATUS_VERSION:
        return Path("_ITIR") / "generated" / "docstore" / "status.md"
    if version == OPEN_QUESTIONS_VERSION:
        return Path("_ITIR") / "generated" / "docstore" / "open-questions.md"
    if version == OBSIDIAN_SCAN_VERSION:
        return Path("_ITIR") / "generated" / "obsidian" / "vault-scan.md"
    return Path("_ITIR") / "generated" / "mcp" / f"{_slug(version or 'unknown')}.md"


def _title_for_version(version: str) -> str:
    if version == DOCSTORE_STATUS_VERSION:
        return "ITIR Docstore Status"
    if version == OPEN_QUESTIONS_VERSION:
        return "ITIR Open Questions"
    if version == OBSIDIAN_SCAN_VERSION:
        return "ITIR Obsidian Vault Scan"
    return "ITIR MCP Projection"


def _block_id(version: str) -> str:
    return "itir:" + _slug(version or "unknown")


def _slug(value: str) -> str:
    chars = [char.lower() if char.isalnum() else "-" for char in value]
    slug = "-".join("".join(chars).split("-"))
    return slug.strip("-") or "unknown"


def _begin_marker(block_id: str) -> str:
    return f"<!-- ITIR-GENERATED:BEGIN {block_id} -->"


def _end_marker(block_id: str) -> str:
    return f"<!-- ITIR-GENERATED:END {block_id} -->"


def _explicit_root(output_root: str | Path) -> Path:
    root_text = str(output_root).strip()
    if not root_text:
        raise ValueError("output_root is required")
    root = Path(output_root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    if not root.is_dir():
        raise ValueError(f"output_root is not a directory: {output_root}")
    return root


def _assert_inside(path: Path, root: Path) -> None:
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"target path escapes output_root: {path}") from exc
