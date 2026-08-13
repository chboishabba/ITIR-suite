# Context Envelope JSON Schema (Draft)

This schema defines the minimal, required context envelope for any artifact
stored or rendered in the ITIR suite.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://itir-suite.local/schema/context-envelope.json",
  "title": "ContextEnvelope",
  "type": "object",
  "required": [
    "artifact_id",
    "temporal",
    "venue",
    "epistemic_state",
    "role_power",
    "provenance"
  ],
  "properties": {
    "artifact_id": {
      "type": "string",
      "description": "Stable identifier for the referenced artifact."
    },
    "temporal": {
      "type": "object",
      "required": ["created_at", "sequence_index"],
      "properties": {
        "created_at": { "type": "string", "format": "date-time" },
        "duration_ms": { "type": "integer", "minimum": 0 },
        "sequence_index": {
          "type": "integer",
          "minimum": 0,
          "description": "Position relative to other artifacts in the same thread."
        },
        "sequence_group_id": {
          "type": "string",
          "description": "Optional grouping key for ordered artifacts."
        }
      }
    },
    "venue": {
      "type": "object",
      "required": ["medium", "intended_audience", "visibility_scope"],
      "properties": {
        "medium": { "type": "string" },
        "intended_audience": { "type": "string" },
        "visibility_scope": {
          "type": "string",
          "enum": ["private", "restricted", "public", "unknown"]
        }
      }
    },
    "epistemic_state": {
      "type": "object",
      "required": ["known_then", "known_now", "legal_status_then", "investigative_status_then"],
      "properties": {
        "known_then": { "type": "array", "items": { "type": "string" } },
        "known_now": { "type": "array", "items": { "type": "string" } },
        "legal_status_then": { "type": "string" },
        "investigative_status_then": { "type": "string" },
        "later_discovered": { "type": "array", "items": { "type": "string" } }
      }
    },
    "role_power": {
      "type": "object",
      "required": ["speaker_role", "recipient_role"],
      "properties": {
        "speaker_role": { "type": "string" },
        "recipient_role": { "type": "string" },
        "institutional_asymmetry": {
          "type": "string",
          "enum": ["none", "low", "medium", "high", "unknown"]
        },
        "status_flags": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "provenance": {
      "type": "object",
      "required": ["source_id", "revision_id", "text_spans"],
      "properties": {
        "source_id": { "type": "string" },
        "revision_id": { "type": "string" },
        "text_spans": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["start_char", "end_char"],
            "properties": {
              "start_char": { "type": "integer", "minimum": 0 },
              "end_char": { "type": "integer", "minimum": 0 }
            }
          }
        }
      }
    }
  }
}
```

Notes:
- This schema enforces a minimum envelope; product-specific extensions are
  allowed but must preserve all required fields.
- The envelope is required for rendering, export, or cross-reference.

## Validation Notes (Implementation Guidance)
- Use a JSON Schema validator compatible with draft 2020-12.
- Validate all fixtures in `docs/planning/context_envelope_fixtures.json` as
  part of CI or pre-commit checks.
- Enforce a hard failure when required fields are missing; warnings are not
  sufficient for context invariants.
