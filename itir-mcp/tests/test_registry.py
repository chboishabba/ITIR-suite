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
        "itir.markdown.render_projection",
        "itir.markdown.write_projection",
        "itir.docstore.config_plan",
    }
