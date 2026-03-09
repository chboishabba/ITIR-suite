#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHAT_ARCHIVE = Path(os.path.expanduser('~/chat_archive.sqlite'))
WIKI_REVISION_DB = ROOT / 'SensibLaw' / '.cache_local' / 'wiki_revision_harness.sqlite'
WIKI_QUERY_SCRIPT = ROOT / 'SensibLaw' / 'scripts' / 'query_wiki_revision_monitor.py'
FRIENDLYJORDIES_SOURCE_THREAD_ID = '69ac40e0-0cfc-839b-b2a8-0de3019379a9'
WIKI_MONITOR_ERROR_RUN = 'run:wiki_revision_monitor_v1:2026-03-08T16:32:32+00:00:1af5177b'
WIKI_MONITOR_ERROR_ARTICLE = 'stress_high_german'
WIKI_CONTESTED_RUN = 'run:wiki_revision_contested_v1:2026-03-09T07:46:59+00:00:05900d8c'
WIKI_CONTESTED_ARTICLE = 'contest_donald_trump'


@dataclass
class RouteResult:
    key: str
    path: str
    marker: str
    status: int | None
    marker_found: bool
    body_bytes: int
    classification: str
    note: str
    error: str | None = None


@dataclass
class ProbeResult:
    key: str
    classification: str
    note: str
    details: dict[str, Any]


def http_get(url: str, timeout: float = 15.0) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={'User-Agent': 'itir-recent-page-audit/0.1'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode('utf-8', 'replace')
        return int(resp.status), body


def probe_route(base_url: str, key: str, path: str, marker: str) -> RouteResult:
    url = base_url.rstrip('/') + path
    try:
        status, body = http_get(url)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode('utf-8', 'replace')
        return RouteResult(
            key=key,
            path=path,
            marker=marker,
            status=int(exc.code),
            marker_found=marker.lower() in body.lower(),
            body_bytes=len(body.encode('utf-8', 'replace')),
            classification='route/load failure',
            note=f'HTTP {exc.code}',
            error=str(exc),
        )
    except Exception as exc:  # noqa: BLE001
        return RouteResult(
            key=key,
            path=path,
            marker=marker,
            status=None,
            marker_found=False,
            body_bytes=0,
            classification='route/load failure',
            note='request failed',
            error=repr(exc),
        )

    marker_found = marker.lower() in body.lower()
    classification = 'pass' if marker_found else 'UI shell mismatch'
    note = 'marker found' if marker_found else f'missing expected marker: {marker}'

    if (
        key in {'wiki_revision_contested_monitor_error_run', 'wiki_revision_contested_contested_run'}
        and 'No contested graph available for the selected article/run.'.lower() in body.lower()
    ):
        classification = 'UI rendered but no meaningful payload'
        note = 'selected run renders shell, but selected article has no contested graph payload'
    elif key == 'mission_lens' and 'No report'.lower() in body.lower():
        classification = 'loader returned empty/error'
        note = 'mission lens page shell loaded with no report body'

    return RouteResult(
        key=key,
        path=path,
        marker=marker,
        status=status,
        marker_found=marker_found,
        body_bytes=len(body.encode('utf-8', 'replace')),
        classification=classification,
        note=note,
        error=None,
    )


def latest_thread_id() -> str:
    if not CHAT_ARCHIVE.exists():
        return 'missing-chat-archive'
    con = sqlite3.connect(f'file:{CHAT_ARCHIVE}?mode=ro&immutable=1', uri=True)
    try:
        row = con.execute(
            'select canonical_thread_id from messages group by canonical_thread_id order by max(ts) desc limit 1'
        ).fetchone()
        return str(row[0]) if row else 'missing-chat-thread'
    finally:
        con.close()


def run_json_command(args: list[str]) -> dict[str, Any]:
    out = subprocess.check_output(args, cwd=ROOT, text=True)
    return json.loads(out)


def probe_chat_archive() -> ProbeResult:
    if not CHAT_ARCHIVE.exists():
        return ProbeResult('chat_archive', 'backing DB/artifact missing', 'canonical chat archive not found', {'path': str(CHAT_ARCHIVE)})
    con = sqlite3.connect(f'file:{CHAT_ARCHIVE}?mode=ro&immutable=1', uri=True)
    try:
        msg_count = int(con.execute('select count(*) from messages').fetchone()[0])
        thread_count = int(con.execute('select count(distinct canonical_thread_id) from messages').fetchone()[0])
    finally:
        con.close()
    return ProbeResult(
        'chat_archive',
        'pass',
        'canonical chat archive present',
        {'path': str(CHAT_ARCHIVE), 'message_count': msg_count, 'thread_count': thread_count},
    )


def probe_wiki_revision_db() -> ProbeResult:
    if not WIKI_REVISION_DB.exists():
        return ProbeResult('wiki_revision_db', 'backing DB/artifact missing', 'wiki revision harness DB not found', {'path': str(WIKI_REVISION_DB)})
    con = sqlite3.connect(str(WIKI_REVISION_DB))
    try:
        tables = sorted(
            row[0] for row in con.execute("select name from sqlite_master where type='table' and name like 'wiki_revision_monitor%'")
        )
        run_count = int(con.execute('select count(*) from wiki_revision_monitor_runs').fetchone()[0])
    finally:
        con.close()
    contested_tables = [t for t in tables if 'contested_' in t]
    classification = 'pass' if contested_tables else 'backing DB/artifact missing'
    note = 'wiki revision monitor tables present' if contested_tables else 'contested graph tables missing from harness DB'
    return ProbeResult(
        'wiki_revision_db',
        classification,
        note,
        {'path': str(WIKI_REVISION_DB), 'run_count': run_count, 'tables': tables, 'contested_tables': contested_tables},
    )


def probe_wiki_revision_run(pack_id: str, run_id: str, article_id: str, key: str) -> ProbeResult:
    payload = run_json_command([
        sys.executable,
        str(WIKI_QUERY_SCRIPT),
        '--db-path',
        str(WIKI_REVISION_DB),
        '--pack-id',
        pack_id,
        '--run-id',
        run_id,
        '--article-id',
        article_id,
    ])
    summary = payload.get('summary') or {}
    counts = summary.get('counts') or {}
    articles = summary.get('articles') or []
    selected = next((row for row in articles if row.get('article_id') == article_id), None)
    selected_graph = payload.get('selected_graph')
    has_graph_counts = 'contested_graph_counts' in summary and summary.get('contested_graph_counts') is not None
    if selected and selected.get('status') == 'error':
        classification = 'producer emitted stale/partial run'
        note = f"selected article is error-only ({selected.get('title') or article_id})"
    elif selected_graph is None:
        classification = 'loader returned empty/error'
        note = 'selected_graph is null for the selected run/article'
    elif not has_graph_counts:
        classification = 'schema mismatch / contract drift'
        note = 'run summary omits contested_graph_counts despite contested graph lane'
    else:
        classification = 'pass'
        note = 'run summary and selected graph are populated'
    return ProbeResult(
        key,
        classification,
        note,
        {
            'pack_id': pack_id,
            'run_id': run_id,
            'article_id': article_id,
            'counts': counts,
            'highest_severity': summary.get('highest_severity'),
            'has_contested_graph_counts': has_graph_counts,
            'selected_article': selected,
            'selected_graph_present': selected_graph is not None,
        },
    )


def build_route_specs(base_url: str) -> list[tuple[str, str, str]]:
    latest_thread = latest_thread_id()
    return [
        ('threads', '/threads', 'Threads'),
        ('thread_viewer', f'/thread/{latest_thread}', 'Thread Viewer'),
        ('arguments_workbench', f'/arguments/thread/{FRIENDLYJORDIES_SOURCE_THREAD_ID}', 'Arguments Workbench'),
        ('narrative_compare', '/graphs/narrative-compare?fixture=friendlyjordies_thread_extract', 'Narrative Comparison Workbench'),
        ('semantic_report', '/graphs/semantic-report?source=gwb', 'Semantic'),
        ('wiki_candidates', '/graphs/wiki-candidates', 'Candidates'),
        ('wiki_fact_timeline', '/graphs/wiki-fact-timeline?source=gwb', 'Propositions'),
        (
            'wiki_revision_contested_monitor_error_run',
            f'/graphs/wiki-revision-contested?pack=wiki_revision_monitor_v1&run={urllib.parse.quote(WIKI_MONITOR_ERROR_RUN, safe="")}&article={WIKI_MONITOR_ERROR_ARTICLE}',
            'Contested region graphs',
        ),
        (
            'wiki_revision_contested_contested_run',
            f'/graphs/wiki-revision-contested?pack=wiki_revision_contested_v1&run={urllib.parse.quote(WIKI_CONTESTED_RUN, safe="")}&article={WIKI_CONTESTED_ARTICLE}',
            'Contested region graphs',
        ),
        ('wiki_timeline', '/graphs/wiki-timeline?source=gwb', 'Timeline'),
        ('wiki_timeline_aoo', '/graphs/wiki-timeline-aoo?source=gwb', 'AAO'),
        ('wiki_timeline_aoo_all', '/graphs/wiki-timeline-aoo-all?source=gwb', 'Corpus'),
        ('mission_lens', '/graphs/mission-lens', 'Mission Lens'),
    ]


def render_markdown(base_url: str, routes: list[RouteResult], probes: list[ProbeResult]) -> str:
    lines = []
    lines.append('# Recent Page Audit')
    lines.append('')
    lines.append(f'- Base URL: `{base_url}`')
    lines.append(f'- Chat archive: `{CHAT_ARCHIVE}`')
    lines.append(f'- Wiki revision DB: `{WIKI_REVISION_DB}`')
    lines.append('')
    lines.append('## Route checks')
    lines.append('')
    lines.append('| Route | Status | Classification | Note |')
    lines.append('| --- | --- | --- | --- |')
    for row in routes:
        status = str(row.status) if row.status is not None else 'ERR'
        note = row.note if not row.error else f"{row.note}; {row.error}"
        lines.append(f'| `{row.path}` | {status} | {row.classification} | {note} |')
    lines.append('')
    lines.append('## Backing probes')
    lines.append('')
    lines.append('| Probe | Classification | Note |')
    lines.append('| --- | --- | --- |')
    for probe in probes:
        lines.append(f'| `{probe.key}` | {probe.classification} | {probe.note} |')
    lines.append('')
    failing_routes = [row for row in routes if row.classification != 'pass']
    failing_probes = [probe for probe in probes if probe.classification != 'pass']
    lines.append('## Findings')
    lines.append('')
    if not failing_routes and not failing_probes:
        lines.append('- No failures detected by the current audit matrix.')
    else:
        for row in failing_routes:
            lines.append(f'- `{row.key}`: {row.classification}. {row.note}.')
        for probe in failing_probes:
            lines.append(f'- `{probe.key}`: {probe.classification}. {probe.note}.')
    lines.append('')
    lines.append('## Raw details')
    lines.append('')
    for probe in probes:
        lines.append(f'### {probe.key}')
        lines.append('```json')
        lines.append(json.dumps(probe.details, indent=2, sort_keys=True))
        lines.append('```')
        lines.append('')
    return '\n'.join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description='Audit recent itir-svelte pages and their backing data sources.')
    ap.add_argument('--base-url', default='http://localhost:4173')
    ap.add_argument('--format', choices=['json', 'markdown'], default='markdown')
    args = ap.parse_args()

    routes = [probe_route(args.base_url, key, path, marker) for key, path, marker in build_route_specs(args.base_url)]
    probes = [
        probe_chat_archive(),
        probe_wiki_revision_db(),
        probe_wiki_revision_run('wiki_revision_monitor_v1', WIKI_MONITOR_ERROR_RUN, WIKI_MONITOR_ERROR_ARTICLE, 'wiki_revision_monitor_error_run'),
        probe_wiki_revision_run('wiki_revision_contested_v1', WIKI_CONTESTED_RUN, WIKI_CONTESTED_ARTICLE, 'wiki_revision_contested_run'),
    ]

    if args.format == 'json':
        print(json.dumps({'routes': [row.__dict__ for row in routes], 'probes': [row.__dict__ for row in probes]}, indent=2))
    else:
        print(render_markdown(args.base_url, routes, probes))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
