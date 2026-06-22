from itir_mcp import build_default_registry


def test_default_registry_lists_expected_tools() -> None:
    registry = build_default_registry()
    names = {tool.name for tool in registry.list_tools()}
    assert names == {
        "itir.build_envelope",
        "itir.compare_observations",
        "itir.score_coherence",
        "sensiblaw.itir_job_status",
        "sensiblaw.obligations_query",
        "sensiblaw.obligations_explain",
        "sensiblaw.obligations_alignment",
        "sensiblaw.obligations_projection",
        "sensiblaw.obligations_activate",
        "itir.docstore.status",
        "itir.docstore.open_questions",
        "itir.obsidian.vault_scan",
        "itir.docstore.proposal_receipt",
        "itir.pnf.context_index",
        "itir.pnf.task_memory_preview",
        "itir.pnf.observer_evidence",
        "itir.markdown.render_projection",
        "itir.markdown.write_projection",
        "itir.docstore.config_plan",
        "itir.governance.tool_profiles",
        "itir.governance.validate_tool_profile",
        "itir.wikidata.tooling_profile",
        "itir.wikidata.review_packet",
        "itir.wikiproject.tooling_profile",
        "itir.zelph.transport_boundary",
        "itir.zelph.partial_closure",
        "itir.shard.validate_artifact",
        "itir.shard.route_selector",
        "itir.shard.partial_graph_view",
    }


def test_default_registry_exposes_stable_authority_profiles_for_governance_and_shards() -> None:
    registry = build_default_registry()
    expected_tools = {
        "itir.governance.tool_profiles",
        "itir.governance.validate_tool_profile",
        "itir.wikidata.tooling_profile",
        "itir.wikidata.review_packet",
        "itir.wikiproject.tooling_profile",
        "itir.zelph.transport_boundary",
        "itir.zelph.partial_closure",
        "itir.shard.validate_artifact",
        "itir.shard.route_selector",
        "itir.shard.partial_graph_view",
    }

    assert set(registry.list_tool_authority_profiles()) == expected_tools

    for tool_name in expected_tools:
        spec = registry.get_tool_spec(tool_name)
        assert spec is not None
        assert getattr(spec, "authority_profile_key", None) == tool_name

        profile_key = registry.get_tool_authority_profile_key(tool_name)
        profile = registry.get_tool_authority_profile(tool_name)

        assert profile_key == tool_name
        assert profile is not None
        assert profile["tool_id"] == tool_name
        assert getattr(spec, "authority_profile", None) == profile
