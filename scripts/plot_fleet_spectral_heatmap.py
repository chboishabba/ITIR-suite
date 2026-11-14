#!/usr/bin/env python3
"""Generate high-resolution XY scatter plot and domain cosine heatmap for the Fleet corpus.

Uses the real PNF relational frames and sheaf hyperfabric embeddings.
Renders:
  - docs/fleet/fleet_corpus_spectral_scatter.png
  - docs/fleet/fleet_domain_spectral_heatmap.png
  - docs/fleet/fleet_spectral_visual_summary.json
"""

from __future__ import annotations

import collections
import json
import math
from pathlib import Path
import struct
import sys
import time

# Repo root paths
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "itir-mcp" / "src"))
sys.path.insert(0, str(REPO_ROOT / "reverse-engineered-chatgpt"))
sys.path.insert(0, str(REPO_ROOT / "SensibLaw"))
sys.path.insert(0, str(REPO_ROOT / "SensibLaw" / "src"))
sys.path.insert(0, str(REPO_ROOT / "StatiBaker"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from re_gpt.gap_comparator import (
    DEFAULT_WORLD_DIR,
    FRAGMENT_NAMES,
    SHAPE_NAMES,
    ExactGapComparator,
)
from itir_mcp.pnf_spectral_packet import (
    extract_relational_frames,
    spectral_no_typed_meet,
    _cosine_similarity,
    _default_lane_embedding,
)


def extract_real_corpus_multisets() -> tuple[list[dict[str, float]], list[str]]:
    """Extract relational-frame factor multisets from the .slrw world store and repo docs."""
    slrw_path = DEFAULT_WORLD_DIR / "fleet_top500_iter1.slrw"
    raw_slots_by_thread: dict[str, list[dict]] = collections.defaultdict(list)

    if slrw_path.exists():
        print(f"Streaming PNF slots from {slrw_path} ({slrw_path.stat().st_size / 1e6:.1f} MB)...")
        with open(slrw_path, "rb") as f:
            while True:
                magic = f.read(4)
                if not magic or magic != b"SLRW":
                    break
                _ver = struct.unpack("<H", f.read(2))[0]
                header = f.read(2)
                kind_u8 = header[0]
                id_len, aux_len, payload_len = struct.unpack("<III", f.read(12))
                _iteration = struct.unpack("<q", f.read(8))[0]
                rec_id = f.read(id_len).decode("utf-8", errors="replace")
                aux = f.read(aux_len).decode("utf-8", errors="replace") if aux_len else ""
                payload = f.read(payload_len)

                if kind_u8 == 2 and payload.startswith(b"PNF1"):
                    frag_u8 = payload[4]
                    shape_u8 = payload[5]
                    try:
                        sent_id, l_ord, h_ord, s_chr, e_chr = struct.unpack("<IIIII", payload[6:26])
                        pos = 32
                        olen = struct.unpack("<I", payload[pos : pos + 4])[0]
                        pos += 4 + olen
                        llen = struct.unpack("<I", payload[pos : pos + 4])[0]
                        pos += 4
                        slot_lemma = payload[pos : pos + llen].decode("utf-8", errors="replace")
                        pos += llen
                        holen = struct.unpack("<I", payload[pos : pos + 4])[0]
                        pos += 4 + holen
                        hllen = struct.unpack("<I", payload[pos : pos + 4])[0]
                        pos += 4
                        head_lemma = payload[pos : pos + hllen].decode("utf-8", errors="replace")

                        cid = aux[:36] if aux else rec_id[:36]
                        if cid and head_lemma and slot_lemma:
                            is_boundary = slot_lemma.lower() in {"you", "i", "we", "to", "not", "be"}
                            b_kind = "dialogue_deictic" if slot_lemma.lower() in {"you", "i", "we"} else (
                                "auxiliary" if slot_lemma.lower() in {"to", "not", "be"} else ""
                            )
                            raw_slots_by_thread[cid].append({
                                "slot_id": f"s_{len(raw_slots_by_thread[cid])}",
                                "sentence_id": f"sent_{sent_id}",
                                "head_ordinal": h_ord,
                                "head_lemma": head_lemma.lower(),
                                "lemma": slot_lemma.lower(),
                                "argument_role": FRAGMENT_NAMES.get(frag_u8, "arg"),
                                "is_boundary": is_boundary,
                                "boundary_kind": b_kind,
                            })
                    except Exception:
                        continue

    print(f"Loaded raw slots across {len(raw_slots_by_thread)} threads.")

    # Convert to relational frames and multiset features
    thread_multisets: list[dict[str, float]] = []
    thread_ids: list[str] = []

    for cid, slots in raw_slots_by_thread.items():
        if not slots:
            continue
        try:
            frames = extract_relational_frames(slots)
        except Exception:
            continue
        features = collections.Counter()
        for frame in frames:
            pred = frame["predicate"]
            features[f"predicate:{pred}"] += 1
            for role, args in frame["arguments"].items():
                for arg in args:
                    features[f"edge:{pred}:{role}:{arg}"] += 1
                    features[f"concept:{arg}"] += 0.5
        if features:
            thread_multisets.append(dict(features))
            thread_ids.append(cid)

    # Ingest repo docs
    comp = ExactGapComparator()
    doc_paths = [
        REPO_ROOT / "ROADMAP.md",
        REPO_ROOT.parent / "COMPACTIFIED_CONTEXT.md",
        REPO_ROOT / "docs" / "adr" / "ADR_014_crisis_advocacy_module_cam_20260208.md",
        REPO_ROOT / "docs" / "adr" / "ADR_contextual_fields_non_authoritative.md",
        REPO_ROOT / "SensibLaw" / "docs" / "ADR_LAYER3_SPAN_CONTRACT.md",
        REPO_ROOT / "SensibLaw" / "docs" / "regex_semantic_policy.md",
        REPO_ROOT / "docs" / "fleet" / "topical_pnf_world_model_convergence_20261027.md",
    ]
    for p in doc_paths:
        if p.exists():
            doc_cnt = comp.extract_formal_multiset(p)
            doc_feats = {f"doc_concept:{k}": float(v) for k, v in doc_cnt.items()}
            if doc_feats:
                thread_multisets.append(doc_feats)
                thread_ids.append(p.name)

    print(f"Extracted {len(thread_multisets)} total entities for spectral decomposition.")
    return thread_multisets, thread_ids


def main() -> None:
    t0 = time.perf_counter()
    out_dir = REPO_ROOT / "docs" / "fleet"
    out_dir.mkdir(parents=True, exist_ok=True)

    multisets, ids = extract_real_corpus_multisets()
    if not multisets:
        print("No multisets extracted. Aborting.")
        return

    # Keep top 1200 factors to avoid dense Jacobi memory blowout
    global_factor_counts = collections.Counter()
    for m in multisets:
        for k, v in m.items():
            global_factor_counts[k] += v

    top_factors = {k for k, _ in global_factor_counts.most_common(1200)}
    pruned_multisets = [
        {k: v for k, v in m.items() if k in top_factors}
        for m in multisets
    ]
    # Filter out empty rows
    valid_data = [(cid, m) for cid, m in zip(ids, pruned_multisets) if m]
    pruned_ids = [cid for cid, _ in valid_data]
    pruned_multisets = [m for _, m in valid_data]

    print(f"Running SVD across {len(pruned_multisets)} entities with {len(top_factors)} factors...")
    factor_list = sorted(top_factors)
    factor_to_idx = {f: idx for idx, f in enumerate(factor_list)}
    X = np.zeros((len(pruned_multisets), len(factor_list)), dtype=np.float64)
    for row_idx, m in enumerate(pruned_multisets):
        for f, val in m.items():
            col_idx = factor_to_idx.get(f)
            if col_idx is not None:
                X[row_idx, col_idx] = val

    mean = np.mean(X, axis=0)
    centered = X - mean

    U, s_vals_arr, Vt = np.linalg.svd(centered, full_matrices=False)
    s_vals = [float(v) for v in s_vals_arr[:8]]

    n_threads, n_factors = X.shape
    variances = np.var(centered, axis=0)
    sigma2 = float(np.median(variances))
    gamma = n_factors / n_threads
    lambda_plus = float(sigma2 * (1.0 + np.sqrt(gamma)) ** 2)
    macro_count = int(np.sum(s_vals_arr > np.sqrt(lambda_plus * n_threads)))

    mp = {
        "sigma_squared": sigma2,
        "gamma": gamma,
        "lambda_plus": lambda_plus,
        "macroscopic_component_count": macro_count,
    }
    print(f"Singular values: {[round(v, 2) for v in s_vals]}")
    print(f"Marchenko-Pastur lambda_plus: {mp['lambda_plus']:.2f} (Macro count: {mp['macroscopic_component_count']})")

    # Extract XY coordinates
    thread_coords = U * s_vals_arr
    x_coords = thread_coords[:, 0].tolist()
    y_coords = thread_coords[:, 1].tolist()

    components = []
    for k in range(min(5, len(s_vals))):
        v = Vt[k]
        top_idx = np.argsort(np.abs(v))[::-1][:3]
        motif_name = " · ".join(factor_list[i] for i in top_idx)
        components.append({"index": k, "motif_name": motif_name, "singular_value": float(s_vals[k])})

    coords = {
        "singular_values": s_vals,
        "marchenko_pastur": mp,
        "components": components,
    }

    # 1. RENDER XY SCATTER PLOT
    plt.figure(figsize=(12, 8), dpi=150)
    plt.style.use("tableau-colorblind10") if "tableau-colorblind10" in plt.style.available else None

    # Density / scatter
    scatter = plt.scatter(
        x_coords,
        y_coords,
        c=np.sqrt(np.array(x_coords)**2 + np.array(y_coords)**2),
        cmap="viridis",
        alpha=0.65,
        edgecolors="none",
        s=35,
    )
    plt.colorbar(scatter, label="Spectral Radial Distance $\\sqrt{x^2 + y^2}$")

    # Highlight top eigen axes
    plt.axhline(0, color="grey", linestyle="--", alpha=0.4, linewidth=0.8)
    plt.axvline(0, color="grey", linestyle="--", alpha=0.4, linewidth=0.8)

    motif_0 = coords["components"][0]["motif_name"][:45] if coords["components"] else "Macro Eigen 0"
    motif_1 = coords["components"][1]["motif_name"][:45] if len(coords["components"]) > 1 else "Macro Eigen 1"

    plt.xlabel(f"Macro Eigen 0 (λ = {s_vals[0]:.1f}) — [{motif_0}]", fontsize=11, fontweight="bold")
    plt.ylabel(f"Macro Eigen 1 (λ = {s_vals[1]:.1f}) — [{motif_1}]", fontsize=11, fontweight="bold")
    plt.title(
        f"Fleet 1,000-Corpus PNF Spectral Field (N={len(x_coords)} entities)\n"
        f"Marchenko-Pastur Bulk Threshold $\\lambda_+ = {mp['lambda_plus']:.2f}$ | Macroscopic Modes: {mp['macroscopic_component_count']}",
        fontsize=13,
        pad=12,
    )

    # Annotate prominent anchor nodes
    for i, cid in enumerate(pruned_ids):
        if i < 8 or "ROADMAP" in cid or "COMPACTIFIED" in cid:
            plt.annotate(
                cid[:18],
                (x_coords[i], y_coords[i]),
                fontsize=8,
                alpha=0.85,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7, ec="grey", lw=0.5),
            )

    plt.grid(True, linestyle=":", alpha=0.4)
    plt.tight_layout()
    scatter_png_path = out_dir / "fleet_corpus_spectral_scatter.png"
    plt.savefig(scatter_png_path, dpi=150)
    plt.close()
    print(f"Saved XY spectral scatter plot to {scatter_png_path}")

    # 2. RENDER 8x8 DOMAIN COSINE HEATMAP VIA REAL WORLD GRAPH SPECTRAL OPERATOR
    graph = {
        "projection_ref": "pnf-follow:fleet-domains:unified-v1",
        "nodes": [
            {"id": "source:ym", "kind": "source_manifestation"},
            {"id": "pnf:ym", "kind": "pnf_candidate"},
            {"id": "atom:ym", "kind": "world_atom"},
            {"id": "source:metrology", "kind": "source_manifestation"},
            {"id": "pnf:metrology", "kind": "pnf_candidate"},
            {"id": "atom:metrology", "kind": "world_atom"},
            {"id": "ontology:gauge", "kind": "external_graph_entity"},
            {"id": "ontology:metric", "kind": "external_graph_entity"},
            {"id": "ontology:curvature", "kind": "external_graph_entity"},
            {"id": "ontology:fisher", "kind": "external_graph_entity"},
            {"id": "ontology:information-geometry", "kind": "external_graph_entity"},
            {"id": "ontology:nv-center", "kind": "external_graph_entity"},
            {"id": "ontology:rg-flow", "kind": "external_graph_entity"},
            {"id": "ontology:two-point", "kind": "external_graph_entity"},
            {"id": "ontology:riemannian", "kind": "external_graph_entity"},
            {"id": "source:slr", "kind": "source_manifestation"},
            {"id": "pnf:slr", "kind": "pnf_candidate"},
            {"id": "atom:sl_world_store", "kind": "world_atom"},
            {"id": "source:sensiblaw", "kind": "source_manifestation"},
            {"id": "pnf:sensiblaw", "kind": "pnf_candidate"},
            {"id": "atom:sensiblaw_projection", "kind": "world_atom"},
            {"id": "ontology:relational_store", "kind": "external_graph_entity"},
            {"id": "source:ns", "kind": "source_manifestation"},
            {"id": "pnf:ns", "kind": "pnf_candidate"},
            {"id": "atom:navier_stokes", "kind": "world_atom"},
            {"id": "ontology:vorticity", "kind": "external_graph_entity"},
            {"id": "source:smii", "kind": "source_manifestation"},
            {"id": "pnf:smii", "kind": "pnf_candidate"},
            {"id": "atom:smii_rom", "kind": "world_atom"},
            {"id": "ontology:elasticity", "kind": "external_graph_entity"},
            {"id": "source:fractran", "kind": "source_manifestation"},
            {"id": "pnf:fractran", "kind": "pnf_candidate"},
            {"id": "atom:fractran", "kind": "world_atom"},
            {"id": "ontology:prime_registers", "kind": "external_graph_entity"},
            {"id": "source:e8", "kind": "source_manifestation"},
            {"id": "pnf:e8", "kind": "pnf_candidate"},
            {"id": "atom:e8_lie", "kind": "world_atom"},
            {"id": "ontology:root_lattice", "kind": "external_graph_entity"},
        ],
        "edges": [
            {"edge_ref": "e_ym1", "relation_kind": "source_to_pnf", "from_node_ref": "source:ym", "to_node_ref": "pnf:ym", "provenance_ref": "slr-world-v2"},
            {"edge_ref": "e_ym2", "relation_kind": "pnf_to_atom", "from_node_ref": "pnf:ym", "to_node_ref": "atom:ym", "provenance_ref": "slr-world-v2"},
            {"edge_ref": "e_ym3", "relation_kind": "external_bridge", "from_node_ref": "atom:ym", "to_node_ref": "ontology:gauge", "provenance_ref": "reviewed-world-bridge"},
            {"edge_ref": "e_ym4", "relation_kind": "external_bridge", "from_node_ref": "atom:ym", "to_node_ref": "ontology:curvature", "provenance_ref": "reviewed-world-bridge"},
            {"edge_ref": "e_ym5", "relation_kind": "external_bridge", "from_node_ref": "atom:ym", "to_node_ref": "ontology:rg-flow", "provenance_ref": "reviewed-world-bridge"},
            {"edge_ref": "e_ym6", "relation_kind": "external_bridge", "from_node_ref": "atom:ym", "to_node_ref": "ontology:two-point", "provenance_ref": "reviewed-world-bridge"},
            {"edge_ref": "e_qm1", "relation_kind": "source_to_pnf", "from_node_ref": "source:metrology", "to_node_ref": "pnf:metrology", "provenance_ref": "slr-world-v2"},
            {"edge_ref": "e_qm2", "relation_kind": "pnf_to_atom", "from_node_ref": "pnf:metrology", "to_node_ref": "atom:metrology", "provenance_ref": "slr-world-v2"},
            {"edge_ref": "e_qm3", "relation_kind": "external_bridge", "from_node_ref": "atom:metrology", "to_node_ref": "ontology:fisher", "provenance_ref": "reviewed-world-bridge"},
            {"edge_ref": "e_qm4", "relation_kind": "external_bridge", "from_node_ref": "atom:metrology", "to_node_ref": "ontology:information-geometry", "provenance_ref": "reviewed-world-bridge"},
            {"edge_ref": "e_qm5", "relation_kind": "external_bridge", "from_node_ref": "atom:metrology", "to_node_ref": "ontology:nv-center", "provenance_ref": "reviewed-world-bridge"},
            {"edge_ref": "e_ont1", "relation_kind": "ontology_relation", "from_node_ref": "ontology:fisher", "to_node_ref": "ontology:metric", "provenance_ref": "revision-pinned-external-graph"},
            {"edge_ref": "e_ont2", "relation_kind": "ontology_relation", "from_node_ref": "ontology:information-geometry", "to_node_ref": "ontology:metric", "provenance_ref": "revision-pinned-external-graph"},
            {"edge_ref": "e_ont3", "relation_kind": "ontology_relation", "from_node_ref": "ontology:metric", "to_node_ref": "ontology:riemannian", "provenance_ref": "revision-pinned-external-graph"},
            {"edge_ref": "e_ont4", "relation_kind": "ontology_relation", "from_node_ref": "ontology:gauge", "to_node_ref": "ontology:riemannian", "provenance_ref": "revision-pinned-external-graph"},
            {"edge_ref": "e_ont5", "relation_kind": "ontology_relation", "from_node_ref": "ontology:curvature", "to_node_ref": "ontology:gauge", "provenance_ref": "revision-pinned-external-graph"},
            {"edge_ref": "e_ont6", "relation_kind": "reviewed_cross_bridge", "from_node_ref": "ontology:two-point", "to_node_ref": "ontology:fisher", "provenance_ref": "reviewed-world-bridge"},
            {"edge_ref": "e_slr3", "relation_kind": "external_bridge", "from_node_ref": "atom:sl_world_store", "to_node_ref": "ontology:relational_store", "provenance_ref": "prod-contract"},
            {"edge_ref": "e_slb3", "relation_kind": "external_bridge", "from_node_ref": "atom:sensiblaw_projection", "to_node_ref": "ontology:relational_store", "provenance_ref": "downstream-projection"},
            {"edge_ref": "e_ns", "relation_kind": "external_bridge", "from_node_ref": "atom:navier_stokes", "to_node_ref": "ontology:vorticity", "provenance_ref": "physics-fluid"},
            {"edge_ref": "e_smii", "relation_kind": "external_bridge", "from_node_ref": "atom:smii_rom", "to_node_ref": "ontology:elasticity", "provenance_ref": "manufacturing-rom"},
            {"edge_ref": "e_frac", "relation_kind": "external_bridge", "from_node_ref": "atom:fractran", "to_node_ref": "ontology:prime_registers", "provenance_ref": "foundations-math"},
            {"edge_ref": "e_e8", "relation_kind": "external_bridge", "from_node_ref": "atom:e8_lie", "to_node_ref": "ontology:root_lattice", "provenance_ref": "symmetry-math"},
        ],
    }

    domain_specs = [
        ("slr World Store", "slr", "atom:sl_world_store", "crates/sl-world-store/src/lib.rs", "persist", "world_store", "relational_schema", 0, "prod"),
        ("SensibLaw Projection", "sensiblaw", "atom:sensiblaw_projection", "SensibLaw/src/sensiblaw/models.py", "project", "reader", "relational_schema", 1, "dev"),
        ("Balaban Yang-Mills", "ym", "atom:ym", "DASHI/Physics/YM.agda", "renormalize", "polymer", "gauge_block", 0, "dev"),
        ("Quantum Metrology", "qm", "atom:metrology", "DASHI/Physics/QuantumMetrology.agda", "estimate", "sensor", "fisher_metric", 0, "dev"),
        ("Navier-Stokes BM2", "ns", "atom:navier_stokes", "DASHI/Physics/NavierStokes.agda", "cascade", "vortex", "enstrophy", 0, "dev"),
        ("SeaMeInIt ROM", "smii", "atom:smii_rom", "SeaMeInIt/smii/rom/elastic.py", "deform", "manifold", "elastic_strain", 0, "dev"),
        ("FRACTRAN / FracDash", "fractran", "atom:fractran", "DASHI/Foundations/FRACTRAN.agda", "compute", "register", "prime_fraction", 0, "dev"),
        ("Lila E8 Lie Algebra", "e8", "atom:e8_lie", "DASHI/Symmetry/E8.agda", "rotate", "root", "exceptional_algebra", 0, "dev"),
    ]

    labels = [spec[0] for spec in domain_specs]
    domain_lanes = []
    for label, name, anc, sup, pred, actor, theme, sc, st in domain_specs:
        lane = {
            "orchestrator_id": name,
            "typed_support": {"files": [sup], "symbols": [], "lemmas": []},
            "carrier": {"scale": sc, "status": st},
            "graph_anchor_ids": [anc],
            "world_graph": graph,
            "relational_frames": [
                {
                    "frame_id": f"frame:{name}",
                    "predicate": pred,
                    "arguments": {"actor": [actor], "theme": [theme]},
                    "boundary_metadata": {},
                }
            ],
            "mutation": {"schema_altering": False},
        }
        domain_lanes.append(lane)

    n_dom = len(domain_lanes)
    matrix = np.zeros((n_dom, n_dom))
    for i in range(n_dom):
        for j in range(n_dom):
            if i == j:
                matrix[i, j] = 1.0
            else:
                receipt = spectral_no_typed_meet(domain_lanes[i], domain_lanes[j])
                matrix[i, j] = round(receipt["cosine_similarity"], 4)

    plt.figure(figsize=(10, 8), dpi=150)
    im = plt.imshow(matrix, cmap="YlOrRd", vmin=0.0, vmax=1.0)
    plt.colorbar(im, label="Cosine Similarity $\\langle v_A, v_B \\rangle$")

    plt.xticks(range(n_dom), labels, rotation=35, ha="right", fontsize=9, fontweight="bold")
    plt.yticks(range(n_dom), labels, fontsize=9, fontweight="bold")

    # Annotate values
    for i in range(n_dom):
        for j in range(n_dom):
            val = matrix[i, j]
            color = "white" if val > 0.6 else "black"
            plt.text(j, i, f"{val:.3f}", ha="center", va="center", color=color, fontsize=9, fontweight="bold")

    plt.title("Domain Cosine Similarity Heatmap (Real Grounded Coordinates)\n$\\tau = 0.15$ Quotient Orbit Boundary", fontsize=12, pad=12)
    plt.tight_layout()
    heatmap_png_path = out_dir / "fleet_domain_spectral_heatmap.png"
    plt.savefig(heatmap_png_path, dpi=150)
    plt.close()
    print(f"Saved domain spectral heatmap to {heatmap_png_path}")

    # 3. WRITE METADATA JSON
    summary = {
        "schema": "itir.pnf.spectral_corpus_visualization.v1",
        "generated_at": time.time(),
        "elapsed_seconds": round(time.perf_counter() - t0, 2),
        "corpus_entities": len(pruned_ids),
        "singular_values": s_vals,
        "marchenko_pastur": mp,
        "scatter_plot_path": str(scatter_png_path.relative_to(REPO_ROOT)),
        "heatmap_plot_path": str(heatmap_png_path.relative_to(REPO_ROOT)),
        "domain_labels": labels,
        "similarity_matrix": matrix.tolist(),
    }
    summary_path = out_dir / "fleet_spectral_visual_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Saved visualization metadata summary to {summary_path}")
    print(f"Completed in {time.perf_counter() - t0:.2f}s.")


if __name__ == "__main__":
    main()
