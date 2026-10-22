"""Validated, source-bound run/study receipts and actual scientific replay."""
from __future__ import annotations

import json

from .identity import canonical_hash, scientific_view, source_hash


def pack(result: dict) -> dict:
    if result.get("schema") not in ("crosswire-result-v1", "crosswire-study-v1"):
        raise ValueError("Only completed run/study results can be exported")
    if result.get('source_hash') != source_hash():
        raise ValueError('Result source revision differs from the current implementation')
    return {"schema": "crosswire-receipt-v1", "source_hash": result['source_hash'],
            "payload": result, "payload_hash": canonical_hash(result)}


def _envelope(receipt: dict) -> dict:
    if not isinstance(receipt, dict) or set(receipt) != {"schema", "source_hash", "payload", "payload_hash"}:
        raise ValueError("Incomplete receipt envelope")
    if receipt["schema"] != "crosswire-receipt-v1" or receipt["source_hash"] != source_hash():
        raise ValueError("Unsupported receipt or source revision; preserve the original code to replay it")
    try:
        payload = receipt["payload"]
        if canonical_hash(payload) != receipt["payload_hash"]:
            raise ValueError("Receipt content digest mismatch")
        if payload["schema"] not in ("crosswire-result-v1", "crosswire-study-v1"):
            raise ValueError("Unsupported payload")
        if payload.get('source_hash') != receipt['source_hash']:
            raise ValueError('Payload source identity differs from its envelope')
        if canonical_hash(scientific_view(payload)) != payload["scientific_hash"]:
            raise ValueError("Scientific content digest mismatch")
    except (TypeError, KeyError, OverflowError) as exc:
        raise ValueError("Incomplete or invalid scientific payload") from exc
    return payload


def check_envelope(receipt: dict) -> dict:
    """Cheap synchronous envelope/digest checks, without recomputing science."""
    return _envelope(receipt)


def validate(receipt: dict, cancel=None, progress=None) -> dict:
    """Import requires actual replay, not only internally consistent hashes."""
    payload = _envelope(receipt)
    checked = replay(receipt, cancel, progress)
    if not checked["valid"]:
        raise ValueError(checked["message"])
    return payload


def replay(receipt: dict, cancel=None, progress=None) -> dict:
    from .study import Cancelled, RunConfig, run, run_study
    payload = _envelope(receipt)
    try:
        if payload["schema"] == "crosswire-result-v1":
            fresh = run(RunConfig.from_dict(payload["configuration"]), cancel, progress)
        else:
            protocol = {k: v for k, v in payload["protocol"].items()
                        if k not in ("exploratory", "analysis_unit", "pre_execution_source_hash")}
            fresh = run_study(protocol, cancel, progress)
    except Cancelled:
        raise
    except (KeyError, TypeError, RuntimeError) as exc:
        raise ValueError("Receipt cannot reproduce its scientific result") from exc
    valid = scientific_view(fresh) == scientific_view(payload)
    return {"valid": valid, "scientific_hash": fresh["scientific_hash"],
            "message": "Scientific decisions, probes, costs and audits replay exactly" if valid else
                       "Recomputed decisions, audit or scientific accounting differ from receipt"}


def load(path) -> dict:
    with open(path, encoding="utf-8") as stream:
        value = json.load(stream, parse_constant=lambda text: (_ for _ in ()).throw(ValueError(f"Invalid JSON number {text}")))
    return validate(value)
