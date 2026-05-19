from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import export_chat_archive_thread as exporter
import benchmark_chat_archive_export_chunks as benchmark


def _make_archive(path: Path) -> None:
    con = sqlite3.connect(path)
    con.executescript(
        """
        CREATE TABLE messages (
          message_id TEXT PRIMARY KEY,
          canonical_thread_id TEXT NOT NULL,
          platform TEXT NOT NULL,
          account_id TEXT NOT NULL,
          ts TEXT NOT NULL,
          role TEXT NOT NULL,
          text TEXT NOT NULL,
          title TEXT,
          source_id TEXT NOT NULL,
          source_thread_id TEXT,
          source_message_id TEXT,
          source_path TEXT,
          source_bucket TEXT,
          provenance_json TEXT
        );
        CREATE TABLE message_blocks (
          message_id TEXT NOT NULL,
          block_index INTEGER NOT NULL,
          block_type TEXT NOT NULL,
          text_value TEXT,
          ref_path TEXT,
          actor TEXT,
          emoji TEXT,
          target TEXT,
          metadata_json TEXT,
          PRIMARY KEY (message_id, block_index)
        );
        """
    )
    rows = [
        (
            "m1",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "perplexity",
            "acct",
            "2026-05-15T10:00:00+00:00",
            "user",
            "Can you export this correctly?",
            "Export Broken Thread",
            "src",
            "11111111-1111-1111-1111-111111111111",
            "sm1",
            "/tmp/source.json",
            "bucket",
            '{"capture":"db"}',
        ),
        (
            "m2",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "perplexity",
            "acct",
            "2026-05-15T10:01:00+00:00",
            "assistant",
            "Yes. Use the canonical DB.",
            "Export Broken Thread",
            "src",
            "11111111-1111-1111-1111-111111111111",
            "sm2",
            "/tmp/source.json",
            "bucket",
            None,
        ),
        (
            "m3",
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "chatgpt",
            "acct",
            "2026-05-14T10:01:00+00:00",
            "user",
            "Different thread",
            "Export Broken Thread",
            "src",
            "22222222-2222-2222-2222-222222222222",
            "sm3",
            None,
            None,
            None,
        ),
    ]
    con.executemany(
        """
        INSERT INTO messages (
          message_id, canonical_thread_id, platform, account_id, ts, role, text,
          title, source_id, source_thread_id, source_message_id, source_path,
          source_bucket, provenance_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    con.execute(
        """
        INSERT INTO message_blocks (
          message_id, block_index, block_type, text_value, metadata_json
        ) VALUES (?, ?, ?, ?, ?)
        """,
        ("m2", 0, "text", "Yes. Use the canonical DB.", '{"kind":"answer"}'),
    )
    con.commit()
    con.close()


def test_exports_markdown_json_bundle_from_source_thread_id(tmp_path: Path) -> None:
    db = tmp_path / "chat_archive.sqlite"
    _make_archive(db)
    out_dir = tmp_path / "bundle"

    rc = exporter.main(
        [
            "--db",
            str(db),
            "--source-thread-id",
            "11111111-1111-1111-1111-111111111111",
            "--include-blocks",
            "--out",
            str(out_dir),
            "--bundle",
            "--format",
            "all",
            "--json",
        ]
    )

    assert rc == 0
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "itir.chat_archive.thread_export_manifest.v1"
    assert manifest["thread"]["canonical_thread_id"] == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    paths = {item["path"] for item in manifest["files"]}
    assert "export-broken-thread.md" in paths
    assert "export-broken-thread.json" in paths
    assert "export-broken-thread.html" in paths

    markdown = (out_dir / "export-broken-thread.md").read_text(encoding="utf-8")
    assert "# Can you export this correctly?" in markdown
    assert "source_message_id=sm2" in markdown
    assert "Yes. Use the canonical DB." in markdown

    payload = json.loads((out_dir / "export-broken-thread.json").read_text(encoding="utf-8"))
    assert payload["schema"] == "itir.chat_archive.thread_export.v1"
    assert len(payload["messages"]) == 2
    assert payload["messages"][1]["blocks"][0]["metadata"] == {"kind": "answer"}

    rendered = (out_dir / "export-broken-thread.html").read_text(encoding="utf-8")
    assert "<!doctype html>" in rendered
    assert "Use the canonical DB." in rendered


def test_transcript_markdown_style_keeps_explicit_roles(tmp_path: Path) -> None:
    db = tmp_path / "chat_archive.sqlite"
    _make_archive(db)
    out_dir = tmp_path / "transcript"

    rc = exporter.main(
        [
            "--db",
            str(db),
            "--source-thread-id",
            "11111111-1111-1111-1111-111111111111",
            "--out",
            str(out_dir),
            "--bundle",
            "--format",
            "markdown",
            "--markdown-style",
            "transcript",
        ]
    )

    assert rc == 0
    markdown = (out_dir / "export-broken-thread.md").read_text(encoding="utf-8")
    assert "# Export Broken Thread" in markdown
    assert "## 1. User" in markdown
    assert "## 2. Assistant" in markdown


def test_ambiguous_title_requires_pick_first_or_stricter_selector(tmp_path: Path) -> None:
    db = tmp_path / "chat_archive.sqlite"
    _make_archive(db)

    try:
        exporter.main(
            [
                "--db",
                str(db),
                "--title",
                "Export Broken",
                "--out",
                str(tmp_path / "out"),
            ]
        )
    except SystemExit as exc:
        assert "selector matched multiple threads" in str(exc)
    else:
        raise AssertionError("expected ambiguous title selector to fail")


def test_platform_filter_disambiguates_title(tmp_path: Path) -> None:
    db = tmp_path / "chat_archive.sqlite"
    _make_archive(db)
    out_dir = tmp_path / "perplexity-export"

    rc = exporter.main(
        [
            "--db",
            str(db),
            "--title",
            "Export Broken",
            "--platform",
            "perplexity",
            "--format",
            "json",
            "--out",
            str(out_dir),
            "--bundle",
        ]
    )

    assert rc == 0
    payload = json.loads((out_dir / "export-broken-thread.json").read_text(encoding="utf-8"))
    assert payload["thread"]["platform"] == "perplexity"
    assert payload["thread"]["message_count"] == 2


def test_perplexity_duplicate_prefix_blocks_are_cleaned_by_default() -> None:
    text = "\n\n".join(
        [
            "Intro",
            "A",
            "B",
            "C",
            "D",
            "E",
            "Intro",
            "A",
            "B",
            "C",
            "D",
            "E",
            "tail",
        ]
    )

    cleaned = exporter._collapse_repeated_prefix_blocks(text)

    assert cleaned == "Intro\n\nA\n\nB\n\nC\n\nD\n\nE\n"


def test_split_prompt_heading_preserves_links_and_moves_remainder_to_body() -> None:
    heading, remainder = exporter._split_prompt_heading(
        "The [Quran](https://www.google.com/search?q=quran&kgmid=/m/096tx#sv=long-token) has no direct inverse. Explain the rest.",
        "fallback",
    )

    assert heading == "The [Quran](https://www.google.com/search?q=quran&kgmid=/m/096tx#sv=long-token) has no direct inverse."
    assert remainder == "Explain the rest."


def test_document_html_compacts_visible_links_without_changing_targets(tmp_path: Path) -> None:
    db = tmp_path / "chat_archive.sqlite"
    _make_archive(db)
    out_dir = tmp_path / "bundle"
    long_url = "https://example.test/search?" + ("q=" + "x" * 120)
    con = sqlite3.connect(db)
    con.execute(
        "UPDATE messages SET text=? WHERE message_id='m2'",
        (f"See {long_url} and $x + 1$.",),
    )
    con.commit()
    con.close()

    rc = exporter.main(
        [
            "--db",
            str(db),
            "--source-thread-id",
            "11111111-1111-1111-1111-111111111111",
            "--out",
            str(out_dir),
            "--bundle",
            "--format",
            "html",
        ]
    )

    assert rc == 0
    rendered = (out_dir / "export-broken-thread.html").read_text(encoding="utf-8")
    assert f'href="{long_url}"' in rendered
    assert "example.test/.../search?..." in rendered
    assert f">{long_url}<" not in rendered


def test_markdown_diagnostics_catches_unbalanced_math_and_links() -> None:
    diagnostics = exporter._diagnose_markdown("Text with $broken math\n[bad](https://example.test/foo")

    kinds = {item["kind"] for item in diagnostics}
    assert "math_delimiter_balance" in kinds
    assert "possibly_truncated_markdown_link" in kinds


def test_fragmented_listing_repair_is_conservative_and_audited() -> None:
    source = """Before

❯
ls

d
r
w
x
r
-
x
r
-
x
-
c
1 Mar 14:49

.agda

d
r
w
x
r
-
x
r
-
x
-
c
1 May 20:24

.agents

d
r
w
x
r
-
x
r
-
x
-
c
14 Mar 02:02

.cache

d
r
w
x
r
-
x
r
-
x
-
c
30 Apr 23:50
artifacts

d
r
w
x
r
-
x
r
-
x
-
c
1 May 00:37

Ontology

 result

d
r
w
x
r
-
x
r
-
x
-
c
19 Feb 23:07
Verification

󰊢 .gitignore
.
r
w
-
r
--
r
--
94
c
1 Apr 23:00

d
r
w
x
r
-
x
r
-
x
-
c
27 Mar 22:40
__pycache__

d
r
w
x
r
-
x
r
-
x
-
c
24 Mar 21:57
_build

c

23 Apr 15:13
 all_code64.txt
.
r
w
-
r
--
r
--
3.3M

c

16 Feb 19:59
 AntiFascistSystem.agda
.
r
w
-
r
--
r
--
42k

c

12 Mar 16:59
 Book.pdf
.
r
w
-
r
--
r
--
218k

After

```text
intentional

vertical

spacing
```
"""

    repaired, diagnostics = exporter._repair_fragmented_listing_markdown(source, policy="conservative")

    assert "❯\nls\n```text\n1 Mar 14:49  c   .agda  drwxr-xr-x-" in repaired
    assert "1 May 20:24  c   .agents  drwxr-xr-x-" in repaired
    assert "14 Mar 02:02  c   .cache  drwxr-xr-x-" in repaired
    assert "30 Apr 23:50  c  artifacts  drwxr-xr-x-" in repaired
    assert "1 May 00:37  c   Ontology  drwxr-xr-x-" in repaired
    assert " result" in repaired
    assert "```\n result\n```text" not in repaired
    assert "19 Feb 23:07  c  Verification  drwxr-xr-x-" in repaired
    assert "1 Apr 23:00  c  󰊢 .gitignore  .rw-r--r--  94" in repaired
    assert "27 Mar 22:40  c  __pycache__  drwxr-xr-x-" in repaired
    assert "24 Mar 21:57  c  _build  drwxr-xr-x-" in repaired
    assert "23 Apr 15:13  c   all_code64.txt  .rw-r--r--  3.3M" in repaired
    assert "16 Feb 19:59  c   AntiFascistSystem.agda  .rw-r--r--  42k" in repaired
    assert "12 Mar 16:59  c   Book.pdf  .rw-r--r--  218k" in repaired
    assert "intentional\n\nvertical\n\nspacing" in repaired
    assert diagnostics[0]["kind"] == "fragmented_listing_repair"
    assert diagnostics[0]["rows_repaired"] == 13


def test_fragmented_listing_repair_ignores_low_evidence_whitespace() -> None:
    source = """A poem

with

deliberate

spacing
"""

    repaired, diagnostics = exporter._repair_fragmented_listing_markdown(source, policy="conservative")

    assert repaired == source
    assert diagnostics == []


def test_codex_transcript_repair_fences_tool_blocks_and_collapses_labels() -> None:
    source = """•
Ran

python
scripts/musical_symmetry_mdl.py
--
length
4
└ {
"alpha": 0.5,
}

────────────────────────────────

-
O
: Docs/governance update.

1.

Origin receipt
: Minimal closure receipt.

-

Docs/MusicalSymmetryMDL.md:1
: the core note.

-
monster/
has a separate music/song cluster.
"""

    repaired, diagnostics = exporter._repair_codex_transcript_markdown(source)

    assert "```text\n• Ran\npython scripts/musical_symmetry_mdl.py --length 4\n└ {\n\"alpha\": 0.5,\n}\n```" in repaired
    assert "- O: Docs/governance update." in repaired
    assert "1. **Origin receipt**: Minimal closure receipt." in repaired
    assert "- Docs/MusicalSymmetryMDL.md:1: the core note." in repaired
    assert "- monster/" in repaired
    assert diagnostics[0]["kind"] == "codex_transcript_repair"


def test_static_math_prerender_uses_katex_when_available() -> None:
    katex = exporter._find_katex_dist()
    rendered, ok = exporter._prerender_math_static("Value $x + 1$.", katex, timeout_seconds=5)

    if katex is None:
        assert not ok
        assert rendered == "Value $x + 1$."
    else:
        assert ok
        assert 'class="katex"' in rendered
        assert "$x + 1$" not in rendered


def test_transcript_html_mode_renders_messages(tmp_path: Path) -> None:
    db = tmp_path / "chat_archive.sqlite"
    _make_archive(db)
    out_dir = tmp_path / "html-transcript"

    rc = exporter.main(
        [
            "--db",
            str(db),
            "--source-thread-id",
            "11111111-1111-1111-1111-111111111111",
            "--out",
            str(out_dir),
            "--bundle",
            "--format",
            "html",
            "--html-style",
            "transcript",
        ]
    )

    assert rc == 0
    rendered = (out_dir / "export-broken-thread.html").read_text(encoding="utf-8")
    assert "1. User" in rendered
    assert "2. Assistant" in rendered
    assert "Use the canonical DB." in rendered


def test_chunk_plan_respects_message_and_byte_limits() -> None:
    messages = [
        {"index": 1, "text": "a" * 100},
        {"index": 2, "text": "b" * 100},
        {"index": 3, "text": "c" * 2000},
        {"index": 4, "text": "d" * 100},
    ]

    plan = exporter.plan_message_chunks(messages, max_messages=2, target_bytes=1500)

    assert [item["message_count"] for item in plan] == [2, 1, 1]
    assert plan[0]["start_message_index"] == 1
    assert plan[-1]["end_message_index"] == 4


def test_chunked_html_export_writes_parts_and_manifest_plan(tmp_path: Path) -> None:
    db = tmp_path / "chat_archive.sqlite"
    _make_archive(db)
    con = sqlite3.connect(db)
    con.execute(
        """
        INSERT INTO messages (
          message_id, canonical_thread_id, platform, account_id, ts, role, text,
          title, source_id, source_thread_id, source_message_id, source_path,
          source_bucket, provenance_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "m4",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "perplexity",
            "acct",
            "2026-05-15T10:02:00+00:00",
            "assistant",
            "Third message.",
            "Export Broken Thread",
            "src",
            "11111111-1111-1111-1111-111111111111",
            "sm4",
            "/tmp/source.json",
            "bucket",
            None,
        ),
    )
    con.commit()
    con.close()
    out_dir = tmp_path / "chunked"

    rc = exporter.main(
        [
            "--db",
            str(db),
            "--source-thread-id",
            "11111111-1111-1111-1111-111111111111",
            "--out",
            str(out_dir),
            "--bundle",
            "--format",
            "html",
            "--chunk-messages",
            "1",
        ]
    )

    assert rc == 0
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["chunk_plan"]) == 3
    paths = {item["path"] for item in manifest["files"]}
    assert "export-broken-thread.part-001.html" in paths
    assert "export-broken-thread.part-003.html" in paths


def test_benchmark_config_parser_and_bundle_summary(tmp_path: Path) -> None:
    assert benchmark._parse_config("80:1200000:2") == (80, 1_200_000, 2)

    out_dir = tmp_path / "bundle"
    out_dir.mkdir()
    (out_dir / "thread.part-001.html").write_text("<html></html>", encoding="utf-8")
    (out_dir / "thread.part-001.pdf").write_bytes(b"pdf")
    (out_dir / "manifest.json").write_text(
        json.dumps(
            {
                "thread": {"title": "Thread"},
                "files": [{"path": "thread.part-001.html"}, {"path": "thread.part-001.pdf"}],
                "chunk_plan": [{"chunk_index": 1, "estimated_bytes": 123, "message_count": 1}],
            }
        ),
        encoding="utf-8",
    )

    summary = benchmark._summarize_bundle(out_dir, elapsed_seconds=1.25, returncode=0)

    assert summary["ok"] is True
    assert summary["chunk_count"] == 1
    assert summary["pdf_count"] == 1
    assert summary["pdf_total_bytes"] == 3
