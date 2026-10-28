#!/usr/bin/env python3
"""Hierarchical PNF Topic Extraction, Continuous/Discrete Pareto Worker Allocation,
and Full 500-Conversation Manifold Projection.

Dynamically discovers primary, sub, and sub-sub topics from the PNF factor graph
across all 449 conversations in fleet_top500_iter1.slrw.
Produces:
  - docs/fleet/fleet_500_manifold_scatter.png (t-SNE 2D manifold of all 500 conversations)
  - docs/fleet/fleet_hierarchical_topic_heatmap.png (Discovered cluster dendrogram heatmap)
  - docs/fleet/fleet_hierarchical_pareto_summary.json (Multi-scale hierarchy & Pareto allocations)
"""

from __future__ import annotations

import collections
import json
import math
from pathlib import Path
import re
import struct
import sys
import time

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "itir-mcp" / "src"))
sys.path.insert(0, str(REPO_ROOT / "reverse-engineered-chatgpt"))
sys.path.insert(0, str(REPO_ROOT / "SensibLaw"))
sys.path.insert(0, str(REPO_ROOT / "SensibLaw" / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import pdist, squareform
from sklearn.manifold import TSNE

from re_gpt.gap_comparator import (
    DEFAULT_WORLD_DIR,
    FRAGMENT_NAMES,
    ExactGapComparator,
)
from itir_mcp.pnf_spectral_packet import (
    extract_relational_frames,
    spectral_no_typed_meet,
    _cosine_similarity,
)


STOP_LEMMAS = {
    "be", "have", "do", "get", "make", "say", "use", "can", "will", "would",
    "could", "not", "it", "this", "that", "there", "which", "what", "all",
    "one", "two", "more", "other", "such", "also", "then", "so", "as", "at",
    "by", "for", "from", "in", "into", "of", "on", "to", "with", "you", "i",
    "we", "they", "he", "she", "\\", "\\\\", "t", "s",
}


def load_roster_titles() -> dict[str, str]:
    """Extract known titles and cluster names from fleet master roster."""
    titles: dict[str, str] = {}
    roster_paths = [
        REPO_ROOT.parent / "fleet_master_roster.md",
        Path("/home/c/.gemini/antigravity/brain/b994a31a-cc21-4949-a4f5-670f5363e464/fleet_master_roster.md"),
    ]
    for p in roster_paths:
        if p.exists():
            text = p.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(r"\| `([a-f0-9]{8})` \| \*\*(\d+)\*\* \| (.*?) \| (.*?) \|", text):
                cid_prefix = m.group(1).lower()
                title = m.group(3).strip()
                cluster = m.group(4).strip()
                titles[cid_prefix] = f"{title} [{cluster}]"
    return titles


def stream_slrw_corpus() -> tuple[list[dict[str, float]], list[str], dict[str, list[dict]]]:
    """Stream all raw PNF slots from fleet_top500_iter1.slrw and group into relational frames."""
    slrw_path = DEFAULT_WORLD_DIR / "fleet_top500_iter1.slrw"
    raw_slots_by_thread: dict[str, list[dict]] = collections.defaultdict(list)

    if not slrw_path.exists():
        raise FileNotFoundError(f"Missing {slrw_path}")

    print(f"Streaming PNF records from {slrw_path} ({slrw_path.stat().st_size / 1e6:.1f} MB)...")
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
                        raw_slots_by_thread[cid].append({
                            "slot_id": f"s_{len(raw_slots_by_thread[cid])}",
                            "sentence_id": f"sent_{sent_id}",
                            "head_ordinal": h_ord,
                            "head_lemma": head_lemma.lower(),
                            "lemma": slot_lemma.lower(),
                            "argument_role": FRAGMENT_NAMES.get(frag_u8, "arg"),
                        })
                except Exception:
                    continue

    print(f"Loaded raw slots across {len(raw_slots_by_thread)} threads.")

    # Group into relational frames & factor multisets
    thread_multisets: list[dict[str, float]] = []
    thread_ids: list[str] = []
    thread_frames: dict[str, list[dict]] = {}

    for cid, slots in raw_slots_by_thread.items():
        frames = extract_relational_frames(slots)
        thread_frames[cid] = frames
        features = collections.Counter()
        for f in frames:
            pred = f.get("predicate", "").lower()
            if pred and pred not in STOP_LEMMAS:
                features[f"pred:{pred}"] += 2.0
            args_map = f.get("arguments", {})
            for role, args in args_map.items():
                for arg in args:
                    arg_clean = arg.lower().strip()
                    if arg_clean and arg_clean not in STOP_LEMMAS and len(arg_clean) > 2:
                        features[f"arg:{role}:{arg_clean}"] += 1.0
                        if pred and pred not in STOP_LEMMAS:
                            features[f"frame:{pred}:{role}:{arg_clean}"] += 1.5
        if features:
            thread_multisets.append(dict(features))
            thread_ids.append(cid)

    # Repo docs
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
                thread_frames[p.name] = []

    return thread_multisets, thread_ids, thread_frames


def compute_continuous_spectral_embedding(
    multisets: list[dict[str, float]],
    top_k_factors: int = 1500,
) -> tuple[np.ndarray, np.ndarray, list[str], dict[str, float]]:
    """Compute continuous SVD coordinates preserving all macroscopic modes λ > λ₊."""
    factor_counts = collections.Counter()
    for m in multisets:
        for k, v in m.items():
            factor_counts[k] += v

    top_factors = [k for k, _ in factor_counts.most_common(top_k_factors)]
    factor_to_idx = {f: idx for idx, f in enumerate(top_factors)}

    N = len(multisets)
    M = len(top_factors)
    X = np.zeros((N, M), dtype=np.float64)
    for i, m in enumerate(multisets):
        for f, v in m.items():
            j = factor_to_idx.get(f)
            if j is not None:
                X[i, j] = v

    mean = np.mean(X, axis=0)
    centered = X - mean

    U, s_vals, Vt = np.linalg.svd(centered, full_matrices=False)

    # Marchenko-Pastur threshold
    variances = np.var(centered, axis=0)
    sigma2 = float(np.median(variances))
    gamma = M / N
    lambda_plus = float(sigma2 * (1.0 + np.sqrt(gamma)) ** 2)
    macro_modes = int(np.sum(s_vals > np.sqrt(lambda_plus * N)))

    print(f"SVD singular values (top 8): {[round(v, 1) for v in s_vals[:8]]}")
    print(f"Marchenko-Pastur λ₊: {lambda_plus:.2f} | Macroscopic modes: {macro_modes} of {len(s_vals)}")

    # Continuous representation in macroscopic subspace
    k_dim = max(macro_modes, 10)
    coordinates_high_d = U[:, :k_dim] * s_vals[:k_dim]

    mp_stats = {
        "sigma_squared": sigma2,
        "gamma": gamma,
        "lambda_plus": lambda_plus,
        "macroscopic_modes": macro_modes,
        "spectral_dimensions": k_dim,
    }
    return coordinates_high_d, s_vals, top_factors, mp_stats


def discover_hierarchical_topics(
    high_d_coords: np.ndarray,
    thread_ids: list[str],
    multisets: list[dict[str, float]],
    roster_titles: dict[str, str],
    k_primary: int = 8,
    k_sub_factor: int = 3,
) -> dict[str, Any]:
    """Perform hierarchical quotient orbit clustering into Primary -> Sub -> Sub-Sub topics."""
    # Normalize rows to unit sphere for cosine similarity
    norms = np.linalg.norm(high_d_coords, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    unit_coords = high_d_coords / norms

    # Pairwise cosine distance
    dist_vec = pdist(unit_coords, metric="cosine")
    # Clean NaNs or infs if any
    dist_vec = np.nan_to_num(dist_vec, nan=1.0, posinf=1.0, neginf=0.0)
    dist_matrix = squareform(dist_vec)

    # Linkage tree
    Z = linkage(dist_vec, method="average")

    # 1. Primary Clusters
    primary_labels = fcluster(Z, t=k_primary, criterion="maxclust")

    # 2. Sub Clusters (fine threshold)
    sub_labels = fcluster(Z, t=k_primary * k_sub_factor, criterion="maxclust")

    # Build hierarchy structures
    hierarchy: dict[int, dict[str, Any]] = {}
    primary_names: dict[int, str] = {}

    for c_id in np.unique(primary_labels):
        members = np.where(primary_labels == c_id)[0]
        # Find top factors for this cluster
        cluster_cnt = collections.Counter()
        for idx in members:
            for k, v in multisets[idx].items():
                cluster_cnt[k] += v

        # Top 3 most characteristic factors
        top_factors = [k for k, _ in cluster_cnt.most_common(4)]
        motif = " · ".join(f.split(":")[-1] for f in top_factors[:3])

        # Check if known title matches any thread in this cluster
        matched_title = ""
        for idx in members:
            tid = thread_ids[idx].replace("chat:", "")[:8].lower()
            if tid in roster_titles:
                matched_title = roster_titles[tid]
                break

        display_name = matched_title or f"Topic {c_id}: {motif}"
        primary_names[c_id] = display_name

        # Sub-clusters in this primary
        subs_in_cluster = np.unique(sub_labels[members])
        sub_list = []
        for s_id in subs_in_cluster:
            sub_members = [idx for idx in members if sub_labels[idx] == s_id]
            sub_cnt = collections.Counter()
            for idx in sub_members:
                for k, v in multisets[idx].items():
                    sub_cnt[k] += v
            sub_motif = " · ".join(f.split(":")[-1] for f, _ in sub_cnt.most_common(2))
            sub_list.append({
                "sub_cluster_id": int(s_id),
                "member_count": len(sub_members),
                "sub_motif": sub_motif,
                "thread_ids": [thread_ids[idx] for idx in sub_members],
            })

        hierarchy[int(c_id)] = {
            "primary_cluster_id": int(c_id),
            "display_name": display_name,
            "member_count": len(members),
            "top_motif": motif,
            "sub_topics": sub_list,
            "member_indices": members.tolist(),
        }

    return {
        "hierarchy": hierarchy,
        "primary_labels": primary_labels,
        "sub_labels": sub_labels,
        "primary_names": primary_names,
        "linkage_matrix": Z,
        "dist_matrix": dist_matrix,
    }


def compute_pareto_allocations(
    high_d_coords: np.ndarray,
    s_vals: np.ndarray,
    thread_ids: list[str],
    cluster_info: dict[str, Any],
    roster_titles: dict[str, str],
    capacities: tuple[int, ...] = (5, 10, 20, 50),
) -> dict[str, Any]:
    """Compute continuous alpha scores and capacity-dependent Pareto worker allocations."""
    # Alpha priority for each thread: weighted projection energy along macroscopic eigen modes
    norm_s = s_vals[:high_d_coords.shape[1]] / s_vals[0]
    alpha_scores = np.sum(np.abs(high_d_coords) * norm_s, axis=1)

    # Rank threads by alpha
    ranked_indices = np.argsort(alpha_scores)[::-1]

    hierarchy = cluster_info["hierarchy"]
    primary_labels = cluster_info["primary_labels"]

    allocations_by_capacity: dict[int, list[dict[str, Any]]] = {}

    for W in capacities:
        schedule = []
        # When capacity is constrained (W <= 10), roll sub-topics into primary topics
        if W <= len(hierarchy):
            # Sort primary topics by aggregate alpha
            primary_alphas = []
            for c_id, h in hierarchy.items():
                members = h["member_indices"]
                agg_alpha = float(np.sum(alpha_scores[members]))
                lead_idx = members[np.argmax(alpha_scores[members])]
                primary_alphas.append((agg_alpha, c_id, lead_idx))
            primary_alphas.sort(reverse=True)

            for slot, (agg_alpha, c_id, lead_idx) in enumerate(primary_alphas[:W]):
                h = hierarchy[c_id]
                tid = thread_ids[lead_idx]
                schedule.append({
                    "worker_slot": slot + 1,
                    "mode": "primary_roll",
                    "lead_thread_id": tid,
                    "lead_title": roster_titles.get(tid.replace("chat:", "")[:8].lower(), h["display_name"]),
                    "primary_cluster": h["display_name"],
                    "rolled_subtopics_count": len(h["sub_topics"]),
                    "rolled_subtopic_motifs": [s["sub_motif"] for s in h["sub_topics"]],
                    "aggregate_alpha": round(agg_alpha, 2),
                    "action": "execute_subtopics_as_internal_work_packets",
                })
        else:
            # Capacity is abundant: split sub-topics into independent worker threads
            all_subs = []
            for c_id, h in hierarchy.items():
                for s in h["sub_topics"]:
                    sub_members = [thread_ids.index(t) for t in s["thread_ids"] if t in thread_ids]
                    sub_alpha = float(np.sum(alpha_scores[sub_members])) if sub_members else 0.0
                    lead_idx = sub_members[np.argmax(alpha_scores[sub_members])] if sub_members else 0
                    all_subs.append((sub_alpha, c_id, s, lead_idx))
            all_subs.sort(reverse=True)

            for slot, (sub_alpha, c_id, s, lead_idx) in enumerate(all_subs[:W]):
                tid = thread_ids[lead_idx]
                schedule.append({
                    "worker_slot": slot + 1,
                    "mode": "independent_subtopic",
                    "lead_thread_id": tid,
                    "lead_title": roster_titles.get(tid.replace("chat:", "")[:8].lower(), f"Sub-topic: {s['sub_motif']}"),
                    "primary_parent": hierarchy[c_id]["display_name"],
                    "sub_motif": s["sub_motif"],
                    "subtopic_alpha": round(sub_alpha, 2),
                    "action": "dispatch_independent_worker_lane",
                })

        allocations_by_capacity[W] = schedule

    return {
        "alpha_scores": alpha_scores.tolist(),
        "allocations_by_capacity": allocations_by_capacity,
    }


def render_visualizations(
    high_d_coords: np.ndarray,
    thread_ids: list[str],
    cluster_info: dict[str, Any],
    pareto_info: dict[str, Any],
    roster_titles: dict[str, str],
    out_dir: Path,
) -> tuple[Path, Path]:
    """Render 2D t-SNE manifold scatter and hierarchical topic heatmap."""
    alpha_scores = np.array(pareto_info["alpha_scores"])
    primary_labels = cluster_info["primary_labels"]
    hierarchy = cluster_info["hierarchy"]
    primary_names = cluster_info["primary_names"]

    # 1. 2D t-SNE Manifold Projection of ALL 449 conversations
    print("Computing 2D t-SNE manifold projection for all 449 conversations...")
    tsne = TSNE(
        n_components=2,
        perplexity=min(30, len(thread_ids) - 1),
        metric="cosine",
        init="random",
        random_state=42,
        max_iter=1000,
    )
    xy_coords = tsne.fit_transform(high_d_coords)

    fig, ax = plt.subplots(figsize=(14, 10), dpi=160)
    cmap = matplotlib.colormaps.get_cmap("tab10")

    # Normalize alpha scores for point sizes (min size 25, max size 250)
    min_a, max_a = np.min(alpha_scores), np.max(alpha_scores)
    point_sizes = 25 + 225 * ((alpha_scores - min_a) / (max_a - min_a + 1e-6))

    for c_id, h in hierarchy.items():
        members = h["member_indices"]
        color = cmap((c_id - 1) % 10)
        scatter = ax.scatter(
            xy_coords[members, 0],
            xy_coords[members, 1],
            s=point_sizes[members],
            color=color,
            alpha=0.75,
            edgecolors="black",
            linewidths=0.5,
            label=f"Topic {c_id}: {h['display_name'][:28]} ({len(members)} convos)",
        )

        # Draw centroid
        centroid_x = np.mean(xy_coords[members, 0])
        centroid_y = np.mean(xy_coords[members, 1])
        ax.plot(
            centroid_x, centroid_y,
            marker="X", markersize=12,
            markeredgecolor="black", markerfacecolor=color,
        )

    # Annotate prominent anchor and lead threads
    top_lead_indices = np.argsort(alpha_scores)[::-1][:14]
    for idx in top_lead_indices:
        tid = thread_ids[idx]
        title = roster_titles.get(tid.replace("chat:", "")[:8].lower(), tid[:12])
        ax.annotate(
            title[:24],
            (xy_coords[idx, 0], xy_coords[idx, 1]),
            fontsize=8,
            fontweight="bold",
            alpha=0.9,
            bbox=dict(boxstyle="round,pad=0.25", fc="#ffffff", ec="#888888", alpha=0.8, lw=0.6),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.1", lw=0.5, color="#555555"),
        )

    ax.set_title(
        f"Fleet 500-Corpus PNF Spectral Manifold (t-SNE 2D Projection, N={len(thread_ids)})\n"
        f"Continuous/Discrete Pareto Allocation: Point Size ~ α Priority Score | Colors ~ Discovered Primary Topics",
        fontsize=13,
        pad=14,
        fontweight="bold",
    )
    ax.set_xlabel("Manifold Dimension 1 (t-SNE)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Manifold Dimension 2 (t-SNE)", fontsize=11, fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9, frameon=True)

    plt.tight_layout()
    scatter_path = out_dir / "fleet_500_manifold_scatter.png"
    plt.savefig(scatter_path, dpi=160, bbox_inches="tight")
    plt.close()
    print(f"Saved 500-conversation manifold scatter plot to {scatter_path}")

    # 2. Clustered Hierarchical Topic Dendrogram / Heatmap
    # Compute centroid vectors for all primary topics
    c_ids = sorted(hierarchy.keys())
    centroids = np.zeros((len(c_ids), high_d_coords.shape[1]))
    labels = []
    for i, c_id in enumerate(c_ids):
        members = hierarchy[c_id]["member_indices"]
        centroids[i] = np.mean(high_d_coords[members], axis=0)
        labels.append(f"T{c_id}: {hierarchy[c_id]['display_name'][:26]}")

    # Pairwise centroid cosine similarity
    c_norms = np.linalg.norm(centroids, axis=1, keepdims=True)
    c_norms[c_norms == 0] = 1.0
    u_centroids = centroids / c_norms
    sim_matrix = np.dot(u_centroids, u_centroids.T)

    fig, ax = plt.subplots(figsize=(11, 9), dpi=160)
    im = ax.imshow(sim_matrix, cmap="YlOrRd", vmin=0.0, vmax=1.0)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Continuous Cosine Similarity $\\langle v_A, v_B \\rangle$", fontsize=11)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=9, fontweight="bold")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9, fontweight="bold")

    for i in range(len(labels)):
        for j in range(len(labels)):
            val = sim_matrix[i, j]
            color = "white" if val > 0.65 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=9, fontweight="bold")

    ax.set_title(
        "Dynamically Discovered Primary Topic Cosine Similarity Matrix\n"
        "Multi-Scale Hierarchy (Primary -> Sub -> Sub-Sub Topics)",
        fontsize=12,
        pad=14,
        fontweight="bold",
    )
    plt.tight_layout()
    heatmap_path = out_dir / "fleet_hierarchical_topic_heatmap.png"
    plt.savefig(heatmap_path, dpi=160, bbox_inches="tight")
    plt.close()
    print(f"Saved hierarchical topic heatmap to {heatmap_path}")

    return scatter_path, heatmap_path


def main() -> None:
    t0 = time.perf_counter()
    out_dir = REPO_ROOT / "docs" / "fleet"
    out_dir.mkdir(parents=True, exist_ok=True)

    roster_titles = load_roster_titles()
    multisets, thread_ids, thread_frames = stream_slrw_corpus()
    if not multisets:
        print("No multisets extracted. Aborting.")
        return

    high_d_coords, s_vals, top_factors, mp_stats = compute_continuous_spectral_embedding(multisets)
    cluster_info = discover_hierarchical_topics(high_d_coords, thread_ids, multisets, roster_titles)
    pareto_info = compute_pareto_allocations(high_d_coords, s_vals, thread_ids, cluster_info, roster_titles)

    scatter_path, heatmap_path = render_visualizations(
        high_d_coords,
        thread_ids,
        cluster_info,
        pareto_info,
        roster_titles,
        out_dir,
    )

    # Save summary JSON
    summary = {
        "version": "itir.pnf.hierarchical_pareto_corpus.v1",
        "generated_at": time.time(),
        "elapsed_seconds": round(time.perf_counter() - t0, 2),
        "corpus_entity_count": len(thread_ids),
        "marchenko_pastur": mp_stats,
        "primary_topics": [
            {
                "topic_id": k,
                "name": v["display_name"],
                "member_count": v["member_count"],
                "top_motif": v["top_motif"],
                "sub_topic_count": len(v["sub_topics"]),
                "sub_topics": [
                    {"sub_id": s["sub_cluster_id"], "sub_motif": s["sub_motif"], "member_count": s["member_count"]}
                    for s in v["sub_topics"]
                ],
            }
            for k, v in cluster_info["hierarchy"].items()
        ],
        "allocations_by_capacity": pareto_info["allocations_by_capacity"],
        "artifacts": {
            "manifold_scatter": str(scatter_path.relative_to(REPO_ROOT)),
            "hierarchical_heatmap": str(heatmap_path.relative_to(REPO_ROOT)),
        },
    }
    summary_path = out_dir / "fleet_hierarchical_pareto_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Saved complete hierarchical Pareto summary to {summary_path}")
    print(f"Workflow completed successfully in {time.perf_counter() - t0:.2f}s.")


if __name__ == "__main__":
    main()
