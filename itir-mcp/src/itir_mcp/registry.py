from __future__ import annotations

from typing import Any, Callable, Mapping

from .autonomous_orchestrator_tools import get_autonomous_orchestrator_tools
from .chatgpt_worker_tools import get_chatgpt_worker_tools
from .tmux_observation_tools import get_tmux_observation_tools
from .tui_state_tools import get_tui_state_tools
from .config_tools import get_config_tools
from .comparison_tools import get_comparison_tools
from .contracts import JsonDict, ToolError, ToolExecutionError, ToolHandler, ToolSpec, error_payload, success_payload
from .docstore_tools import get_docstore_tools
from .export_tools import get_export_tools
from .frontier_tools import get_frontier_tools
from .formal_tools import get_formal_tools
from .formal_receipt_store import default_receipt_store
from .guardrails import safe_tool_call
from .governance_tools import get_governance_tools
from .promotion_tools import get_promotion_tools
from .pnf_tools import get_pnf_tools
from .sensiblaw_tools import get_sensiblaw_tools
from .spectral_plot_tools import get_spectral_plot_tools
from .tool_authority_profiles import DEFAULT_REGISTRY_TOOL_AUTHORITY_PROFILES, validate_tool_authority_profile
from .wikidata_disjointness_tool import get_wikidata_disjointness_tools


class ToolRegistry:
    """Simple in-process registry for namespaced suite tools."""

    def __init__(self) -> None:
        self._tools: dict[str, tuple[ToolSpec, ToolHandler, str | None, JsonDict | None]] = {}

    def register(
        self,
        spec: ToolSpec,
        handler: ToolHandler,
        *,
        authority_profile_key: str | None = None,
        authority_profile: Mapping[str, Any] | None = None,
    ) -> None:
        profile_key = authority_profile_key
        profile: JsonDict | None = None
        if authority_profile is not None:
            profile = validate_tool_authority_profile(authority_profile)
            profile_key = profile_key or str(profile["tool_id"])
        if profile_key is not None:
            object.__setattr__(spec, "authority_profile_key", profile_key)
        if profile is not None:
            object.__setattr__(spec, "authority_profile", profile)
        self._tools[spec.name] = (spec, handler, profile_key, profile)

    def list_tools(self) -> list[ToolSpec]:
        return [spec for spec, _, _, _ in self._tools.values()]

    def get_tool_spec(self, name: str) -> ToolSpec | None:
        tool = self._tools.get(name)
        if tool is None:
            return None
        return tool[0]

    def get_tool_authority_profile_key(self, name: str) -> str | None:
        tool = self._tools.get(name)
        if tool is None:
            return None
        return tool[2]

    def get_tool_authority_profile(self, name: str) -> JsonDict | None:
        tool = self._tools.get(name)
        if tool is None:
            return None
        return tool[3]

    def list_tool_authority_profiles(self) -> dict[str, JsonDict]:
        return {name: profile for name, (_, _, _, profile) in self._tools.items() if profile is not None}

    def invoke(self, name: str, payload: Mapping[str, Any]) -> JsonDict:
        try:
            _, handler, _, _ = self._tools[name]
        except KeyError:
            return error_payload(ToolError(f"Unknown tool: {name}"))
        try:
            return success_payload(handler(payload))
        except ToolError as exc:
            return error_payload(exc)
        except Exception as exc:
            return error_payload(ToolExecutionError(str(exc), details={"tool": name}))

    def safe_invoke(self, name: str, payload: Mapping[str, Any]) -> JsonDict:
        try:
            return success_payload(safe_tool_call(self, name, payload))
        except ToolError as exc:
            return error_payload(exc)
        except Exception as exc:
            return error_payload(ToolExecutionError(str(exc), details={"tool": name}))


def build_default_registry(
    *, local_referee_context: Callable[[], Mapping[str, Any]] | None = None,
) -> ToolRegistry:
    registry = ToolRegistry()
    for spec, handler in get_tui_state_tools():
        registry.register(spec, handler)
    for spec, handler in get_tmux_observation_tools():
        registry.register(spec, handler)
    for spec, handler in get_chatgpt_worker_tools():
        registry.register(spec, handler)
    for spec, handler in get_sensiblaw_tools():
        registry.register(spec, handler)
    for spec, handler in get_comparison_tools():
        registry.register(spec, handler)
    for spec, handler in get_docstore_tools():
        registry.register(spec, handler)
    for spec, handler in get_promotion_tools():
        registry.register(spec, handler)
    for spec, handler in get_pnf_tools():
        registry.register(spec, handler)
    for spec, handler in get_export_tools():
        registry.register(spec, handler)
    for spec, handler in get_config_tools():
        registry.register(spec, handler)
    for spec, handler in get_spectral_plot_tools():
        registry.register(
            spec,
            handler,
            authority_profile_key=spec.name if spec.name in DEFAULT_REGISTRY_TOOL_AUTHORITY_PROFILES else None,
            authority_profile=DEFAULT_REGISTRY_TOOL_AUTHORITY_PROFILES.get(spec.name),
        )
    for spec, handler in get_governance_tools():
        registry.register(
            spec,
            handler,
            authority_profile_key=spec.name if spec.name in DEFAULT_REGISTRY_TOOL_AUTHORITY_PROFILES else None,
            authority_profile=DEFAULT_REGISTRY_TOOL_AUTHORITY_PROFILES.get(spec.name),
        )
    def write_referee_receipt(result: Mapping[str, Any], trusted: Mapping[str, Any]) -> bool:
        binding = result["reference_binding"]
        return default_receipt_store().record_from_referee(
            binding["repo"], binding["sha"], binding["path"],
            binding["canonical_thread_id"], result, referee_verified=True,
        )

    for spec, handler in get_formal_tools(
        referee_context=local_referee_context,
        verified_receipt_writer=write_referee_receipt if local_referee_context is not None else None,
    ):
        registry.register(spec, handler)
    for spec, handler in get_frontier_tools():
        registry.register(spec, handler)
    for spec, handler in get_autonomous_orchestrator_tools():
        registry.register(spec, handler)
    for spec, handler in get_wikidata_disjointness_tools():
        registry.register(spec, handler)
    return registry
