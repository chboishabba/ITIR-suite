from itir_mcp import build_default_registry


def _sample_observation(**overrides):
    payload = {
        "obs_id": "obs-1",
        "source_family": "worldmonitor",
        "source_system": "worldmonitor",
        "source_scope": "external",
        "capture_mode": "news_event",
        "observed_time": "2026-04-06T00:00:00+00:00",
        "text": "Explosion reported near Odesa port after overnight drone attack",
        "geometry": {"lat": 46.48, "lon": 30.72},
        "anchor_refs": {"source_id": "wm:1"},
        "provenance": {"source": "fixture"},
    }
    payload.update(overrides)
    return payload


def test_compare_observations_returns_deterministic_payload() -> None:
    registry = build_default_registry()
    result = registry.invoke(
        "itir.compare_observations",
        {
            "left": _sample_observation(),
            "right": _sample_observation(
                obs_id="obs-2",
                source_family="openrecall",
                source_system="openrecall",
                source_scope="internal",
                capture_mode="screen_capture",
                observed_time="2026-04-06T00:30:00+00:00",
                text="Odesa port explosion noted after overnight drone strike",
                anchor_refs={"source_id": "or:1"},
            ),
        },
    )
    assert result["ok"] is True
    payload = result["result"]
    assert payload["version"] == "itir.compare_observations.v1"
    assert payload["similarity"] >= 0.4
    assert payload["signals"]["text_overlap"] > 0
    assert payload["left"]["source_system"] == "worldmonitor"
    assert payload["right"]["source_system"] == "openrecall"


def test_score_coherence_reports_weakest_pair() -> None:
    registry = build_default_registry()
    result = registry.invoke(
        "itir.score_coherence",
        {
            "observations": [
                _sample_observation(),
                _sample_observation(obs_id="obs-2", text="Explosion reported near Odesa port"),
                _sample_observation(
                    obs_id="obs-3",
                    text="Chip stocks rally after earnings guidance",
                    geometry={"lat": 37.77, "lon": -122.41},
                ),
            ]
        },
    )
    assert result["ok"] is True
    payload = result["result"]
    assert payload["version"] == "itir.score_coherence.v1"
    assert payload["comparison_count"] == 3
    assert payload["weakest_pair"] is not None


def test_build_envelope_wraps_transport_safe_payload() -> None:
    registry = build_default_registry()
    result = registry.invoke(
        "itir.build_envelope",
        {
            "left": _sample_observation(),
            "right": _sample_observation(obs_id="obs-2", source_system="openrecall"),
        },
    )
    assert result["ok"] is True
    payload = result["result"]
    assert payload["version"] == "itir.build_envelope.v1"
    assert payload["envelope_type"] == "itir.observation_comparison.v1"
    assert payload["meta"]["generated_by"] == "itir.compare_observations"
