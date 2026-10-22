"""Stable artifact identity; hashes identify content, not scientific truth."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def canonical_hash(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def source_hash() -> str:
    root = Path(__file__).parent
    content = {p.name: p.read_text(encoding="utf-8").replace("\r\n", "\n") for p in sorted(root.glob("*.py"))}
    return canonical_hash(content)


def scientific_view(result: dict) -> dict:
    """Remove measured runtime and self-referential IDs, retain scientific work."""
    value = json.loads(canonical_json(result))
    if value.get("schema") == "crosswire-study-v1":
        value["rows"] = [scientific_view(row) for row in value["rows"]]
    else:
        for field in ("parent_cpu_seconds", "wall_seconds", "parent_peak_traced_bytes"):
            value.get("metrics", {}).pop(field, None)
    value.pop("scientific_hash", None)
    return value
