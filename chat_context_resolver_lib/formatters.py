from __future__ import annotations

import json
from dataclasses import asdict
from typing import Optional


def db_payload(
    match,
    *,
    max_text_chars: int,
    latest_paragraphs: bool = False,
    recent_turns: Optional[list[dict]] = None,
    truncate_text,
    split_paragraphs,
    iso_utc,
) -> dict:
    latest_text_full = match.latest_text or ""
    payload = {
        **asdict(match),
        "earliest_ts_utc": iso_utc(match.earliest_datetime),
        "latest_ts_utc": iso_utc(match.latest_datetime),
    }
    payload["latest_text"] = truncate_text(latest_text_full, max_text_chars)
    if latest_paragraphs:
        payload["latest_paragraphs"] = [
            truncate_text(paragraph, max_text_chars)
            for paragraph in split_paragraphs(latest_text_full)
        ]
    if recent_turns:
        payload["recent_turns"] = recent_turns
    return payload


def print_result(payload: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    source = payload.get("source", "unknown")
    print(f"source: {source}")
    reason = payload.get("decision_reason")
    if reason:
        print(f"decision_reason: {reason}")
    persist = payload.get("persist") or {}
    if persist:
        print(f"persist_ok: {persist.get('ok')}")
        downloaded = persist.get("downloaded_json_paths") or []
        if downloaded:
            print(f"persist_downloaded_json_count: {len(downloaded)}")
        ingest = persist.get("ingest") or {}
        if ingest:
            print(f"persist_ingested_count: {ingest.get('ingested_count', 0)}")

    if source == "db":
        db = payload.get("db_match") or {}
        candidates = payload.get("db_candidates") or []
        analysis = payload.get("analysis") or {}

        if db:
            print(f"match_type: {db.get('match_type')}")
            print(f"title: {db.get('title')}")
            print(f"online_thread_id: {db.get('online_thread_id')}")
            print(f"canonical_thread_id: {db.get('canonical_thread_id')}")
            print(f"earliest_ts_utc: {db.get('earliest_ts_utc')}")
            print(f"latest_ts_utc: {db.get('latest_ts_utc')}")
            print(f"latest_role: {db.get('latest_role')}")
            print(f"thread_message_count: {db.get('thread_message_count')}")
            print(f"matched_thread_count: {db.get('matched_thread_count')}")
            print("latest_text:")
            print(db.get("latest_text", ""))

            latest_paragraphs = db.get("latest_paragraphs") or []
            if latest_paragraphs:
                print("latest_paragraphs:")
                for idx, paragraph in enumerate(latest_paragraphs, start=1):
                    print(f"[{idx}] {paragraph}")
            recent_turns = db.get("recent_turns") or []
            if recent_turns:
                print("recent_turns:")
                for idx, turn in enumerate(recent_turns, start=1):
                    print(
                        f"[{idx}] ts={turn.get('ts')} "
                        f"ts_utc={turn.get('ts_utc')} role={turn.get('role')}:"
                    )
                    print(turn.get("text", ""))
        else:
            print("db_match: (none)")

        if candidates:
            print("db_candidates:")
            for idx, candidate in enumerate(candidates, start=1):
                print(
                    f"[{idx}] hits={candidate.get('hit_count')} "
                    f"latest_ts={candidate.get('latest_ts')} "
                    f"id={candidate.get('canonical_thread_id')} "
                    f"title={candidate.get('title')}"
                )
        if analysis:
            print(f"analysis_scope: {analysis.get('analysis_scope')}")
            if analysis.get("analysis_scope") == "thread_local":
                stats = analysis.get("transcript_stats") or {}
                print(
                    "transcript_stats: "
                    f"messages={stats.get('message_count', 0)} "
                    f"lines={stats.get('stitched_line_count', 0)} "
                    f"chars={stats.get('character_count', 0)}"
                )
                for item in analysis.get("term_stats") or []:
                    print(
                        "term_stat: "
                        f"term={item.get('term')} raw={item.get('raw_count')} "
                        f"line_hits={item.get('line_hit_count')} "
                        f"message_hits={item.get('message_hit_count')} "
                        f"density_100_lines={item.get('density_per_100_lines')}"
                    )
                if analysis.get("top_terms"):
                    print("top_terms:")
                    for item in analysis["top_terms"]:
                        print(f"  {item.get('term')}: {item.get('count')}")
                if analysis.get("mentions"):
                    print("mentions:")
                    for mention in analysis["mentions"]:
                        print(
                            f"  term={mention.get('term')} "
                            f"thread_line={mention.get('thread_line_start')} "
                            f"message={mention.get('message_index')}:{mention.get('message_line_start')} "
                            f"role={mention.get('role')} text={mention.get('line_text')}"
                        )
            elif analysis.get("analysis_scope") == "cross_thread":
                print("cross_thread_results:")
                for item in analysis.get("results") or []:
                    print(
                        f"  raw={item.get('raw_count')} lines={item.get('line_hit_count')} "
                        f"density={item.get('density_per_100_lines')} "
                        f"id={item.get('canonical_thread_id')} title={item.get('title')}"
                    )
        return

    if source == "web":
        web = payload.get("web", {})
        print("web_command:")
        print(" ".join(web.get("command", [])))
        if web.get("stderr"):
            print("web_stderr:")
            print(web["stderr"].rstrip())
        live_warning = payload.get("web_recent_turns_warning")
        if live_warning:
            print(f"web_recent_turns_warning: {live_warning}")
        live_turns = payload.get("web_recent_turns") or []
        if live_turns:
            print("web_recent_turns:")
            for idx, turn in enumerate(live_turns, start=1):
                print(
                    f"[{idx}] ts={turn.get('ts')} "
                    f"ts_utc={turn.get('ts_utc')} role={turn.get('role')}:"
                )
                print(turn.get("text", ""))
        print("web_stdout:")
        print((web.get("stdout") or "").rstrip())
        return

    print(payload.get("error", "unknown error"))
