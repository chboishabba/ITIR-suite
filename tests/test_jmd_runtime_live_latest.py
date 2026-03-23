from __future__ import annotations

import os

import pytest

from itir_jmd_bridge.runtime import ingest_latest_pastes


@pytest.mark.skipif(
    os.environ.get("JMD_LIVE_LATEST") != "1",
    reason="set JMD_LIVE_LATEST=1 to run live latest-post ingest checks",
)
def test_live_latest_post_ingest_smoke() -> None:
    base_url = os.environ.get("JMD_LIVE_BASE_URL", "https://pastebin.xware.online")
    limit = int(os.environ.get("JMD_LIVE_LIMIT", "3"))
    verify_ipfs = os.environ.get("JMD_LIVE_VERIFY_IPFS", "0") == "1"

    payload = ingest_latest_pastes(
        base_url=base_url,
        limit=limit,
        verify_ipfs=verify_ipfs,
    )

    assert payload["resolved_count"] == limit
    assert len(payload["results"]) == limit
