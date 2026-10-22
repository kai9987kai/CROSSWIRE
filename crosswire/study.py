"""Public-only acquisition followed by frozen decisions and private auditing."""
from __future__ import annotations

from collections import defaultdict
from contextlib import ExitStack
from dataclasses import asdict, dataclass, fields
from itertools import product
import random
import threading
import time
import tracemalloc
from typing import Callable

from .core import CandidateSpace, Contract, Machine
from .fixtures import catalog, make_case, oracle_plan
from .interfaces import InterfaceError, TargetProcess
from .identity import canonical_hash, scientific_view, source_hash

POLICIES = ("fixed", "random", "disagreement", "task", "aalpy", "counterexample")
ADMISSIONS = ("robust", "one_best", "unique", "fit", "identity", "abstain", "oracle")
EXECUTION_MODES = ("open_loop", "shielded")
_RUN_LOCK = threading.RLock()
_PROCESS_SOURCE_HASH = source_hash()


class Cancelled(RuntimeError):
    pass


@dataclass(frozen=True)
class RunConfig:
    family: str = "latch"
    seed: int = 17
    implementation: str = "procedural"
    split: str = "development"
    anchors: bool = False
    budget: int = 16
    horizon: int = 4
    policy: str = "task"
    admission: str = "robust"
    execution_mode: str = "open_loop"
    temporal: bool = False

    @classmethod
    def from_dict(cls, values: dict) -> "RunConfig":
        if not isinstance(values, dict) or set(values) - {f.name for f in fields(cls)}:
            raise ValueError("Unknown run fields or non-object configuration")
        instance = cls(**values)
        instance.check()
        return instance

    def check(self) -> None:
        for key, low, high in (("budget", 0, 512), ("horizon", 1, 6), ("seed", 0, 2**32 - 1)):
            value = getattr(self, key)
            if type(value) is not int or not low <= value <= high:
                raise ValueError(f"{key} must be an integer in [{low}, {high}]")
        if type(self.anchors) is not bool:
            raise ValueError("anchors must be a boolean")
        if type(self.temporal) is not bool:
            raise ValueError("temporal must be a boolean")
        if self.execution_mode not in EXECUTION_MODES:
            raise ValueError("Unknown execution mode")
        if self.family not in {f["id"] for f in catalog()}:
            raise ValueError("Unknown fixture family")
        if self.implementation not in ("table", "procedural") or self.split not in ("development", "evaluation"):
            raise ValueError("Unknown implementation or split")
        if self.policy not in POLICIES or self.admission not in ADMISSIONS:
            raise ValueError("Unknown probe/admission policy")


def _check_cancel(cancel: Callable[[], bool] | None) -> None:
    if cancel and cancel():
        raise Cancelled("Run cancelled before scientific completion")


def fit_evidence(probes: list[dict]) -> list[dict]:
    evidence = []
    for item in probes:
        if item['complete']:
            evidence.append(item)
        elif item.get('outputs'):
            evidence.append({'word': item['word'][:len(item['outputs'])],
                             'outputs': item['outputs'], 'complete': True})
    return evidence


def fit_diagnostics(space: CandidateSpace, evidence: list[dict], anchors: dict) -> dict:
    """Residual of the forced best-fit map, split into raw-output and anchor terms.

    Uses the same deterministic tie-break as CandidateSpace.plan('fit'), so a
    nonzero residual distinguishes forced fitting from consistent survivors.
    """
    losses = space.losses(evidence, anchors)
    chosen = min(losses, key=lambda i: (losses[i], i))
    raw = sum(p != o for item in evidence
              for p, o in zip(space.predict(chosen, tuple(item["word"])), item["outputs"]))
    tied = sum(1 for value in losses.values() if value == losses[chosen])
    return {"chosen_adapter_id": chosen, "chosen_adapter": space.adapters[chosen].to_dict(),
            "raw_mismatches": raw, "anchor_mismatches": losses[chosen] - raw,
            "total_residual": losses[chosen], "zero_residual": losses[chosen] == 0,
            "maps_tied_at_minimum": tied,
            "raw_symbols_compared": sum(len(item["outputs"]) for item in evidence)}


def _acquire(public: dict, policy: str, budget: int, query: Callable, counts: dict,
             cancel: Callable[[], bool] | None, progress: Callable | None, temporal: bool = False):
    """This function receives no Case, private map, target states or family label."""
    space = CandidateSpace(Machine.from_dict(public["reference"]), Contract.from_dict(public["contract"]), temporal=temporal)
    anchors = {int(k): int(v) for k, v in public.get("anchors", {}).items()}
    probes: list[dict] = []
    survivors = space.survivors(probes, anchors)
    seen: set[tuple] = set()
    error = None
    # `budget` is the shared system-call cap: every reset and every action
    # attempt counts, so all methods compare at the same total target access.
    while counts["target_calls"] < budget:
        _check_cancel(cancel)
        if space.plan(survivors, "robust")["admitted"]:
            break
        remaining_actions = budget - counts["target_calls"] - 1  # one reset per query
        if remaining_actions < 1:
            break
        word = space.choose_probe(survivors, policy, remaining_actions, seen,
                                  seed=92821 + len(probes))
        if word is None:
            break
        seen.add(word)
        before = len(survivors)
        outputs = []
        complete = False
        try:
            outputs = query(word)
            complete = True
        except InterfaceError as exc:
            error = {"code": exc.code, "message": str(exc)}
            outputs = getattr(exc, 'trace', {}).get('outputs', [])
        entry = {"word": list(word), "outputs": list(outputs), "complete": complete,
                 "survivors_before": before}
        probes.append(entry)
        survivors = space.survivors(fit_evidence(probes), anchors)
        entry["survivors_after"] = len(survivors)
        if progress:
            progress(counts["target_calls"], budget, f"{len(survivors)} mappings remain")
        if error or not survivors:
            break
    return space, survivors, probes, error


def run(config: RunConfig, cancel: Callable[[], bool] | None = None, progress: Callable | None = None) -> dict:
    """A single serialized experiment; targets are always closed on cancellation."""
    config.check()
    with _RUN_LOCK:
        return _run(config, cancel, progress)


def _run(config: RunConfig, cancel: Callable[[], bool] | None, progress: Callable | None) -> dict:
    started, cpu = time.perf_counter(), time.process_time()
    frozen_source = source_hash()
    if frozen_source != _PROCESS_SOURCE_HASH:
        raise RuntimeError('Source changed since runtime import; restart CROSSWIRE before creating evidence')
    _check_cancel(cancel)
    case = make_case(config.family, config.seed, config.implementation, config.split, config.anchors, config.horizon)
    public = case.public
    counts = dict(reset_attempts=0, step_attempts=0, reset_successes=0, step_successes=0, target_calls=0)
    baseline = {"name": config.policy, "privileged": config.admission == "oracle"}
    resources = ExitStack()
    target = None
    if not tracemalloc.is_tracing():
        tracemalloc.start()
    tracemalloc.reset_peak()
    try:
        temporal = config.temporal
        if config.policy == "aalpy" and config.admission != "oracle":
            from .baselines import acquire_aalpy
            target = resources.enter_context(TargetProcess(case.private))
            space, survivors, probes, error, detail = acquire_aalpy(public, config.budget, target, cancel)
            counts = dict(target.counts)
            baseline.update(detail)
        elif config.budget and config.admission != "oracle":
            target = resources.enter_context(TargetProcess(case.private))
            space, survivors, probes, error = _acquire(public, config.policy, config.budget, target.query, target.counts, cancel, progress, temporal=temporal)
            counts = dict(target.counts)
        else:
            space = CandidateSpace(Machine.from_dict(public["reference"]), Contract.from_dict(public["contract"]), temporal=temporal)
            survivors = space.survivors([], {int(k): int(v) for k, v in public.get("anchors", {}).items()})
            probes, error = [], None
        _check_cancel(cancel)
        if config.admission == "oracle":
            word = oracle_plan(case.private, config.horizon)
            decision = {"status": "ORACLE_DIAGNOSTIC", "admitted": word is not None,
                        "word": word, "candidate_count": len(survivors)}
        else:
            anchors = {int(k): int(v) for k, v in public.get("anchors", {}).items()}
            decision = space.plan(survivors, config.admission, transcripts=fit_evidence(probes),
                                  anchors=anchors)
            if config.admission == "fit":
                baseline["fit_diagnostics"] = fit_diagnostics(space, fit_evidence(probes), anchors)
        if error:
            decision = {"status": "INTERFACE_ERROR", "admitted": False, "word": None,
                        "candidate_count": len(survivors), "error": error}
        elif config.policy == 'aalpy' and not baseline.get('model_complete') and config.admission != 'oracle':
            decision = {'status': 'UNRESOLVED', 'admitted': False, 'word': None,
                        'candidate_count': 0, 'reason': 'Budget exhausted before a complete classical model'}
        ambiguity = space.ambiguity(survivors)
        # The digest is constructed before importing/calling the private auditor.
        frozen = canonical_hash({"decision": decision, "probes": probes, "reference": public["reference"],
                                 "contract": public["contract"], "target_id": public['target_id'],
                                 'anchors': public.get('anchors', {}), "survivors": list(survivors)})
        deployment = {'word': decision['word'], 'outputs': [], 'complete': False,
                      'error': None, 'target_steps': 0, 'resets': 0, 'target_calls': 0}
        if decision['admitted']:
            _check_cancel(cancel)
            if target is None:
                target = resources.enter_context(TargetProcess(case.private))
            from .shield import execute_deployment
            deployment = execute_deployment(target, decision['word'], space, survivors, space.contract,
                                            mode=config.execution_mode, cancel=cancel)
        from .audit import evaluate
        audit = evaluate(case, space, survivors, decision, probes, deployment)
        peak = tracemalloc.get_traced_memory()[1]
        work = dict(space.work)
        result = {
            "schema": "crosswire-result-v1", "configuration": asdict(config),
            'source_hash': frozen_source,
            "reference": public["reference"], "contract": public["contract"],
            "target_id": public["target_id"], "parent_instance_id": public["parent_instance_id"],
            "anchors": public.get("anchors", {}), "decision": decision, "ambiguity": ambiguity,
            "candidates": [a.to_dict() for a in space.adapters if a.id in survivors],
            "probes": probes, "decision_frozen_hash": frozen, 'deployment': deployment, "audit": audit,
            "metrics": {"target_steps": counts["step_attempts"], "resets": counts["reset_attempts"],
                        "target_calls": counts["target_calls"], **work,
                        'anchor_facts_supplied': len(public.get('anchors', {})),
                        "parent_cpu_seconds": time.process_time() - cpu,
                        "wall_seconds": time.perf_counter() - started, "parent_peak_traced_bytes": peak,
                        "audit_product_pairs": audit["audit_product_pairs"],
                        "audit_execution_steps": audit["audit_execution_steps"]},
            "baseline": baseline,
        }
        if source_hash() != frozen_source:
            raise RuntimeError('Source changed during run; discard mixed-revision evidence')
        result["scientific_hash"] = canonical_hash(scientific_view(result))
        return result
    finally:
        resources.close()
        tracemalloc.stop()


def summarize(rows: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    scopes = {f["id"]: f["scope"] for f in catalog()}
    for row in rows:
        cfg = row["configuration"]
        groups[(cfg["policy"] + "/" + cfg["admission"], cfg["family"], cfg["budget"])].append(row)
    result = []
    for (method, family, budget), members in sorted(groups.items()):
        n = len(members)
        admitted = sum(r["decision"]["admitted"] for r in members)
        success = sum(r["audit"]["contract_satisfied"] is True for r in members)
        harm = sum(r["audit"]["contract_satisfied"] is False for r in members)
        feasible = sum(r["audit"]["oracle_feasible"] for r in members)
        abstained = n - admitted
        result.append({
            "method": method, "family": family, "scope": scopes[family], "budget": budget, "requests": n,
            "admitted": admitted, "successful": success, "harmful": harm,
            "hazardous": sum(r["audit"]["hazard"] is True for r in members),
            "hazards_averted": sum(r["audit"].get("hazard_averted") is True for r in members),
            "shield_interventions": sum(r["audit"].get("shield_intervened") is True for r in members),
            "interface_errors": sum(r["decision"]["status"] == "INTERFACE_ERROR"
                                    or bool((r.get("deployment") or {}).get("error")) for r in members),
            "acquisition_interface_errors": sum(r["decision"]["status"] == "INTERFACE_ERROR" for r in members),
            "deployment_interface_errors": sum(bool((r.get("deployment") or {}).get("error")) for r in members),
            "abstained": abstained, "oracle_feasible": feasible,
            "admission_coverage": admitted / n, "useful_coverage": success / n,
            "feasible_useful_coverage": success / feasible if feasible else None,
            "selective_harm": harm / admitted if admitted else None, "population_harm": harm / n,
            "mean_target_steps": sum(r["metrics"]["target_steps"] for r in members) / n,
            "mean_resets": sum(r["metrics"]["resets"] for r in members) / n,
            "parent_clusters": len({r["parent_instance_id"] for r in members}),
            "utility": {str(cost): (success - harm - cost * abstained) / n for cost in (0, 0.1, 0.5, 1)},
        })
    return result


def paired_comparisons(rows: list[dict]) -> list[dict]:
    """Exploratory cluster-paired coverage differences, no power claim.

    Contrasts are emitted per call-cap stratum. Within a stratum, task and the
    comparison method are matched cell by cell (family, seed, implementation,
    anchors, split, horizon); matched deltas are averaged inside each semantic
    parent, and whole parents are resampled. Families are pooled only across
    in-family fixtures and the output labels that pooling explicitly.
    """
    scopes = {f["id"]: f["scope"] for f in catalog()}
    cells = defaultdict(dict)  # (budget, parent, cell) -> {policy: outcome}
    for row in rows:
        c = row["configuration"]
        # Out-of-family/control cases are never pooled into primary in-family effect.
        if scopes.get(c["family"]) != "in_family" or c["admission"] != "robust":
            continue
        cell = tuple(c.get(k) for k in ("family", "seed", "implementation", "anchors", "split", "horizon"))
        cells[(c["budget"], row["parent_instance_id"], cell)][c["policy"]] = \
            int(row["audit"]["contract_satisfied"] is True)
    policies = sorted({p for values in cells.values() for p in values} - {"task"})
    budgets = sorted({key[0] for key in cells})
    output = []
    for budget in budgets:
        for method in policies:
            per_parent = defaultdict(list)
            families = set()
            for (b, parent, cell), values in cells.items():
                if b == budget and "task" in values and method in values:
                    per_parent[parent].append(values["task"] - values[method])
                    families.add(cell[0])
            if not per_parent:
                continue
            delta = [sum(v) / len(v) for _, v in sorted(per_parent.items())]
            rng = random.Random(68219)
            draws = sorted(sum(rng.choice(delta) for _ in delta) / len(delta) for _ in range(2000))
            output.append({"contrast": f"task - {method}", "outcome": "useful_coverage",
                           "budget": budget, "budget_unit": "target calls (resets + actions)",
                           "parent_clusters": len(delta),
                           "matched_cells": sum(len(v) for v in per_parent.values()),
                           "families_pooled": sorted(families),
                           "mean_delta": sum(delta) / len(delta),
                           "descriptive_95_interval": [draws[49], draws[1949]],
                           "scope": "exploratory parent-cluster paired bootstrap within one call cap; "
                                    "in-family fixtures pooled; few clusters, no confirmatory claim"})
    return output


STUDY_DEFAULTS = {"families": ["latch", "symmetric", "neutral"], "seeds": [17], "budgets": [0, 8],
                  "policies": ["random", "task"], "admissions": ["robust"], "implementations": ["procedural"]}


def study_configs(spec: dict) -> list[RunConfig]:
    if not isinstance(spec, dict):
        raise ValueError("Study must be an object")
    allowed = {"families", "seeds", "budgets", "policies", "admissions", "implementations",
               "anchors", "split", "horizon", "execution_mode", "temporal"}
    if set(spec) - allowed:
        raise ValueError("Unknown study fields")
    dimensions = []
    for key, default in STUDY_DEFAULTS.items():
        values = spec.get(key, default)
        if not isinstance(values, list) or not 1 <= len(values) <= 64:
            raise ValueError(f"{key} must contain 1-64 entries")
        if len({canonical_hash(v) for v in values}) != len(values):
            raise ValueError(f"Duplicate {key} inflate repeated observations")
        dimensions.append(values)
    total = 1
    for values in dimensions:
        total *= len(values)
    if total > 512:
        raise ValueError("Study exceeds 512 runs; split the protocol explicitly")
    return [RunConfig.from_dict(dict(zip(("family", "seed", "budget", "policy", "admission", "implementation"), values),
                                         anchors=spec.get("anchors", False), split=spec.get("split", "development"),
                                         horizon=spec.get("horizon", 4),
                                         execution_mode=spec.get("execution_mode", "open_loop"),
                                         temporal=spec.get("temporal", False))) for values in product(*dimensions)]


def run_study(spec: dict, cancel: Callable[[], bool] | None = None, progress: Callable | None = None) -> dict:
    configs = study_configs(spec)
    frozen_source = source_hash()
    protocol = {**STUDY_DEFAULTS, **spec, "exploratory": True,
                "analysis_unit": "underlying semantic parent instance; label permutations and implementations clustered",
                "pre_execution_source_hash": frozen_source}
    protocol_hash = canonical_hash(protocol)
    rows = []
    for i, cfg in enumerate(configs):
        _check_cancel(cancel)
        if progress:
            progress(i, len(configs), f"{cfg.family}: {cfg.policy}/{cfg.admission}, budget {cfg.budget}")
        rows.append(run(cfg, cancel))
    if source_hash() != frozen_source:
        raise RuntimeError("Source changed during study; results cannot be labeled frozen")
    value = {"schema": "crosswire-study-v1", "protocol": protocol, "protocol_hash": protocol_hash,
             "source_hash": frozen_source, "rows": rows, "summary": summarize(rows),
             "paired": paired_comparisons(rows)}
    value["scientific_hash"] = canonical_hash(scientific_view(value))
    if progress:
        progress(len(configs), len(configs), "Complete; decisions and private audits recorded")
    return value
