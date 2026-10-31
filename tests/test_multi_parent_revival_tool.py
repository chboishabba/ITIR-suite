from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "itir-mcp" / "src"))

from itir_mcp.chatgpt_worker_tools import get_chatgpt_worker_tools, revive_multi
from itir_mcp.contracts import ToolInputError


class FakeAPI:
    def __init__(self):
        self.calls = []

    def chatgpt_revive_multi(self, **kwargs):
        self.calls.append(kwargs)
        return {"state": "complete", "child_conversation_id": "child",
                "attachment_receipt": {"operation_id": "op-1"}}


class MultiParentToolTests(unittest.TestCase):
    def test_worker_tool_delegates_exact_explicit_artifact_and_parent_ids(self):
        api = FakeAPI()
        payload = {"parent_thread_ids": ["canonical-a", "canonical-b"],
                   "handoff_path": "/owned/output/handoff.json",
                   "prompt": "continue", "follow": False}
        with patch("itir_mcp.chatgpt_worker_tools._worker_api", return_value=api):
            result = revive_multi(payload)
        self.assertEqual(result["operation"]["child_conversation_id"], "child")
        self.assertEqual(api.calls[0]["parent_thread_ids"], payload["parent_thread_ids"])
        self.assertEqual(api.calls[0]["handoff_path"], payload["handoff_path"])
        self.assertEqual(api.calls[0]["follow"], False)

    def test_rejects_parent_count_duplicates_and_unknown_fields(self):
        with self.assertRaises(ToolInputError):
            revive_multi({"parent_thread_ids": ["only"], "handoff_path": "/x",
                          "prompt": "continue"})
        with self.assertRaises(ToolInputError):
            revive_multi({"parent_thread_ids": ["same", "same"], "handoff_path": "/x",
                          "prompt": "continue"})
        with self.assertRaises(ToolInputError):
            revive_multi({"parent_thread_ids": ["a", "b"], "handoff_path": "/x",
                          "prompt": "continue", "unexpected": True})

    def test_tool_is_registered_as_mutating_not_read_only(self):
        specs = {spec.name: spec for spec, _handler in get_chatgpt_worker_tools()}
        self.assertIn("itir.chatgpt.revive_multi", specs)
        self.assertFalse(specs["itir.chatgpt.revive_multi"].read_only)


if __name__ == "__main__":
    unittest.main()
