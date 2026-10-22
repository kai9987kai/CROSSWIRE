"""Render a CROSSWIRE study receipt into a Markdown results table.

Reads only the saved receipt; it does not rerun or alter scientific results.
Usage: python tools/report.py reports/pilot-in-family-receipt.json [--title T]
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path


def _pct(value):
    return "n/a" if value is None else f"{100 * value:.0f}%"


def render(receipt: dict, title: str) -> str:
    payload = receipt["payload"]
    if payload.get("schema") != "crosswire-study-v1":
        raise ValueError("Expected a study receipt")
    rows, summary = payload["rows"], payload["summary"]
    out = [f"## {title}", "",
           f"- Runs: {len(rows)}; source hash `{payload['source_hash'][:16]}…`; "
           f"protocol hash `{payload['protocol_hash'][:16]}…`; scientific hash `{payload['scientific_hash'][:16]}…`.",
           f"- Parent clusters: {len({r['parent_instance_id'] for r in rows})} "
           "(label permutations and implementations are not independent samples).", ""]

    # Method × budget aggregate across families (each family weighted by its requests).
    agg = defaultdict(lambda: defaultdict(float))
    for s in summary:
        key = (s["method"], s["budget"])
        for field in ("requests", "admitted", "successful", "harmful", "hazardous",
                      "interface_errors", "abstained", "oracle_feasible"):
            agg[key][field] += s[field]
        agg[key]["calls"] += (s["mean_target_steps"] + s["mean_resets"]) * s["requests"]
    out += ["### Method × call budget (pooled over families)", "",
            "| Method | Budget | Requests | Admitted | Useful coverage | Selective harm | Hazard | Interface errors | Mean calls |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for (method, budget), a in sorted(agg.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        n = a["requests"]
        out.append(f"| {method} | {budget} | {n:.0f} | {a['admitted']:.0f} | {_pct(a['successful'] / n)} | "
                   f"{_pct(a['harmful'] / a['admitted'] if a['admitted'] else None)} | {a['hazardous']:.0f} | "
                   f"{a['interface_errors']:.0f} | {a['calls'] / n:.1f} |")
    out.append("")

    # Family detail.
    out += ["### Per family", "",
            "| Family | Scope | Method | Budget | Admitted/requests | Successful | Harmful | Oracle-feasible |",
            "|---|---|---|---:|---:|---:|---:|---:|"]
    for s in sorted(summary, key=lambda s: (s["family"], s["method"], s["budget"])):
        out.append(f"| {s['family']} | {s['scope']} | {s['method']} | {s['budget']} | {s['admitted']}/{s['requests']} | "
                   f"{s['successful']} | {s['harmful']} | {s['oracle_feasible']} |")
    out.append("")

    if payload.get("paired"):
        out += ["### Paired contrasts (useful coverage, within call cap)", "",
                "| Contrast | Budget | Parent clusters | Matched cells | Mean Δ | Descriptive 95% interval |",
                "|---|---:|---:|---:|---:|---|"]
        for p in payload["paired"]:
            lo, hi = p["descriptive_95_interval"]
            out.append(f"| {p['contrast']} | {p['budget']} | {p['parent_clusters']} | {p['matched_cells']} | "
                       f"{p['mean_delta']:+.3f} | [{lo:+.3f}, {hi:+.3f}] |")
        out += ["", "_Exploratory parent-cluster bootstrap over few fixture clusters; not a confirmatory test._", ""]

    fits = [r for r in rows if "fit_diagnostics" in r["baseline"]]
    if fits:
        out += ["### Forced-fit residuals", "",
                "| Family | Implementation | Seed | Residual (raw + anchor) | Tied maps | Contract satisfied |",
                "|---|---|---:|---:|---:|---|"]
        for r in sorted(fits, key=lambda r: (r["configuration"]["family"], r["configuration"]["implementation"],
                                             r["configuration"]["seed"])):
            f, c = r["baseline"]["fit_diagnostics"], r["configuration"]
            out.append(f"| {c['family']} | {c['implementation']} | {c['seed']} | {f['total_residual']} "
                       f"({f['raw_mismatches']} + {f['anchor_mismatches']}) | {f['maps_tied_at_minimum']} | "
                       f"{r['audit']['contract_satisfied']} |")
        out.append("")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--title", default="Study results")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    text = render(json.loads(args.receipt.read_text(encoding="utf-8")), args.title)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        import sys
        sys.stdout.reconfigure(encoding="utf-8")
        print(text)


if __name__ == "__main__":
    main()
