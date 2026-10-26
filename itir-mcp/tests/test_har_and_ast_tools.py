"""Tests for HAR analysis and JavaScript AST deobfuscation MCP tools."""

from __future__ import annotations

import json
import unittest

from itir_mcp.ast_deobfuscator_tools import analyze_bundle
from itir_mcp.har_tools import har_diff, har_inspect, har_token_lineage
from itir_mcp.registry import build_default_registry


SAMPLE_HAR = {
    "log": {
        "version": "1.2",
        "creator": {"name": "TestBrowser", "version": "1.0"},
        "entries": [
            {
                "startedDateTime": "2026-10-26T12:00:00.000Z",
                "time": 45.2,
                "request": {
                    "method": "POST",
                    "url": "https://chatgpt.com/backend-api/sentinel/chat-requirements",
                    "headers": [
                        {"name": "Content-Type", "value": "application/json"},
                        {"name": "User-Agent", "value": "Mozilla/5.0"},
                    ],
                    "queryString": [],
                    "cookies": [
                        {"name": "cf_clearance", "value": "cf-12345"},
                        {"name": "oai-did", "value": "device-abc"},
                    ],
                    "postData": {"mimeType": "application/json", "text": '{"dx": "turnstile-dx-secret-999"}'},
                },
                "response": {
                    "status": 200,
                    "statusText": "OK",
                    "headers": [
                        {"name": "Content-Type", "value": "application/json"},
                        {"name": "Set-Cookie", "value": "oai-sc=secret-cookie-777; Path=/; Secure"},
                    ],
                    "cookies": [{"name": "oai-sc", "value": "secret-cookie-777"}],
                    "content": {
                        "mimeType": "application/json",
                        "text": json.dumps({
                            "token": "sentinel-token-xyz-123",
                            "persona": "chatgpt-paid",
                            "expire_after": 540,
                        }),
                    },
                },
            },
            {
                "startedDateTime": "2026-10-26T12:00:01.000Z",
                "time": 82.5,
                "request": {
                    "method": "POST",
                    "url": "https://chatgpt.com/backend-api/conversation",
                    "headers": [
                        {"name": "Content-Type", "value": "application/json"},
                        {"name": "openai-sentinel-chat-requirements-token", "value": "sentinel-token-xyz-123"},
                        {"name": "openai-sentinel-turnstile-token", "value": "turnstile-token-888"},
                        {"name": "User-Agent", "value": "Mozilla/5.0"},
                    ],
                    "queryString": [],
                    "cookies": [
                        {"name": "cf_clearance", "value": "cf-12345"},
                        {"name": "oai-did", "value": "device-abc"},
                        {"name": "oai-sc", "value": "secret-cookie-777"},
                    ],
                    "postData": {
                        "mimeType": "application/json",
                        "text": json.dumps({
                            "action": "next",
                            "messages": [{"content": {"parts": ["Hello world"]}}],
                            "parent_message_id": "root",
                        }),
                    },
                },
                "response": {
                    "status": 200,
                    "statusText": "OK",
                    "headers": [{"name": "Content-Type", "value": "text/event-stream"}],
                    "cookies": [],
                    "content": {"mimeType": "text/event-stream", "text": "data: [DONE]\n\n"},
                },
            },
        ],
    }
}


SAMPLE_JS_CODE = """
async function dispatchConversation(prompt, requirements) {
    const token = requirements.token;
    const turnstile = window.turnstile ? window.turnstile.getResponse() : null;
    const now = performance.now();
    const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(token));
    
    return fetch("/backend-api/conversation", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "openai-sentinel-chat-requirements-token": token,
            "openai-sentinel-turnstile-token": turnstile,
        },
        body: JSON.stringify({ prompt, timestamp: now })
    });
}
"""

SAMPLE_HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script>
    <script>
        window.addEventListener("message", async (evt) => {
            const requirements = await fetch("/sentinel/chat-requirements", { method: "POST" });
            const data = await requirements.json();
            window.parent.postMessage({ token: data.token }, "*");
        });
    </script>
</head>
<body></body>
</html>
"""


class TestHarTools(unittest.TestCase):
    def test_har_inspect_in_memory(self):
        res = har_inspect({"har_data": SAMPLE_HAR})
        self.assertEqual(res["total_entries"], 2)
        self.assertEqual(res["matched_entries"], 2)
        flows = res["flows"]
        self.assertEqual(len(flows), 2)
        self.assertEqual(flows[0]["method"], "POST")
        self.assertEqual(flows[0]["path"], "/backend-api/sentinel/chat-requirements")
        self.assertEqual(flows[0]["status"], 200)
        self.assertEqual(flows[0]["response_body"]["token"], "sentinel-token-xyz-123")
        self.assertEqual(flows[1]["path"], "/backend-api/conversation")

    def test_har_inspect_filter(self):
        res = har_inspect({"har_data": SAMPLE_HAR, "url_filter": "conversation"})
        self.assertEqual(res["matched_entries"], 1)
        self.assertEqual(res["flows"][0]["path"], "/backend-api/conversation")

    def test_har_diff_flows(self):
        res = har_diff({"har_data": SAMPLE_HAR, "index_a": 0, "index_b": 1})
        self.assertTrue(res["matches"]["method"])
        self.assertFalse(res["matches"]["path"])
        self.assertTrue(res["matches"]["status"])
        headers = res["headers"]
        self.assertIn("openai-sentinel-chat-requirements-token", headers["missing_in_a"])
        cookies = res["cookies"]
        self.assertIn("oai-sc", cookies["missing_in_a"])

    def test_har_token_lineage(self):
        res = har_token_lineage({"har_data": SAMPLE_HAR, "token": "sentinel-token-xyz-123"})
        self.assertEqual(res["total_occurrences"], 2)
        origin = res["origin"]
        self.assertIsNotNone(origin)
        self.assertEqual(origin["entry_index"], 0)
        self.assertEqual(origin["direction"], "incoming")
        self.assertEqual(origin["channel"], "response_body")
        self.assertEqual(origin["key_path"], "token")

        summary = res["summary"]
        self.assertEqual(summary["times_transmitted"], 1)
        self.assertEqual(summary["last_transmitted_index"], 1)

        # Lineage entry 1 was transmitted in outgoing request_header
        lineage = res["lineage"]
        self.assertEqual(lineage[1]["direction"], "outgoing")
        self.assertEqual(lineage[1]["channel"], "request_header")
        self.assertEqual(lineage[1]["key_path"], "openai-sentinel-chat-requirements-token")

    def test_har_token_lineage_cookie(self):
        res = har_token_lineage({"har_data": SAMPLE_HAR, "token": "secret-cookie-777"})
        self.assertGreaterEqual(res["total_occurrences"], 2)
        origin = res["origin"]
        self.assertEqual(origin["entry_index"], 0)
        self.assertEqual(origin["direction"], "incoming")


class TestAstDeobfuscatorTools(unittest.TestCase):
    def test_analyze_bundle_js(self):
        res = analyze_bundle({"code": SAMPLE_JS_CODE, "target_endpoints": ["/backend-api/conversation"]})
        self.assertEqual(res["summary"]["total_endpoints_referenced"], 1)
        endpoint_ref = res["endpoint_references"][0]
        self.assertEqual(endpoint_ref["endpoint"], "/backend-api/conversation")
        self.assertTrue(endpoint_ref["is_call_site"])

        telemetry = res["telemetry_detections"]
        self.assertIn("crypto_subtle", telemetry)
        self.assertIn("timing_check", telemetry)

        dep_classes = res["summary"]["preflight_dependency_properties"]
        self.assertIn("chat_requirements_token", dep_classes)
        self.assertIn("turnstile_dx", dep_classes)
        self.assertIn("header_sentinel_chat", dep_classes)
        self.assertIn("header_sentinel_turnstile", dep_classes)

    def test_analyze_bundle_html(self):
        res = analyze_bundle({"code": SAMPLE_HTML_CODE})
        self.assertTrue(res["is_html"])
        self.assertGreaterEqual(res["html_script_tags"], 1)
        self.assertEqual(res["summary"]["total_endpoints_referenced"], 1)
        self.assertIn("post_message", res["telemetry_detections"])

    def test_registry_integration(self):
        registry = build_default_registry()
        for expected in ["itir.har.inspect", "itir.har.diff", "itir.har.token_lineage", "itir.ast.analyze_bundle"]:
            spec = registry.get_tool_spec(expected)
            self.assertIsNotNone(spec, f"Tool {expected} not registered")
            self.assertTrue(spec.read_only)


if __name__ == "__main__":
    unittest.main()
