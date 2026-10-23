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


_CONDITIONS = {'probe_safety': 'unrestricted', 'risk_tolerance': 0.0,
               'execution_mode': 'open_loop', 'anchors': False, 'split': 'development',
               'horizon': 4, 'temporal': False, 'escalate': False}


def _conditions(record, rows):
    """Read saved conditions, recovering missing legacy fields only if unique."""
    missing = set(_CONDITIONS) - set(record)
    matches = []
    if missing:
        for row in rows:
            cfg = row.get('configuration', {})
            if cfg.get('budget') != record['budget']:
                continue
            if 'method' in record:
                if (cfg.get('family') != record['family'] or
                        cfg.get('policy', '') + '/' + cfg.get('admission', '') != record['method']):
                    continue
            elif (cfg.get('family') not in record.get('families_pooled', []) or
                  ('fixed_admission' in record and cfg.get('admission') != record['fixed_admission']) or
                  ('fixed_policy' in record and cfg.get('policy') != record['fixed_policy'])):
                continue
            if all(key not in record or cfg.get(key, default) == record[key]
                   for key, default in _CONDITIONS.items()):
                matches.append(cfg)
    values = []
    for key, default in _CONDITIONS.items():
        possible = {cfg.get(key, default) for cfg in matches}
        if key in missing and len(possible) > 1:
            raise ValueError('Saved summary mixes unrecorded conditions; cannot render an unstratified aggregate')
        values.append(record.get(key, next(iter(possible)) if possible else default))
    return tuple(values)


def _condition_text(conditions):
    def value_text(value):
        if type(value) is bool:
            return str(value).lower()
        if type(value) in (int, float):
            return f'{value:g}'
        return str(value)
    return '; '.join(f'{key}={value_text(value)}' for key, value in zip(_CONDITIONS, conditions))


def _calls(summary):
    calibration = summary.get('mean_target_calls')
    if calibration is None and 'mean_target_steps' in summary and 'mean_resets' in summary:
        calibration = summary['mean_target_steps'] + summary['mean_resets']
    deployment = summary.get('mean_deployment_calls')
    total = summary.get('mean_total_calls')
    if total is None and calibration is not None and deployment is not None:
        total = calibration + deployment
    return calibration, deployment, total


def _mean(value):
    return 'n/a' if value is None else f'{value:.1f}'


def _table(out, headers, rows):
    out.append('| ' + ' | '.join(headers) + ' |')
    out.append('|' + '|'.join('---' for _ in headers) + '|')
    for row in rows:
        out.append('| ' + ' | '.join(str(value) for value in row) + ' |')
    out.append('')


def _reliability_pct(value):
    # Significant digits preserve a positive upper bound even with zero events.
    return 'n/a' if value is None else f'{100 * value:.4g}%'


def _reliability_interval(value):
    if value is None:
        return 'unavailable (descriptive)'
    return '[' + ', '.join(_reliability_pct(bound) for bound in value) + ']'


def _reliability_tables(out, records, rows):
    """Render saved target-cluster estimates without recomputing or pooling them."""
    if not records:
        return
    out += ['### Reliability design and sampling assumptions', '',
            'Each reliability row retains its exact method, family, call cap and conditions. '
            'Independent-parent counts are declarations; interval eligibility and its reason '
            'state which sampling assumptions apply.', '']
    design, hazards, useful, scopes = [], [], [], defaultdict(list)
    for index, record in enumerate(records, 1):
        label = f'R{index}'
        design.append([label, record['family'], record['method'], record['budget'],
                       _condition_text(_conditions(record, rows)), record['requests'],
                       record['parent_clusters'], record['independent_parents'],
                       str(record['inference_eligible']).lower(), record['inference_reason'],
                       record['interval_status']])
        confidence = _reliability_pct(record.get('confidence'))
        for key, outcome in (('target_any_deployment_hazard', 'Deployment hazard'),
                             ('target_any_calibration_hazard', 'Calibration hazard')):
            metric = record[key]
            hazards.append([label, outcome, metric['events'], metric['targets'],
                            metric['unknown_targets'], _reliability_pct(metric['rate']),
                            _reliability_pct(metric['possible_rate']), confidence,
                            _reliability_interval(metric['interval'])])
        metric = record['target_average_useful_coverage']
        useful.append([label, _reliability_pct(metric['estimate']), confidence,
                       _reliability_interval(metric['interval']),
                       _reliability_pct(record['conditional_selective_harm'])])
        scopes[record['scope']].append(label)
    _table(out, ['Row', 'Family', 'Method', 'Budget', 'Conditions', 'Requests', 'Parent clusters',
                 'Independent parents (declared)', 'Inference eligible', 'Inference reason',
                 'Interval status'], design)
    out += ['### Target-cluster hazard bounds', '',
            'Events count semantic parents with any hazard across the saved nuisance-cell design. '
            'Targets are the parent denominator; possible rates also include unknown target outcomes. '
            'Saved intervals are pointwise bounds under the assumptions listed for each row.', '']
    _table(out, ['Row', 'Outcome', 'Events', 'Targets', 'Unknown targets', 'Observed rate',
                 'Possible rate', 'Confidence', 'Pointwise interval'], hazards)
    out += ['### Target-cluster useful coverage and selective harm', '',
            'Useful coverage gives each semantic parent equal weight. Selective harm is the saved '
            'ratio of target-average failure and admission rates; it is undefined when no target admits.', '']
    _table(out, ['Row', 'Target-average useful coverage', 'Confidence', 'Pointwise interval',
                 'Conditional selective harm'], useful)
    out += ['Reliability scope:', '']
    out.extend(f'- {", ".join(labels)}: {scope}' for scope, labels in scopes.items())
    out.append('')


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

    # Families pool only within the same scope and complete scientific conditions.
    agg = defaultdict(lambda: defaultdict(float))
    for s in summary:
        key = (s['scope'], s["method"], s["budget"], _conditions(s, rows))
        for field in ("requests", "admitted", "successful", "harmful", "hazardous",
                      "hazards_averted", "shield_interventions",
                      "interface_errors", "abstained", "oracle_feasible",
                      'calibration_hazardous_runs', 'calibration_hazardous_probes'):
            agg[key][field] += s.get(field, 0)
        for field, calls in zip(('calibration_calls', 'deployment_calls', 'total_calls'), _calls(s)):
            if calls is None:
                agg[key][field + '_missing'] = True
            else:
                agg[key][field] += calls * s['requests']
    out += ["### Method × call budget (families pooled within scope and conditions)", "",
            'Controls and out-of-family stress remain separate from in-family results. '
            'Calibration costs include resets and action attempts; deployment costs are separate.', '']
    aggregate_rows = []
    for (scope, method, budget, conditions), a in sorted(agg.items()):
        n = a["requests"]
        call_means = [_mean(None if a[field + '_missing'] else a[field] / n)
                      for field in ('calibration_calls', 'deployment_calls', 'total_calls')]
        aggregate_rows.append([scope, method, budget, _condition_text(conditions), f'{n:.0f}',
                               f"{a['admitted']:.0f}", _pct(a['successful'] / n),
                               _pct(a['harmful'] / a['admitted'] if a['admitted'] else None),
                               *(f'{a[field]:.0f}' for field in ('hazardous', 'hazards_averted',
                                 'shield_interventions', 'interface_errors',
                                 'calibration_hazardous_runs', 'calibration_hazardous_probes')),
                               *call_means])
    _table(out, ['Scope', 'Method', 'Budget', 'Conditions', 'Requests', 'Admitted', 'Useful coverage',
                 'Selective harm', 'Hazard', 'Averted', 'Shield interventions', 'Interface errors',
                 'Hazardous calibration runs', 'Hazardous calibration probes', 'Mean calibration calls',
                 'Mean deployment calls', 'Mean total calls'], aggregate_rows)

    # Family detail.
    out += ["### Per family", ""]
    family_rows = []
    for s in sorted(summary, key=lambda s: (s['scope'], s["family"], s["method"], s["budget"], _conditions(s, rows))):
        family_rows.append([s['family'], s['scope'], s['method'], s['budget'],
                            _condition_text(_conditions(s, rows)), f"{s['admitted']}/{s['requests']}",
                            s['successful'], s['harmful'], s.get('hazardous', 0), s.get('hazards_averted', 0),
                            s.get('shield_interventions', 0), s['oracle_feasible'],
                            s.get('calibration_hazardous_runs', 0), s.get('calibration_hazardous_probes', 0),
                            *(_mean(value) for value in _calls(s))])
    _table(out, ['Family', 'Scope', 'Method', 'Budget', 'Conditions', 'Admitted/requests', 'Successful',
                 'Harmful', 'Hazards', 'Averted', 'Interventions', 'Oracle-feasible',
                 'Hazardous calibration runs', 'Hazardous calibration probes', 'Mean calibration calls',
                 'Mean deployment calls', 'Mean total calls'], family_rows)

    if payload.get("paired"):
        out += ["### Paired contrasts (useful coverage, within call cap)", ""]
        paired_rows = []
        for p in payload["paired"]:
            lo, hi = p["descriptive_95_interval"]
            fixed = ('admission=' + p['fixed_admission'] if 'fixed_admission' in p else
                     'policy=' + p['fixed_policy'] if 'fixed_policy' in p else 'not recorded')
            paired_rows.append([p['contrast'], p.get('scope', 'not recorded'),
                                ', '.join(p.get('families_pooled', [])) or 'not recorded',
                                p['budget'], _condition_text(_conditions(p, rows)), fixed,
                                p['parent_clusters'], p['matched_cells'], f"{p['mean_delta']:+.3f}",
                                f'[{lo:+.3f}, {hi:+.3f}]'])
        _table(out, ['Contrast', 'Scope', 'Families', 'Budget', 'Conditions', 'Fixed rule',
                     'Parent clusters', 'Matched cells', 'Mean Δ', 'Descriptive 95% interval'], paired_rows)
        out += ["", "_Exploratory parent-cluster bootstrap over few fixture clusters; not a confirmatory test._", ""]

    fits = [r for r in rows if "fit_diagnostics" in r.get("baseline", {})]
    if fits:
        out += ["### Forced-fit residuals", ""]
        fit_rows = []
        scopes = {s['family']: s['scope'] for s in summary}
        for r in sorted(fits, key=lambda r: (r["configuration"]["family"], r["configuration"]["implementation"],
                                             r["configuration"]["seed"])):
            f, c = r["baseline"]["fit_diagnostics"], r["configuration"]
            record = {**c, 'method': c['policy'] + '/' + c['admission']}
            fit_rows.append([c['family'], scopes.get(c['family'], 'not recorded'), c['implementation'],
                             c['seed'], c['budget'], _condition_text(_conditions(record, rows)),
                             f"{f['total_residual']} ({f['raw_mismatches']} + {f['anchor_mismatches']})",
                             f['maps_tied_at_minimum'], r['audit']['contract_satisfied']])
        _table(out, ['Family', 'Scope', 'Implementation', 'Seed', 'Budget', 'Conditions',
                     'Residual (raw + anchor)', 'Tied maps', 'Contract satisfied'], fit_rows)
    _reliability_tables(out, payload.get('reliability'), rows)
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
