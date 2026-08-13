from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TransportPlugin(ABC):
    """Transport boundary for JMD runtime publication.

    The first executable slice remains pull-based, but publication and handoff
    should still go through a plugin seam rather than being hard-coded into the
    runtime builder.
    """

    @abstractmethod
    def publish(self, *, runtime_receipt: dict[str, Any], runtime_graph: dict[str, Any] | None = None) -> dict[str, Any]:
        raise NotImplementedError


class NullTransportPlugin(TransportPlugin):
    """No-op transport used for local runs and tests."""

    def publish(self, *, runtime_receipt: dict[str, Any], runtime_graph: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "transport": "null",
            "status": "skipped",
            "receipt_id": runtime_receipt["receipt_id"],
            "graph_id": runtime_graph.get("graph_id") if runtime_graph is not None else None,
        }


def publish_bundle(
    *,
    plugin: TransportPlugin,
    runtime_receipt: dict[str, Any],
    runtime_graph: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return plugin.publish(runtime_receipt=runtime_receipt, runtime_graph=runtime_graph)
