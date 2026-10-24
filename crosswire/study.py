"""Public-only acquisition followed by frozen decisions and private auditing."""
from __future__ import annotations

from collections import defaultdict
from contextlib import ExitStack
from dataclasses import asdict, dataclass, fields
from itertools import product
import math
import random
import threading
import time
import tracemalloc
from typing import Callable

from .core import CandidateSpace, Contract, Machine
from .fixtures import catalog, make_case, oracle_plan
from .interfaces import InterfaceError, TargetProcess
from .identity import canonical_hash, scientific_view, source_hash

POLICIES = ("fixed", "random", "disagreement", "task", "aalpy", "counterexample", "entropy", "ec2", "branching")
ADMISSIONS = ("robust", "adaptive", "one_best", "unique", "fit", "identity", "abstain", "oracle", "risk_controlled")
EXECUTION_MODES = ("open_loop", "shielded", "recovery", "replan")
PROBE_SAFETY_MODES = ('unrestricted', 'model_safe')
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
    escalate: bool = False
    probe_safety: str = 'unrestricted'
    risk_tolerance: float = 0.0
    instance_seed: int | None = None
    fault_schedule: dict | None = None

    def __post_init__(self):
        if self.family == 'generated_protocol' and self.instance_seed is None:
            object.__setattr__(self, 'instance_seed', 0)

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
        if self.instance_seed is not None and (
                type(self.instance_seed) is not int or not 0 <= self.instance_seed <= 2**32 - 1):
            raise ValueError('instance_seed must be an unsigned 32-bit integer or null')
        if self.instance_seed is not None and self.family != 'generated_protocol':
            raise ValueError('instance_seed is supported only by generated_protocol')
        if type(self.anchors) is not bool:
            raise ValueError("anchors must be a boolean")
        if type(self.temporal) is not bool:
            raise ValueError("temporal must be a boolean")
        if type(self.escalate) is not bool:
            raise ValueError("escalate must be a boolean")
        if self.probe_safety not in PROBE_SAFETY_MODES:
            raise ValueError('Unknown probe_safety mode')
        if (type(self.risk_tolerance) not in (int, float) or not 0 <= self.risk_tolerance < 1
                or not math.isfinite(self.risk_tolerance)):
            raise ValueError('risk_tolerance must be a finite number in [0, 1)')
        if self.risk_tolerance and self.admission != 'risk_controlled':
            raise ValueError('Positive risk_tolerance requires risk_controlled admission')
        if self.policy == 'aalpy' and self.probe_safety != 'unrestricted':
            raise ValueError('The AALpy baseline does not support model_safe calibration')
        if self.escalate and self.temporal:
            raise ValueError("escalate cannot be combined with temporal=True (starts at static and escalates)")
        if self.execution_mode not in EXECUTION_MODES:
            raise ValueError("Unknown execution mode")
        if self.family not in {f["id"] for f in catalog()}:
            raise ValueError("Unknown fixture family")
        if self.implementation not in ("table", "procedural") or self.split not in ("development", "evaluation"):
            raise ValueError("Unknown implementation or split")
        if self.policy not in POLICIES or self.admission not in ADMISSIONS:
            raise ValueError("Unknown probe/admission policy")
        if self.admission == 'adaptive' and self.execution_mode not in ('shielded', 'recovery'):
            raise ValueError('Adaptive admission requires shielded or recovery execution')
        if self.policy == 'aalpy' and self.temporal:
            raise ValueError('The AALpy baseline does not support temporal adapters')
        if self.policy == 'aalpy' and self.admission == 'adaptive':
            raise ValueError('The AALpy baseline does not support adaptive admission')
        if self.policy == 'aalpy' and self.escalate:
            raise ValueError('The AALpy baseline does not support model escalation')
        if self.fault_schedule is not None:
            if not isinstance(self.fault_schedule, dict):
                raise ValueError('fault_schedule must be a dict or None')
            if 'step' not in self.fault_schedule or 'type' not in self.fault_schedule:
                raise ValueError("fault_schedule must specify 'step' and 'type'")
            if type(self.fault_schedule['step']) is not int or self.fault_schedule['step'] < 0:
                raise ValueError("fault_schedule 'step' must be a non-negative integer")
            valid_faults = ('sensor_drift', 'actuator_swap', 'delay_spike', 'stuck_output', 'semantic_swap')
            if self.fault_schedule['type'] not in valid_faults:
                raise ValueError(f"fault_schedule 'type' must be one of {valid_faults}")


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
             cancel: Callable[[], bool] | None, progress: Callable | None, temporal: bool = False,
             admission: str = 'robust', escalate: bool = False, probe_safety: str = 'unrestricted',
             step: Callable | None = None, reset: Callable | None = None):
    """This function receives no Case, private map, target states or family label."""
    space = CandidateSpace(Machine.from_dict(public["reference"]), Contract.from_dict(public["contract"]), temporal=temporal)
    anchors = {int(k): int(v) for k, v in public.get("anchors", {}).items()}
    probes: list[dict] = []
    survivors = space.survivors(probes, anchors)
    seen: set[tuple] = set()
    error = None
    escalated = False
    escalation_history = []
    safe_mode = probe_safety == 'model_safe'
    # An enabled larger class must be guarded before it becomes necessary for
    # fitting. Static predictions alone cannot protect a delayed target.
    safety_space = (CandidateSpace(space.machine, space.contract, temporal=True)
                    if safe_mode and escalate else space)
    stop_reason = 'CALL_CAP'
    # `budget` is the shared system-call cap: every reset and every action
    # attempt counts, so all methods compare at the same total target access.
    while counts["target_calls"] < budget:
        _check_cancel(cancel)
        if admission == 'adaptive':
            from .adaptive import synthesize_policy
            ready = synthesize_policy(space, survivors, cancel=cancel)['admitted']
        else:
            ready = space.plan(survivors, "robust")["admitted"]
        if ready:
            stop_reason = 'CONTRACT_READY'
            break
        remaining_actions = budget - counts["target_calls"] - 1  # one reset per query
        if remaining_actions < 1:
            break
        selection_space = safety_space if safe_mode else space
        selection_ids = (selection_space.survivors(fit_evidence(probes), anchors)
                         if selection_space is not space else survivors)
        before = len(survivors)

        if policy == 'branching':
            # Interactive within-query branching calibration:
            # Observes intermediate outputs and selects each subsequent action conditionally.
            word = []
            outputs = []
            complete = False
            try:
                if reset is not None:
                    reset()
                elif hasattr(query, '__self__') and hasattr(query.__self__, 'reset'):
                    query.__self__.reset()
            except InterfaceError as exc:
                error = {"code": exc.code, "message": str(exc)}
                stop_reason = 'INTERFACE_ERROR'
                break

            current_ids = list(selection_ids)
            max_query_depth = min(4, remaining_actions)

            while len(word) < max_query_depth and counts["target_calls"] < budget:
                _check_cancel(cancel)
                if len(current_ids) <= 1:
                    break

                if budget - counts["target_calls"] < 1:
                    break

                next_action = selection_space.choose_branching_step(
                    current_ids, tuple(word), safe_only=safe_mode, safe_ids=selection_ids,
                    seed=92821 + len(probes) + len(word)
                )
                if next_action is None:
                    break

                try:
                    if step is not None:
                        out = step(next_action)
                    elif hasattr(query, '__self__') and hasattr(query.__self__, 'step'):
                        out = query.__self__.step(next_action)
                    else:
                        out = query([next_action])[-1]
                    word.append(next_action)
                    outputs.append(out)
                except InterfaceError as exc:
                    error = {"code": exc.code, "message": str(exc)}
                    break

                current_ids = [
                    i for i in current_ids
                    if selection_space.predict(i, tuple(word)) == tuple(outputs)
                ]
                if len(current_ids) <= 1:
                    break

            complete = error is None
            if word:
                seen.add(tuple(word))
                entry = {"word": list(word), "outputs": list(outputs), "complete": complete,
                         "survivors_before": before}
                if safe_mode:
                    entry['safety'] = {'model_class': 'temporal' if selection_space.temporal else 'static',
                                       'candidate_count': len(selection_ids), 'model_safe': True}
                probes.append(entry)
                survivors = space.survivors(fit_evidence(probes), anchors)
                entry["survivors_after"] = len(survivors)
            else:
                stop_reason = 'NO_ELIGIBLE_SAFE_PROBE' if safe_mode else 'NO_INFORMATIVE_PROBE'
                break
        else:
            word = selection_space.choose_probe(selection_ids, policy, remaining_actions, seen,
                                                seed=92821 + len(probes), safe_only=safe_mode)
            if word is None:
                stop_reason = 'NO_ELIGIBLE_SAFE_PROBE' if safe_mode else 'NO_INFORMATIVE_PROBE'
                break
            seen.add(word)
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
            if safe_mode:
                entry['safety'] = {'model_class': 'temporal' if selection_space.temporal else 'static',
                                   'candidate_count': len(selection_ids), 'model_safe': True}
            probes.append(entry)
            survivors = space.survivors(fit_evidence(probes), anchors)
            entry["survivors_after"] = len(survivors)
        if progress:
            progress(counts["target_calls"], budget, f"{len(survivors)} mappings remain")
        if error:
            stop_reason = 'INTERFACE_ERROR'
            break
        if not survivors:
            if escalate and not space.temporal:
                # Autonomous Model-Class Escalation: static refuted -> escalate to temporal
                previous_work = dict(space.work)
                space = CandidateSpace(space.machine, space.contract, temporal=True)
                # Rebuilding a larger hypothesis class does not erase the work
                # already spent refuting the smaller one.
                space.work.update(previous_work)
                survivors = space.survivors(fit_evidence(probes), anchors)
                entry["survivors_after"] = len(survivors)
                escalated = True
                escalation_history.append({"step": len(probes), "from": "static", "to": "temporal",
                                           "work_before_escalation": previous_work,
                                           "survivors_after_escalation": len(survivors)})
                if progress:
                    progress(counts["target_calls"], budget, f"Escalated to temporal model class: {len(survivors)} mappings")
                if not survivors:
                    stop_reason = 'MODEL_CONTRADICTED'
                    break
            else:
                stop_reason = 'MODEL_CONTRADICTED'
                break
    if safety_space is not space and safe_mode:
        # Count the independent envelope selection work as well as fitting and
        # any discarded static search work. No target calls are hidden here.
        for key in space.work:
            space.work[key] += safety_space.work[key]
    escalation_info = {
        "enabled": escalate,
        "escalated": escalated,
        "escalations": len(escalation_history),
        "history": escalation_history,
        "model_class": "temporal" if space.temporal else "static",
        "structural_complexity": 1 if space.temporal else 0,
        'calibration': {'mode': probe_safety, 'stop_reason': stop_reason,
                        'safety_model_class': 'temporal' if (temporal or (safe_mode and escalate)) else 'static',
                        'scope': 'Bounded probe search within the remaining call cap; model-safe means hazard-free '
                                 'under every evidence-compatible enabled model, conditional on truthful semantics.'},
    }
    return space, survivors, probes, error, escalation_info


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
    case = make_case(config.family, config.seed, config.implementation, config.split, config.anchors, config.horizon,
                     instance_seed=config.instance_seed, fault_schedule=config.fault_schedule)
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
            escalation_info = {
                "enabled": False, "escalated": False, "escalations": 0, "history": [],
                "model_class": "static", "structural_complexity": 0,
            }
        elif config.budget and config.admission != "oracle":
            target = resources.enter_context(TargetProcess(case.private))
            space, survivors, probes, error, escalation_info = _acquire(
                public, config.policy, config.budget, target.query, target.counts, cancel, progress,
                temporal=temporal, admission=config.admission, escalate=config.escalate,
                probe_safety=config.probe_safety,
                step=target.step, reset=target.reset
            )
            counts = dict(target.counts)
        else:
            space = CandidateSpace(Machine.from_dict(public["reference"]), Contract.from_dict(public["contract"]), temporal=temporal)
            survivors = space.survivors([], {int(k): int(v) for k, v in public.get("anchors", {}).items()})
            probes, error = [], None
            escalation_info = {
                "enabled": config.escalate, "escalated": False, "escalations": 0, "history": [],
                "model_class": "temporal" if space.temporal else "static",
                "structural_complexity": 1 if space.temporal else 0,
            }
        _check_cancel(cancel)
        if config.admission == "oracle":
            word = oracle_plan(case.private, config.horizon)
            decision = {"status": "ORACLE_DIAGNOSTIC", "admitted": word is not None,
                        "word": word, "candidate_count": len(survivors)}
        elif config.admission == 'adaptive':
            from .adaptive import synthesize_policy
            decision = synthesize_policy(space, survivors, cancel=cancel)
        else:
            anchors = {int(k): int(v) for k, v in public.get("anchors", {}).items()}
            decision = space.plan(survivors, config.admission, transcripts=fit_evidence(probes),
                                  anchors=anchors, risk_tolerance=config.risk_tolerance)
            if config.admission == "fit":
                baseline["fit_diagnostics"] = fit_diagnostics(space, fit_evidence(probes), anchors)
        if error:
            decision = {"status": "INTERFACE_ERROR", "admitted": False, "word": None,
                        "candidate_count": len(survivors), "error": error}
        elif config.policy == 'aalpy' and not baseline.get('model_complete') and config.admission != 'oracle':
            decision = {'status': 'UNRESOLVED', 'admitted': False, 'word': None,
                        'candidate_count': 0, 'reason': 'Budget exhausted before a complete classical model'}
        decision['calibration'] = escalation_info.pop('calibration', {
            'mode': config.probe_safety,
            'stop_reason': 'CLASSICAL_BASELINE' if config.policy == 'aalpy' else 'NOT_REQUESTED',
            'safety_model_class': 'temporal' if (config.temporal or config.escalate) else 'static',
            'scope': 'Calibration safety is conditional on the declared finite enabled model and truthful anchors.'})
        decision["escalation"] = escalation_info
        if decision["status"] == "FAMILY_CONTRADICTED" and config.escalate:
            static_count = len(space.adapters) // (1 + space.machine.outputs) if space.temporal else len(space.adapters)
            decision["structural_contradiction"] = {
                "classes_refuted": [f"static ({static_count} maps)"] +
                                   ([f"temporal ({len(space.adapters)} latency maps)"] if space.temporal else []),
                "evidence_length": len(probes),
                "scope": "No adapter in the checked finite hypothesis class can explain the public evidence."
            }
        from .certificates import check_result
        candidates = [a.to_dict() for a in space.adapters if a.id in survivors]
        evidence_certificate = check_result({
            'schema': 'crosswire-result-v1', 'configuration': asdict(config),
            'reference': public['reference'], 'contract': public['contract'],
            'anchors': public.get('anchors', {}), 'target_id': public['target_id'],
            'decision': decision, 'candidates': candidates, 'probes': probes,
        })
        if not evidence_certificate['valid']:
            raise RuntimeError('Independent public-evidence check failed: ' + evidence_certificate['reason'])
        ambiguity = space.ambiguity(survivors)
        # The digest is constructed before importing/calling the private auditor.
        frozen = canonical_hash({"decision": decision, "probes": probes, "reference": public["reference"],
                                 "contract": public["contract"], "target_id": public['target_id'],
                                 'anchors': public.get('anchors', {}), "survivors": list(survivors),
                                 'evidence_certificate': evidence_certificate})
        deployment = {'word': decision['word'], 'outputs': [], 'complete': False,
                      'mode': config.execution_mode,
                      'error': None, 'target_steps': 0, 'resets': 0, 'target_calls': 0}
        if decision['admitted']:
            _check_cancel(cancel)
            if target is None:
                target = resources.enter_context(TargetProcess(case.private))
            if config.admission == 'adaptive':
                from .adaptive import execute_policy
                deployment = execute_policy(target, decision['policy'], space, survivors, cancel,
                                            fault_schedule=config.fault_schedule,
                                            mode='recovery' if config.execution_mode == 'recovery' else 'adaptive')
            else:
                from .shield import execute_deployment
                deployment = execute_deployment(target, decision['word'], space, survivors, space.contract,
                                                mode=config.execution_mode, cancel=cancel,
                                                fault_schedule=config.fault_schedule)
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
            "candidates": candidates, "evidence_certificate": evidence_certificate,
            "probes": probes, "decision_frozen_hash": frozen, 'deployment': deployment, "audit": audit,
            "metrics": {"target_steps": counts["step_attempts"], "resets": counts["reset_attempts"],
                        "target_calls": counts["target_calls"], **work,
                        'anchor_facts_supplied': len(public.get('anchors', {})),
                        "escalations": escalation_info["escalations"],
                        "escalation_level": escalation_info["structural_complexity"],
                        "parent_cpu_seconds": time.process_time() - cpu,
                        "wall_seconds": time.perf_counter() - started, "parent_peak_traced_bytes": peak,
                        "audit_product_pairs": audit["audit_product_pairs"],
                        "audit_execution_steps": audit["audit_execution_steps"]},
            "baseline": baseline,
        }
        if 'instance_design' in public:
            result['instance_design'] = public['instance_design']
        if source_hash() != frozen_source:
            raise RuntimeError('Source changed during run; discard mixed-revision evidence')
        result["scientific_hash"] = canonical_hash(scientific_view(result))
        return result
    finally:
        resources.close()
        tracemalloc.stop()


_CONDITION_FIELDS = ('anchors', 'split', 'horizon', 'execution_mode', 'temporal', 'escalate', 'probe_safety', 'risk_tolerance')
_CONDITION_DEFAULTS = (False, 'development', 4, 'open_loop', False, False, 'unrestricted', 0.0)


def _condition(configuration: dict) -> tuple:
    """Comparable scientific conditions, with defaults for legacy row inputs."""
    return tuple(configuration.get(key, default)
                 for key, default in zip(_CONDITION_FIELDS, _CONDITION_DEFAULTS))


def summarize(rows: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    scopes = {f["id"]: f["scope"] for f in catalog()}
    for row in rows:
        cfg = row["configuration"]
        groups[(cfg["policy"] + "/" + cfg["admission"], cfg["family"], cfg["budget"],
                _condition(cfg))].append(row)
    result = []
    for (method, family, budget, conditions), members in sorted(groups.items()):
        n = len(members)
        admitted = sum(r["decision"]["admitted"] for r in members)
        success = sum(r["audit"]["contract_satisfied"] is True for r in members)
        harm = sum(r["audit"]["contract_satisfied"] is False for r in members)
        feasible = sum(r["audit"]["oracle_feasible"] for r in members)
        abstained = n - admitted
        result.append({
            "method": method, "family": family, "scope": scopes[family], "budget": budget, "requests": n,
            **dict(zip(_CONDITION_FIELDS, conditions)),
            "admitted": admitted, "successful": success, "harmful": harm,
            "hazardous": sum(r["audit"]["hazard"] is True for r in members),
            "hazards_averted": sum(r["audit"].get("hazard_averted") is True for r in members),
            "shield_interventions": sum(r["audit"].get("shield_intervened") is True for r in members),
            "calibration_hazardous_probes": sum(r['audit']['calibration_hazardous_probes'] for r in members),
            "calibration_hazardous_runs": sum(r['audit']['calibration_hazardous_probes'] > 0 for r in members),
            "mean_target_calls": sum(r['metrics']['target_calls'] for r in members) / n,
            "mean_deployment_calls": sum(r['deployment']['target_calls'] for r in members) / n,
            "mean_total_calls": sum(r['metrics']['target_calls'] + r['deployment']['target_calls'] for r in members) / n,
            "interface_errors": sum(r["decision"]["status"] == "INTERFACE_ERROR"
                                    or bool((r.get("deployment") or {}).get("error")) for r in members),
            "acquisition_interface_errors": sum(r["decision"]["status"] == "INTERFACE_ERROR" for r in members),
            "deployment_interface_errors": sum(bool((r.get("deployment") or {}).get("error")) for r in members),
            "escalated_runs": sum(r["metrics"].get("escalations", 0) > 0 for r in members),
            "recovered_runs": sum((r.get("deployment") or {}).get("recovery", {}).get("succeeded") is True for r in members),
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

    Every comparison fixes the budget, execution settings, semantic grounding,
    horizon and split. Label seeds and implementations are matched within each
    semantic parent before whole-parent resampling. Duplicate cells are refused
    instead of allowing their last value to silently determine the contrast.
    Policy pairs also fix admission; admission contrasts use robust as reference.
    """
    scopes = {f["id"]: f["scope"] for f in catalog()}
    comparisons = {'policy': defaultdict(dict), 'admission': defaultdict(dict)}
    seen = set()
    for row in rows:
        c = row["configuration"]
        # Out-of-family/control cases are never pooled into primary in-family effect.
        if scopes.get(c["family"]) != "in_family":
            continue
        conditions = _condition(c)
        cell = (c['family'], c['seed'], c['implementation'], c.get('instance_seed'))
        parent = row['parent_instance_id']
        identity = (c['budget'], conditions, parent, cell, c['policy'], c['admission'])
        if identity in seen:
            raise ValueError('Duplicate matched analysis cell; each condition/method must occur once')
        seen.add(identity)
        outcome = int(row['audit']['contract_satisfied'] is True)
        key = (c['budget'], conditions, c['admission'], parent, cell)
        comparisons['policy'][key][c['policy']] = outcome
        key = (c['budget'], conditions, c['policy'], parent, cell)
        comparisons['admission'][key][c['admission']] = outcome

    output = []
    for axis, cells in comparisons.items():
        strata = sorted({key[:3] for key in cells})
        for budget, conditions, fixed in strata:
            stratum = (budget, conditions, fixed)
            methods = sorted({method for key, values in cells.items() if key[:3] == stratum for method in values})
            if axis == 'policy':
                # Preserve task-relative signs while making arbitrary selected
                # policy pairs (e.g. entropy vs fixed) analyzable too.
                ordered = (['task'] if 'task' in methods else []) + [m for m in methods if m != 'task']
                contrasts = [(a, b) for i, a in enumerate(ordered) for b in ordered[i + 1:]]
            else:
                contrasts = [('robust', m) for m in methods if m != 'robust']
            for reference, method in contrasts:
                per_parent = defaultdict(list)
                families = set()
                for key, values in cells.items():
                    if key[:3] != stratum or reference not in values or method not in values:
                        continue
                    parent, cell = key[3:]
                    difference = values[reference] - values[method]
                    per_parent[parent].append(difference if axis == 'policy' else -difference)
                    families.add(cell[0])
                if not per_parent:
                    continue
                delta = [sum(v) / len(v) for _, v in sorted(per_parent.items())]
                rng = random.Random(68219)
                draws = sorted(sum(rng.choice(delta) for _ in delta) / len(delta) for _ in range(2000))
                output.append({
                    'contrast': f'{reference} - {method}' if axis == 'policy' else f'{method} - robust',
                    'comparison_axis': axis,
                    'fixed_admission' if axis == 'policy' else 'fixed_policy': fixed,
                    'outcome': 'useful_coverage', 'budget': budget,
                    **dict(zip(_CONDITION_FIELDS, conditions)),
                    'budget_unit': 'target calls (resets + actions)',
                    'parent_clusters': len(delta),
                    'matched_cells': sum(len(v) for v in per_parent.values()),
                    'families_pooled': sorted(families),
                    'mean_delta': sum(delta) / len(delta),
                    'descriptive_95_interval': [draws[49], draws[1949]],
                    'scope': 'exploratory parent-cluster paired bootstrap within identical call cap and conditions; '
                             'in-family fixtures pooled; few clusters, no confirmatory claim',
                })
    return output


STUDY_DEFAULTS = {"families": ["latch", "symmetric", "neutral"], "seeds": [17], "budgets": [0, 8],
                  "policies": ["random", "task"], "admissions": ["robust"], "implementations": ["procedural"],
                  'instance_seeds': [None]}


def study_configs(spec: dict) -> list[RunConfig]:
    if not isinstance(spec, dict):
        raise ValueError("Study must be an object")
    allowed = {"families", "seeds", "budgets", "policies", "admissions", "implementations",
               "anchors", "split", "horizon", "execution_mode", "temporal", "escalate", "probe_safety", "risk_tolerance",
               'instance_seeds'}
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
    configs = [RunConfig.from_dict(dict(zip(("family", "seed", "budget", "policy", "admission", "implementation", 'instance_seed'), values),
                                         anchors=spec.get("anchors", False), split=spec.get("split", "development"),
                                         horizon=spec.get("horizon", 4),
                                         execution_mode=spec.get("execution_mode", "open_loop"),
                                         temporal=spec.get("temporal", False),
                                         escalate=spec.get("escalate", False),
                                         probe_safety=spec.get('probe_safety', 'unrestricted'),
                                         risk_tolerance=spec.get('risk_tolerance', 0.0))) for values in product(*dimensions)]
    if len({canonical_hash(asdict(cfg)) for cfg in configs}) != len(configs):
        raise ValueError('Duplicate effective study configuration; null generated instance and zero are identical')
    return configs


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
    from .reliability import reliability_summary
    value['reliability'] = reliability_summary(rows)
    value["scientific_hash"] = canonical_hash(scientific_view(value))
    if progress:
        progress(len(configs), len(configs), "Complete; decisions and private audits recorded")
    return value
