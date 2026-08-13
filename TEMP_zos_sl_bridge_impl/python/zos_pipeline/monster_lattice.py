from __future__ import annotations

import hashlib
from typing import Tuple

from .types import ResonanceScore

MODS = (71, 59, 47)
PRIMARY_OFFSET = 24  # from lattice_breed_lite generator note
SECONDARY_OFFSET = 0
THRESHOLD = 3


def hash_file_bytes(data: bytes) -> int:
    """
    Surrogate for `monster-hash(file) -> h`.
    The exact monster-hash algorithm was not specified in the source artifact,
    so this uses a deterministic SHA-256-derived 64-bit integer as a pluggable stand-in.
    Replace this with the true monster-hash when available.
    """
    digest = hashlib.sha256(data).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def orbifold_coords(h: int) -> Tuple[int, int, int]:
    return (h % MODS[0], h % MODS[1], h % MODS[2])


def _mod_dist(lhs: int, rhs: int, modulus: int) -> int:
    d = abs(lhs - rhs) % modulus
    return min(d, modulus - d)


def resonance_score_from_hash(h: int, threshold: int = THRESHOLD) -> ResonanceScore:
    o71, o59, o47 = orbifold_coords(h)
    # Project into the o71-o59 plane.
    # dist = |o59 - o71 - offset| mod 59
    dist_primary = _mod_dist(o59, (o71 + PRIMARY_OFFSET) % MODS[1], MODS[1])
    dist_secondary = _mod_dist(o59, (o71 + SECONDARY_OFFSET) % MODS[1], MODS[1])
    best = min(dist_primary, dist_secondary)
    strength = max(0.0, 1.0 - (best / max(1, threshold)))
    return ResonanceScore(
        hash_u64=h,
        o71=o71,
        o59=o59,
        o47=o47,
        offset_primary=PRIMARY_OFFSET,
        offset_secondary=SECONDARY_OFFSET,
        dist_primary=dist_primary,
        dist_secondary=dist_secondary,
        resonance_strength=strength,
        resonance=best < threshold,
    )


def resonance_score(data: bytes, threshold: int = THRESHOLD) -> ResonanceScore:
    return resonance_score_from_hash(hash_file_bytes(data), threshold=threshold)


def resonance_flag(data: bytes, threshold: int = THRESHOLD) -> bool:
    return resonance_score(data, threshold=threshold).resonance
