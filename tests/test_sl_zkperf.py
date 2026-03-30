from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import subprocess
import sys

SENSIBLAW_ROOT = Path("SensibLaw").resolve()
SENSIBLAW_SRC = SENSIBLAW_ROOT / "src"
for path in (SENSIBLAW_ROOT, SENSIBLAW_SRC):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from fact_intake import persist_contested_affidavit_review
from itir_jmd_bridge.sl_zkperf import (
    build_zkperf_observation_from_contested_review_db,
    build_zkperf_observation_from_sl_file,
    build_zkperf_trace_observations_from_progress_log,
)


FIXTURE = Path("itir-svelte/tests/fixtures/fact_review_wave1_real_au_demo_bundle.json")


def _metric_map(observation: dict) -> dict[str, int]:
    return {row["metric"]: row["value"] for row in observation["metrics"]}


def test_build_zkperf_observation_from_sl_file() -> None:
    observation = build_zkperf_observation_from_sl_file(FIXTURE)
    metrics = _metric_map(observation)

    assert observation["run_id"] == "run:5ab560b645ee10d0badd59fe6ef0a9442bf5d41bc57e7ff950688ae5961ef12d"
    assert observation["trace_id"].startswith("sl-trace:")
    assert observation["status"] == "observed"
    assert observation["source_ref"].endswith(str(FIXTURE))
    assert observation["zkperf_observation_id"].startswith("zkperf-obsv:")
    assert observation["hash"].startswith("sha256:")
    assert observation["proof_refs"]
    assert observation["trace_refs"]
    assert metrics["payload_bytes"] > 0
    assert metrics["acceptance_story_count"] == 6
    assert metrics["acceptance_pass_count"] == 6
    assert metrics["dict_nodes"] > 0


def test_built_observation_is_json_serializable() -> None:
    observation = build_zkperf_observation_from_sl_file(FIXTURE)
    json.dumps(observation)


def test_run_sl_with_zkperf_script_captures_runtime_metrics(tmp_path: Path) -> None:
    sl_output = tmp_path / "sl-output.json"
    observation_output = tmp_path / "observation.json"
    command = [
        sys.executable,
        "scripts/run_sl_with_zkperf.py",
        "--sl-output",
        str(sl_output),
        "--observation-output",
        str(observation_output),
        "--",
        sys.executable,
        "-c",
        (
            "import json, pathlib; "
            "pathlib.Path(r'" + str(sl_output) + "').write_text("
            "json.dumps({'run': {'semantic_run_id': 'run:test-runtime'}}, sort_keys=True), encoding='utf-8')"
        ),
    ]
    subprocess.run(command, cwd=Path.cwd(), check=True)

    payload = json.loads(observation_output.read_text(encoding="utf-8"))
    metrics = _metric_map(payload)
    trace_ref_kinds = {row["kind"] for row in payload["trace_refs"]}

    assert payload["run_id"] == "run:test-runtime"
    assert metrics["elapsed_ms"] >= 0
    assert metrics["exit_code"] == 0
    assert metrics["stdout_bytes"] >= 0
    assert metrics["stderr_bytes"] >= 0
    assert metrics["minor_page_faults"] >= 0
    assert metrics["major_page_faults"] >= 0
    assert metrics["voluntary_context_switches"] >= 0
    assert metrics["involuntary_context_switches"] >= 0
    assert metrics["block_input_ops"] >= 0
    assert metrics["block_output_ops"] >= 0
    assert metrics["ipc_messages_sent"] >= 0
    assert metrics["ipc_messages_received"] >= 0
    assert metrics["signals_received"] >= 0
    assert metrics["swaps"] >= 0
    assert "sl_stdout_path" in trace_ref_kinds
    assert "sl_stderr_path" in trace_ref_kinds
    assert "sl_command" in trace_ref_kinds


def test_run_sl_with_zkperf_script_emits_trace_observations_from_progress(tmp_path: Path) -> None:
    sl_output = tmp_path / "sl-output.json"
    observation_output = tmp_path / "observation.json"
    trace_output = tmp_path / "trace-observations.json"
    stream_output = tmp_path / "stream-observations.json"
    command = [
        sys.executable,
        "scripts/run_sl_with_zkperf.py",
        "--sl-output",
        str(sl_output),
        "--observation-output",
        str(observation_output),
        "--trace-observations-output",
        str(trace_output),
        "--stream-observations-output",
        str(stream_output),
        "--",
        sys.executable,
        "-c",
        (
            "import json, pathlib, sys; "
            "print('[progress] load_started section=demo 0/2 elapsed=0.1s status=running - load', file=sys.stderr); "
            "print('[progress] load_finished section=demo 2/2 elapsed=0.3s status=complete - done', file=sys.stderr); "
            "pathlib.Path(r'" + str(sl_output) + "').write_text("
            "json.dumps({'run': {'semantic_run_id': 'run:test-progress'}}, sort_keys=True), encoding='utf-8')"
        ),
    ]
    subprocess.run(command, cwd=Path.cwd(), check=True)

    trace_observations = json.loads(trace_output.read_text(encoding="utf-8"))
    assert len(trace_observations) == 2
    trace_metrics = [_metric_map(row) for row in trace_observations]
    assert trace_metrics[0]["trace.stage.load-started"] == 1
    assert trace_metrics[0]["trace.stage_family.start"] == 1
    assert trace_metrics[0]["trace.section.demo"] == 1
    assert trace_metrics[0]["trace.progress_ratio"] == 0.0
    assert trace_metrics[0]["trace.progress_remaining_ratio"] == 1.0
    assert trace_metrics[0]["trace.message_present"] == 1
    assert trace_metrics[0]["trace.message_length_chars"] == 4
    assert trace_metrics[1]["trace.stage.load-finished"] == 1
    assert trace_metrics[1]["trace.progress_ratio"] == 1.0
    assert trace_metrics[1]["trace.stage_family.finish"] == 1
    assert trace_metrics[1]["trace.progress_delta_ratio"] == 1.0
    assert trace_metrics[1]["trace.transition.load-started__to__load-finished"] == 1

    stream_payload = json.loads(stream_output.read_text(encoding="utf-8"))
    assert len(stream_payload) == 3
    assert stream_payload[-1]["run_id"] == "run:test-progress"


def test_trace_observations_include_domain_roles(tmp_path: Path) -> None:
    progress_log = tmp_path / "stderr.log"
    progress_log.write_text(
        "\n".join(
            [
                "[progress] affidavit_load section=affidavit 0/1 - loading affidavit",
                "[progress] coverage_match status=running 1/2 - coverage matching",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    observations = build_zkperf_trace_observations_from_progress_log(
        progress_log,
        run_id="run:domain-role-test",
        trace_id="sl-trace:domain-role-test",
        started_at="2026-03-30T04:00:00Z",
        finished_at="2026-03-30T04:00:02Z",
    )

    metrics0 = _metric_map(observations[0])
    metrics1 = _metric_map(observations[1])

    assert metrics0["trace.domain_role.affidavit"] == 1
    assert metrics1["trace.domain_role.coverage"] == 1
    assert metrics1["trace.domain_role.matching"] == 1

    trace_ref_kinds = [row["kind"] for row in observations[1]["trace_refs"]]
    assert "trace_domain_role" in trace_ref_kinds


def test_trace_observations_include_domain_signals(tmp_path: Path) -> None:
    progress_log = tmp_path / "stderr.log"
    progress_log.write_text(
        "\n".join(
            [
                "[progress] review_gap status=running 0/3 - missing review items",
                "[progress] persist_finished status=complete 3/3 - covered rows written",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    observations = build_zkperf_trace_observations_from_progress_log(
        progress_log,
        run_id="run:domain-signal-test",
        trace_id="sl-trace:domain-signal-test",
        started_at="2026-03-30T04:00:00Z",
        finished_at="2026-03-30T04:00:02Z",
    )

    metrics0 = _metric_map(observations[0])
    metrics1 = _metric_map(observations[1])

    assert metrics0["trace.domain_signal.review_gap"] == 1
    assert metrics1["trace.domain_signal.persistence_boundary"] == 1
    assert metrics1["trace.domain_signal.coverage_recovered"] == 1

    trace_ref_kinds = [row["kind"] for row in observations[1]["trace_refs"]]
    assert "trace_domain_signal" in trace_ref_kinds


def test_build_zkperf_trace_observations_from_json_progress_log(tmp_path: Path) -> None:
    progress_log = tmp_path / "stderr.log"
    progress_log.write_text(
        "\n".join(
            [
                json.dumps({"stage": "build_started", "section": "google_docs", "completed": 0, "total": 2}),
                json.dumps({"stage": "build_finished", "section": "google_docs", "completed": 2, "total": 2, "elapsed_seconds": 1.5}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    observations = build_zkperf_trace_observations_from_progress_log(
        progress_log,
        run_id="run:test-progress-log",
        trace_id="sl-trace:test-progress-log",
        started_at="2026-03-30T04:00:00Z",
        finished_at="2026-03-30T04:00:02Z",
        command=["python", "demo.py"],
    )
    assert len(observations) == 2
    metrics = _metric_map(observations[1])
    trace_ref_kinds = {row["kind"] for row in observations[0]["trace_refs"]}
    assert metrics["trace.stage.build-finished"] == 1
    assert metrics["trace.stage_family.finish"] == 1
    assert metrics["trace.progress_ratio"] == 1.0
    assert metrics["trace.progress_delta_ratio"] == 1.0
    assert metrics["trace.transition.build-started__to__build-finished"] == 1
    assert metrics["trace.message_present"] == 0
    assert "sl_progress_log_path" in trace_ref_kinds
    assert "progress_stage" in trace_ref_kinds
    assert "sl_observation_role" in trace_ref_kinds


def test_build_zkperf_observation_from_sl_file_with_theory_evidence(tmp_path: Path) -> None:
    sl_path = tmp_path / "sl.json"
    sl_path.write_text(json.dumps({"run": {"semantic_run_id": "run:mdl-test"}, "summary": {"covered_count": 1}}), encoding="utf-8")
    theory_path = tmp_path / "theory.json"
    theory_path.write_text(
        json.dumps(
            {
                "family_context": {
                    "family": "z_pt_7tev_atlas",
                    "report_summary": {
                        "closestpoint": [{"closest_frac": 1.0, "closest_max_violation": -0.01}],
                        "fejer_set": [{"fejer_set_frac": 1.0, "fejer_set_max_violation": 0.0}],
                        "mdl_descent": [
                            {
                                "MDL_monotone": False,
                                "MDL_violations": 2,
                                "MDL_worst_increase": 0.694577,
                                "MDL_worst_iter": 10,
                            }
                        ],
                    },
                }
            }
        ),
        encoding="utf-8",
    )

    observation = build_zkperf_observation_from_sl_file(
        sl_path,
        theory_evidence_path=theory_path,
    )
    metrics = _metric_map(observation)
    trace_refs = {row["kind"]: row["ref"] for row in observation["trace_refs"]}
    proof_refs = {row["kind"]: row["ref"] for row in observation["proof_refs"]}

    assert metrics["theory.mdl.available"] == 1
    assert metrics["theory.mdl.descent_monotone"] == 0
    assert metrics["theory.mdl.violation_count"] == 2
    assert metrics["theory.mdl.worst_increase"] == 0.694577
    assert metrics["theory.dynamics.closestpoint.available"] == 1
    assert metrics["theory.dynamics.fejer.available"] == 1
    assert trace_refs["theory_family"] == "z_pt_7tev_atlas"
    assert proof_refs["theory_evidence_kind"] == "dashi_family_report"


def test_build_zkperf_observation_from_sl_file_with_mdl_evidence_v1(tmp_path: Path) -> None:
    sl_path = tmp_path / "sl.json"
    sl_path.write_text(json.dumps({"summary": {"covered_count": 1}}), encoding="utf-8")
    theory_path = tmp_path / "mdl-evidence.json"
    theory_path.write_text(
        json.dumps(
            {
                "schema_version": "mdl-evidence-v1",
                "program_id": "demo-program",
                "run_id": "run-123",
                "input_id": "input-456",
                "family": "demo-family",
                "model_class": "demo-model-class",
                "coding_scheme": "exact_code_length_v1",
                "measured_at": "2026-03-30T12:34:56Z",
                "mdl": {
                    "total_length": 1234.5,
                    "descent_monotone": False,
                    "violation_count": 3,
                    "worst_increase": 12.25,
                    "worst_step": 17,
                },
                "trajectory": [
                    {"step": 0, "length": 1300.0},
                    {"step": 1, "length": 1288.5},
                ],
                "witness": {
                    "artifact_path": "artifacts/mdl/run-123.json",
                    "commit": "abcdef123456",
                },
            }
        ),
        encoding="utf-8",
    )

    observation = build_zkperf_observation_from_sl_file(
        sl_path,
        theory_evidence_path=theory_path,
    )
    metrics = _metric_map(observation)
    trace_refs = {row["kind"]: row["ref"] for row in observation["trace_refs"]}
    proof_refs = {row["kind"]: row["ref"] for row in observation["proof_refs"]}

    assert metrics["theory.mdl.available"] == 1
    assert metrics["theory.mdl.total_length"] == 1234.5
    assert metrics["theory.mdl.descent_monotone"] == 0
    assert metrics["theory.mdl.violation_count"] == 3
    assert metrics["theory.mdl.worst_increase"] == 12.25
    assert metrics["theory.mdl.worst_step"] == 17
    assert metrics["theory.mdl.trajectory_step_count"] == 2
    assert trace_refs["theory_program_id"] == "demo-program"
    assert trace_refs["theory_coding_scheme"] == "exact_code_length_v1"
    assert proof_refs["theory_evidence_kind"] == "mdl_evidence_v1"
    assert proof_refs["theory_witness_artifact_path"] == "artifacts/mdl/run-123.json"
    assert proof_refs["theory_witness_commit"] == "abcdef123456"


def test_build_zkperf_observation_from_sl_file_with_family_classification_evidence(tmp_path: Path) -> None:
    sl_path = tmp_path / "sl.json"
    sl_path.write_text(json.dumps({"summary": {"covered_count": 1}}), encoding="utf-8")
    theory_path = tmp_path / "family-classification.json"
    theory_path.write_text(
        json.dumps(
            [
                {
                    "family": "dijet_chi_7tev_cms",
                    "cone_ok": True,
                    "fejer_ok": True,
                    "closest_ok": True,
                    "mdl_exact_ok": True,
                    "boundary_steps": 0,
                    "tail_localized": False,
                    "terminal_boundary": False,
                    "family_class": "interior_family",
                }
            ]
        ),
        encoding="utf-8",
    )

    observation = build_zkperf_observation_from_sl_file(
        sl_path,
        theory_evidence_path=theory_path,
        theory_family="dijet_chi_7tev_cms",
    )
    metrics = _metric_map(observation)

    assert metrics["theory.mdl.exact_ok"] == 1
    assert metrics["theory.dynamics.cone_ok"] == 1
    assert metrics["theory.dynamics.fejer_ok"] == 1
    assert metrics["theory.dynamics.closest_ok"] == 1


def test_affidavit_semantic_counters(tmp_path: Path) -> None:
    payload = {
        "summary": {
            "contested_affidavit_count": 2,
            "contested_source_count": 3,
            "covered_count": 5,
            "unsupported_affidavit_count": 1,
            "substantive_response_ratio": 0.5,
                "conflict_state_counts": {"clean": 3, "contested": 1, "unresolved": 1},
            "support_status_counts": {"supported": 3, "unsupported": 2},
        },
        "normalized_metrics_v1": {
            "candidate_signal_count": 10,
            "candidate_signal_density": 1.5,
            "review_item_status_counts": {"review_required": 7, "accepted": 1},
            "source_status_counts": {"review_required": 4, "accepted": 2},
            "primary_workload_counts": {"queue_pressure": 3},
        },
        "affidavit_rows": [
            {"coverage_status": "covered", "support_status": "supported", "relation_type": "agrees"},
            {"coverage_status": "missing", "support_status": "unsupported", "relation_type": "disputes"},
        ],
        "source_review_rows": [
            {"review_status": "review_required", "candidate_status": "candidate"},
            {"review_status": "accepted", "candidate_status": "not_candidate"},
        ],
        "zelph_claim_state_facts": [
            {"support_status": "supported", "coverage_status": "covered", "conflict_state": "clean"},
            {"support_status": "unsupported", "coverage_status": "missing", "conflict_state": "contested"},
        ],
    }
    sl_path = tmp_path / "sl.json"
    sl_path.write_text(json.dumps(payload), encoding="utf-8")

    observation = build_zkperf_observation_from_sl_file(sl_path)
    metrics = _metric_map(observation)

    assert metrics["summary.contested_affidavit_count"] == 2
    assert metrics["summary.contested_source_count"] == 3
    assert metrics["summary.support_status.supported"] == 3
    assert metrics["summary.support_status.unsupported"] == 2
    assert metrics["summary.conflict_state.clean"] == 3
    assert metrics["norm.candidate_signal_count"] == 10
    assert metrics["norm.candidate_signal_density"] == 1.5
    assert metrics["affidavit_rows.count"] == 2
    assert metrics["affidavit_rows.coverage_status.covered"] == 1
    assert metrics["affidavit_rows.coverage_status.missing"] == 1
    assert metrics["affidavit_rows.relation_type.agrees"] == 1
    assert metrics["affidavit_rows.relation_type.disputes"] == 1
    assert metrics["source_review_rows.count"] == 2
    assert metrics["source_review_rows.review_status.review_required"] == 1
    assert metrics["source_review_rows.review_status.accepted"] == 1
    assert metrics["zelph_claim_state_facts.count"] == 2
    assert metrics["zelph_claim_state_facts.conflict_state.clean"] == 1
    assert metrics["semantic_gap_model_version"] == 1
    assert metrics["semantic_gap_terms.missing_review_count"] == 0
    assert metrics["semantic_gap_terms.unresolved_conflict_count"] == 1
    assert metrics["semantic_gap_terms.contested_affidavit_count"] == 2
    assert metrics["semantic_gap_terms.covered_count"] == 5
    assert metrics["semantic_gap_weights.missing_review"] == 1.0
    assert metrics["semantic_gap_weights.unresolved_conflict"] == 3.0
    assert metrics["semantic_gap_weights.contested_affidavit"] == 2.0
    assert metrics["semantic_gap_weights.covered_credit"] == 1.0
    assert metrics["semantic_gap_score"] == 2.0


def test_build_zkperf_observation_from_contested_review_db(tmp_path: Path) -> None:
    db_path = tmp_path / "itir.sqlite"
    payload = {
        "version": "affidavit.coverage.review.v1",
        "fixture_kind": "contested_review",
        "source_input": {
            "path": "https://example.test/response",
            "source_kind": "google_doc",
            "source_label": "response_doc",
        },
        "affidavit_input": {
            "path": "https://example.test/affidavit",
            "character_count": 123,
        },
        "summary": {
            "source_row_count": 1,
            "affidavit_proposition_count": 1,
            "covered_count": 1,
            "partial_count": 0,
            "contested_affidavit_count": 0,
            "unsupported_affidavit_count": 0,
            "missing_review_count": 0,
            "contested_source_count": 0,
            "abstained_source_count": 0,
            "semantic_basis_counts": {"structural": 1},
            "promotion_status_counts": {"promoted_true": 1},
            "support_direction_counts": {"for": 1},
            "conflict_state_counts": {"clean": 1},
            "evidentiary_state_counts": {"supported": 1},
            "operational_status_counts": {"claim_with_support": 1},
        },
        "affidavit_rows": [
            {
                "proposition_id": "aff-prop:p1-s1",
                "paragraph_id": "p1",
                "paragraph_order": 1,
                "sentence_order": 1,
                "text": "Test proposition",
                "coverage_status": "covered",
                "best_source_row_id": "source-row-1",
                "best_match_score": 0.9,
                "best_adjusted_match_score": 0.95,
                "best_match_basis": "structural",
                "best_match_excerpt": "Test excerpt",
                "duplicate_match_excerpt": "",
                "best_response_role": "admission",
                "support_status": "supported",
                "semantic_basis": "structural",
                "promotion_status": "promoted_true",
                "promotion_basis": "structural",
                "promotion_reason": "matched",
                "support_direction": "for",
                "conflict_state": "clean",
                "evidentiary_state": "supported",
                "operational_status": "claim_with_support",
                "relation_root": "agrees",
                "relation_leaf": "predicate_text",
                "primary_target_component": "predicate_text",
                "explanation": {"reason": "demo"},
                "missing_dimensions": [],
                "semantic_candidate": {"schema_version": "contested.semantic_candidate.v1"},
                "claim": {"text": "Test proposition"},
                "response": {"text": "Test excerpt"},
                "justifications": [],
                "matched_source_rows": [],
            }
        ],
        "source_review_rows": [
            {
                "source_row_id": "source-row-1",
                "source_kind": "google_doc",
                "text": "Test excerpt",
                "candidate_status": "candidate",
                "review_status": "accepted",
                "best_affidavit_proposition_id": "aff-prop:p1-s1",
                "best_match_score": 0.9,
                "best_adjusted_match_score": 0.95,
                "best_match_basis": "structural",
                "best_match_excerpt": "Test excerpt",
                "best_response_role": "admission",
                "matched_affidavit_proposition_ids": ["aff-prop:p1-s1"],
                "related_affidavit_proposition_ids": [],
                "reason_codes": [],
                "workload_classes": [],
                "candidate_anchors": [],
            }
        ],
        "zelph_claim_state_facts": [
            {
                "fact_id": "zelph:1",
                "proposition_id": "aff-prop:p1-s1",
                "best_source_row_id": "source-row-1",
                "fact_kind": "contested_claim_state",
                "semantic_basis": "structural",
                "promotion_status": "promoted_true",
                "promotion_basis": "structural",
                "support_direction": "for",
                "conflict_state": "clean",
                "evidentiary_state": "supported",
                "operational_status": "claim_with_support",
            }
        ],
    }
    with sqlite3.connect(str(db_path)) as conn:
        persist_summary = persist_contested_affidavit_review(conn, payload)

    observation = build_zkperf_observation_from_contested_review_db(
        db_path,
        review_run_id=persist_summary["review_run_id"],
    )
    metrics = _metric_map(observation)
    trace_ref_kinds = {row["kind"] for row in observation["trace_refs"]}

    assert observation["run_id"] == persist_summary["review_run_id"]
    assert metrics["summary.covered_count"] == 1
    assert metrics["affidavit_rows.count"] == 1
    assert metrics["source_review_rows.count"] == 1
    assert metrics["zelph_claim_state_facts.count"] == 1
    assert metrics["semantic_gap_score"] == 0.0
    assert "sl_db_path" in trace_ref_kinds
    assert "sl_review_run_id" in trace_ref_kinds


def test_run_sl_with_zkperf_script_supports_sqlite_contested_review_mode(tmp_path: Path) -> None:
    db_path = tmp_path / "itir.sqlite"
    observation_output = tmp_path / "observation.json"
    sl_output = tmp_path / "unused.json"
    command = [
        sys.executable,
        "scripts/run_sl_with_zkperf.py",
        "--sl-output",
        str(sl_output),
        "--sl-db-path",
        str(db_path),
        "--observation-output",
        str(observation_output),
        "--",
        sys.executable,
        "-c",
        (
            "import sqlite3, sys; "
            "sys.path.insert(0, r'" + str(SENSIBLAW_ROOT) + "'); "
            "sys.path.insert(0, r'" + str(SENSIBLAW_SRC) + "'); "
            "from fact_intake import persist_contested_affidavit_review; "
            "payload = {"
            "'version':'affidavit.coverage.review.v1',"
            "'fixture_kind':'contested_review',"
            "'source_input':{'path':'https://example.test/response','source_kind':'google_doc','source_label':'response_doc'},"
            "'affidavit_input':{'path':'https://example.test/affidavit','character_count':123},"
            "'summary':{'source_row_count':1,'affidavit_proposition_count':1,'covered_count':1,'partial_count':0,'contested_affidavit_count':0,'unsupported_affidavit_count':0,'missing_review_count':0,'contested_source_count':0,'abstained_source_count':0,'semantic_basis_counts':{'structural':1},'promotion_status_counts':{'promoted_true':1},'support_direction_counts':{'for':1},'conflict_state_counts':{'clean':1},'evidentiary_state_counts':{'supported':1},'operational_status_counts':{'claim_with_support':1}},"
            "'affidavit_rows':[{'proposition_id':'aff-prop:p1-s1','paragraph_id':'p1','paragraph_order':1,'sentence_order':1,'text':'Test proposition','coverage_status':'covered','best_source_row_id':'source-row-1','best_match_score':0.9,'best_adjusted_match_score':0.95,'best_match_basis':'structural','best_match_excerpt':'Test excerpt','duplicate_match_excerpt':'','best_response_role':'admission','support_status':'supported','semantic_basis':'structural','promotion_status':'promoted_true','promotion_basis':'structural','promotion_reason':'matched','support_direction':'for','conflict_state':'clean','evidentiary_state':'supported','operational_status':'claim_with_support','relation_root':'agrees','relation_leaf':'predicate_text','primary_target_component':'predicate_text','explanation':{'reason':'demo'},'missing_dimensions':[],'semantic_candidate':{'schema_version':'contested.semantic_candidate.v1'},'claim':{'text':'Test proposition'},'response':{'text':'Test excerpt'},'justifications':[],'matched_source_rows':[]}],"
            "'source_review_rows':[{'source_row_id':'source-row-1','source_kind':'google_doc','text':'Test excerpt','candidate_status':'candidate','review_status':'accepted','best_affidavit_proposition_id':'aff-prop:p1-s1','best_match_score':0.9,'best_adjusted_match_score':0.95,'best_match_basis':'structural','best_match_excerpt':'Test excerpt','best_response_role':'admission','matched_affidavit_proposition_ids':['aff-prop:p1-s1'],'related_affidavit_proposition_ids':[],'reason_codes':[],'workload_classes':[],'candidate_anchors':[]}],"
            "'zelph_claim_state_facts':[{'fact_id':'zelph:1','proposition_id':'aff-prop:p1-s1','best_source_row_id':'source-row-1','fact_kind':'contested_claim_state','semantic_basis':'structural','promotion_status':'promoted_true','promotion_basis':'structural','support_direction':'for','conflict_state':'clean','evidentiary_state':'supported','operational_status':'claim_with_support'}]"
            "}; "
            "conn = sqlite3.connect(r'" + str(db_path) + "'); "
            "persist_contested_affidavit_review(conn, payload); "
            "conn.close()"
        ),
    ]
    subprocess.run(command, cwd=Path.cwd(), check=True)

    payload = json.loads(observation_output.read_text(encoding="utf-8"))
    metrics = _metric_map(payload)
    assert payload["run_id"].startswith("contested_review:")
    assert metrics["summary.covered_count"] == 1
    assert metrics["semantic_gap_score"] == 0.0
    assert metrics["elapsed_ms"] >= 0


def test_run_sl_with_zkperf_script_allows_sqlite_mode_without_sl_output(tmp_path: Path) -> None:
    db_path = tmp_path / "itir.sqlite"
    observation_output = tmp_path / "observation.json"
    command = [
        sys.executable,
        "scripts/run_sl_with_zkperf.py",
        "--sl-db-path",
        str(db_path),
        "--observation-output",
        str(observation_output),
        "--",
        sys.executable,
        "-c",
        (
            "import sqlite3, sys; "
            "sys.path.insert(0, r'" + str(SENSIBLAW_ROOT) + "'); "
            "sys.path.insert(0, r'" + str(SENSIBLAW_SRC) + "'); "
            "from fact_intake import persist_contested_affidavit_review; "
            "payload = {"
            "'version':'affidavit.coverage.review.v1',"
            "'fixture_kind':'contested_review',"
            "'source_input':{'path':'https://example.test/response','source_kind':'google_doc','source_label':'response_doc'},"
            "'affidavit_input':{'path':'https://example.test/affidavit','character_count':123},"
            "'summary':{'source_row_count':1,'affidavit_proposition_count':1,'covered_count':1,'partial_count':0,'contested_affidavit_count':0,'unsupported_affidavit_count':0,'missing_review_count':0,'contested_source_count':0,'abstained_source_count':0,'semantic_basis_counts':{'structural':1},'promotion_status_counts':{'promoted_true':1},'support_direction_counts':{'for':1},'conflict_state_counts':{'clean':1},'evidentiary_state_counts':{'supported':1},'operational_status_counts':{'claim_with_support':1}},"
            "'affidavit_rows':[{'proposition_id':'aff-prop:p1-s1','paragraph_id':'p1','paragraph_order':1,'sentence_order':1,'text':'Test proposition','coverage_status':'covered','best_source_row_id':'source-row-1','best_match_score':0.9,'best_adjusted_match_score':0.95,'best_match_basis':'structural','best_match_excerpt':'Test excerpt','duplicate_match_excerpt':'','best_response_role':'admission','support_status':'supported','semantic_basis':'structural','promotion_status':'promoted_true','promotion_basis':'structural','promotion_reason':'matched','support_direction':'for','conflict_state':'clean','evidentiary_state':'supported','operational_status':'claim_with_support','relation_root':'agrees','relation_leaf':'predicate_text','primary_target_component':'predicate_text','explanation':{'reason':'demo'},'missing_dimensions':[],'semantic_candidate':{'schema_version':'contested.semantic_candidate.v1'},'claim':{'text':'Test proposition'},'response':{'text':'Test excerpt'},'justifications':[],'matched_source_rows':[]}],"
            "'source_review_rows':[{'source_row_id':'source-row-1','source_kind':'google_doc','text':'Test excerpt','candidate_status':'candidate','review_status':'accepted','best_affidavit_proposition_id':'aff-prop:p1-s1','best_match_score':0.9,'best_adjusted_match_score':0.95,'best_match_basis':'structural','best_match_excerpt':'Test excerpt','best_response_role':'admission','matched_affidavit_proposition_ids':['aff-prop:p1-s1'],'related_affidavit_proposition_ids':[],'reason_codes':[],'workload_classes':[],'candidate_anchors':[]}],"
            "'zelph_claim_state_facts':[{'fact_id':'zelph:1','proposition_id':'aff-prop:p1-s1','best_source_row_id':'source-row-1','fact_kind':'contested_claim_state','semantic_basis':'structural','promotion_status':'promoted_true','promotion_basis':'structural','support_direction':'for','conflict_state':'clean','evidentiary_state':'supported','operational_status':'claim_with_support'}]"
            "}; "
            "conn = sqlite3.connect(r'" + str(db_path) + "'); "
            "persist_contested_affidavit_review(conn, payload); "
            "conn.close()"
        ),
    ]
    subprocess.run(command, cwd=Path.cwd(), check=True)

    payload = json.loads(observation_output.read_text(encoding="utf-8"))
    metrics = _metric_map(payload)
    assert payload["run_id"].startswith("contested_review:")
    assert metrics["summary.covered_count"] == 1
    assert metrics["semantic_gap_score"] == 0.0
    assert metrics["elapsed_ms"] >= 0
