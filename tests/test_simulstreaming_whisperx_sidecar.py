from __future__ import annotations

import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SIMULSTREAMING_ROOT = ROOT / "SimulStreaming"
if str(SIMULSTREAMING_ROOT) not in sys.path:
    sys.path.insert(0, str(SIMULSTREAMING_ROOT))

from simulstreaming.whisper.whisper_streaming.whisperx_sidecar import (  # noqa: E402
    FinalSegmentPayload,
    WhisperXSidecar,
)


class FakeAligner:
    def align(self, payload: FinalSegmentPayload):
        assert payload.audio is not None
        assert payload.source_row["text"]
        return {
            "model": "fake-whisperx",
            "language": payload.language or "en",
            "segments": [
                {
                    "start": payload.source_row["start"],
                    "end": payload.source_row["end"],
                    "text": payload.source_row["text"],
                    "confidence": 0.9,
                    "words": [
                        {
                            "start": payload.source_row["start"],
                            "end": payload.source_row["end"],
                            "word": payload.source_row["text"].strip(),
                            "confidence": 0.9,
                        }
                    ],
                }
            ],
        }


def test_sync_sidecar_aligns_latest_text_when_final_row_has_no_text():
    sidecar = WhisperXSidecar(
        enabled=True,
        language="en",
        aligner=FakeAligner(),
        async_mode=False,
    )
    sidecar.append_audio_chunk(np.ones(1600, dtype=np.float32))
    partial_rows = sidecar.process_output(
        {"start": 0.1, "end": 0.5, "text": " hello", "is_final": False},
        now=1.0,
    )
    assert len(partial_rows) == 1
    assert partial_rows[0]["segment_id"] == 0

    final_rows = sidecar.process_output({"is_final": True}, now=2.0)
    assert len(final_rows) == 2
    assert final_rows[0]["segment_id"] == 0
    assert final_rows[1]["event"] == "whisperx_alignment"
    assert final_rows[1]["segment_id"] == 0
    assert final_rows[1]["source_text"] == " hello"
    assert final_rows[1]["whisperx_transcript"]["segments"][0]["text"] == " hello"


def test_async_sidecar_drains_alignment_rows_after_final_segment():
    sidecar = WhisperXSidecar(
        enabled=True,
        language="en",
        aligner=FakeAligner(),
        async_mode=True,
    )
    sidecar.append_audio_chunk(np.ones(3200, dtype=np.float32))
    immediate = sidecar.process_output(
        {"start": 0.0, "end": 0.2, "text": " test", "is_final": True},
        now=3.0,
    )
    assert len(immediate) == 1
    assert immediate[0]["segment_id"] == 0

    flushed = sidecar.close(now=4.0)
    assert len(flushed) == 1
    assert flushed[0]["event"] == "whisperx_alignment"
    assert flushed[0]["segment_id"] == 0
    assert flushed[0]["emission_time"] == 4.0
