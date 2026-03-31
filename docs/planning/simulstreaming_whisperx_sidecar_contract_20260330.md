# SimulStreaming WhisperX Sidecar Contract

Date: 2026-03-30

## Purpose

Define the bounded integration contract for attaching WhisperX alignment to
`SimulStreaming/` without replacing the live SimulStreaming decoder loop.

## Decision

- Keep SimulStreaming as the streaming ASR engine.
- Run WhisperX only on committed/final segments.
- Preserve low-latency partial output from SimulStreaming.
- Reuse a WhisperX-style transcript shape so downstream ingest can map onto the
  existing `SensibLaw` ASR/WhisperX adapter contract.

## Runtime Rules

### File simulation

- Hook at the JSON emission boundary in
  `SimulStreaming/simulstreaming/whisper/whisper_streaming/whisper_online_main.py`.
- When `is_final` is false:
  - emit the original SimulStreaming row only.
- When `is_final` is true:
  - emit the original row;
  - run WhisperX alignment against the buffered audio for the just-closed
    segment;
  - emit a second JSON row that carries the aligned transcript segment.

### Server mode

- Hook at the TCP send boundary in
  `SimulStreaming/simulstreaming/whisper/whisper_streaming/whisper_server.py`.
- Do not run WhisperX synchronously in the receive/process/send loop.
- Queue final-segment alignment work onto a background worker.
- Emit the original SimulStreaming row immediately.
- Emit a second JSON row once alignment finishes.

## JSON Contract

The original SimulStreaming row remains unchanged except for adding
`segment_id`.

The sidecar emits a second row with:

- `event`: `whisperx_alignment`
- `segment_id`
- `is_final`: `true`
- `source_start`
- `source_end`
- `source_text`
- `whisperx_transcript`

`whisperx_transcript` must follow a bounded WhisperX-style shape:

```json
{
  "model": "whisperx_alignment",
  "language": "en",
  "segments": [
    {
      "start": 0.0,
      "end": 1.2,
      "text": "example text",
      "confidence": 0.93,
      "words": [
        {
          "start": 0.0,
          "end": 0.4,
          "word": "example",
          "confidence": 0.95
        }
      ]
    }
  ]
}
```

This keeps the sidecar output close to the existing
`SensibLaw/src/sensiblaw/ingest/whisperx_adapter.py` expectations without
forcing SimulStreaming itself to adopt the full WhisperX transcript as its
primary output.

## Non-Goals

- Do not replace `SimulWhisperASR`.
- Do not block partial-output emission on WhisperX.
- Do not add semantic labels beyond timestamped transcript alignment.
- Do not require diarization in the first slice.

## Initial Implementation Slice

1. Add a reusable WhisperX sidecar processor inside `SimulStreaming/`.
2. Thread it through file simulation in synchronous mode.
3. Thread it through server mode in asynchronous mode.
4. Add focused unit tests for segment buffering and async drain behavior.
