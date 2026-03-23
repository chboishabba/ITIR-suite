from __future__ import annotations

from typing import Any


DA51_PREFIX = 0xDA51


def decode_dasl_hex(value: str | None) -> dict[str, Any] | None:
    if not value:
        return None
    text = str(value).strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    try:
        cid = int(text, 16)
    except ValueError:
        return None
    if cid >> 48 != DA51_PREFIX:
        return None

    type_code = (cid >> 44) & 0xF
    raw_data = cid & 0x0FFFFFFFFFFF
    decoded: dict[str, Any] = {
        "raw": value,
        "prefix": "0xDA51",
        "type_code": type_code,
        "raw_data": f"0x{raw_data:012x}",
    }
    if type_code == 3:
        decoded["nested_cid"] = {
            "shard_index": (cid >> 36) & 0xFF,
            "hecke_index": (cid >> 28) & 0xFF,
            "bott_index": (cid >> 20) & 0xFF,
            "hash_fragment": cid & 0xFFFFF,
        }
    return decoded
