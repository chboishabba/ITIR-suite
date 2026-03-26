from pathlib import Path

from tools.run_zelph_partial_load_harness import HarnessCase, classify_result


def test_classify_result_marks_fallback_case_ok() -> None:
    case = HarnessCase(
        name="manifest_v1_left0",
        command=".load-partial manifest left=0",
        expected_mode="fallback_or_ok",
    )
    output = """
Partial loading from manifest: left chunks=1/18, right chunks=18/18, nameOfNode chunks=8/8, nodeOfName chunks=8/8, skip_payload=false
Shard chunk left/0 failed (...); falling back to sequential bin load
Partial loading: left chunks=1/18, right chunks=18/18, nameOfNode chunks=8/8, nodeOfName chunks=8/8, skip_payload=false
String pool size after partial load: 6632692
WARNING: partial/incomplete graph loaded; reasoning, pruning, cleanup, and destructive edits are blocked.
Time needed for partial loading: 0h0m18.159s
"""
    result = classify_result(Path("/tmp/demo.bin"), case, 0, output, 18.2)
    assert result.ok is True
    assert result.fallback_used is True
    assert result.had_repl_error is False
    assert result.reported_partial_time == "0h0m18.159s"


def test_classify_result_marks_repl_error_not_ok() -> None:
    case = HarnessCase(
        name="manifest_v1_left0",
        command=".load-partial manifest left=0",
        expected_mode="fallback_or_ok",
    )
    output = """
Partial loading from manifest: left chunks=1/18, right chunks=18/18, nameOfNode chunks=8/8, nodeOfName chunks=8/8, skip_payload=false
Error in line ".load-partial manifest left=0": capnp/serialize.c++:201: failed
"""
    result = classify_result(Path("/tmp/demo.bin"), case, 0, output, 1.1)
    assert result.ok is False
    assert result.had_repl_error is True


def test_classify_result_marks_direct_case_ok() -> None:
    case = HarnessCase(
        name="bin_left0",
        command=".load-partial demo.bin left=0 right=none nameOfNode=none nodeOfName=none",
        expected_mode="ok",
    )
    output = """
Partial loading: left chunks=1/18, right chunks=0/18, nameOfNode chunks=0/8, nodeOfName chunks=0/8, skip_payload=false
String pool size after partial load: 0
WARNING: partial/incomplete graph loaded; reasoning, pruning, cleanup, and destructive edits are blocked.
Time needed for partial loading: 0h0m2.490s
"""
    result = classify_result(Path("/tmp/demo.bin"), case, 0, output, 2.5)
    assert result.ok is True
    assert result.fallback_used is False
    assert result.reported_partial_time == "0h0m2.490s"
