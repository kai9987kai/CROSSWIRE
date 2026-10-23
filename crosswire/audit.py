"""Private post-decision evaluation, never used to choose ordinary probes/plans."""
from __future__ import annotations

from .core import CandidateSpace, compare_adapter, words
from .fixtures import Case, catalog, evaluate_deployment, target_machine
from .identity import canonical_hash


def evaluate(case: Case, space: CandidateSpace, survivors: tuple[int, ...], decision: dict, probes: list[dict], deployment: dict) -> dict:
    private = case.private
    work = {'resets': 0, 'steps': 0}
    model = target_machine(private, work=work)
    equivalent = []
    counterexamples = []
    visited = 0
    reference_steps = target_model_steps = 0
    if model is not None:
        for adapter in space.adapters:
            check = compare_adapter(space.machine, adapter, model)
            visited += check["visited_pairs"]
            reference_steps += check.get('source_steps', 0)
            target_model_steps += check.get('target_model_steps', 0)
            if check["equivalent"]:
                equivalent.append(adapter.id)
            else:
                counterexamples.append({"adapter_id": adapter.id, "word": check["counterexample"]})
    actual = None
    deployment_audit = None
    counterfactual_hazard = False
    if decision["admitted"]:
        # Execution evidence owns the audited trajectory. A contingent policy
        # or recovery can dispatch a different word from the initial request.
        plan = (deployment['executed_word'] if 'executed_word' in deployment else
                decision['policy'] if decision.get('word') is None else decision['word'])
        if deployment['complete']:
            actual = evaluate_deployment(private, probes, plan, work=work)
            reproduced = actual['outputs'] == deployment['outputs']
            if not reproduced:
                actual = {**actual, 'goal_success': False, 'contract_satisfied': False}
            executed_len = len(deployment['outputs'])
            deployment_audit = {'completed': True, 'executed_prefix_length': executed_len,
                                'reconstruction_matches_observed': reproduced, 'prefix_hazard': actual['hazard'],
                                'counterfactual_hazard': actual['hazard']}
        else:
            # Only the successfully executed prefix happened. Fixture faults
            # fail before the engine steps, so the failed call emitted no event.
            # The unexecuted suffix is never simulated as if it occurred.
            executed = list((deployment.get('executed_word', decision.get('word')) or ())[:len(deployment['outputs'])])
            prefix = (evaluate_deployment(private, probes, executed, work=work) if executed
                      else {'outputs': [], 'semantic_events': [], 'hazard': False})
            hazard_key = private['contract']['hazard']
            prefix_hazard = hazard_key in prefix['semantic_events']
            actual = {'outputs': prefix['outputs'], 'semantic_events': prefix['semantic_events'],
                      'goal_success': False, 'contract_satisfied': False,
                      # Observed prefix hazard is evidence; absence is not proof of safety.
                      'hazard': True if prefix_hazard else None}
            # Counterfactual audit: would the full unshielded plan have triggered a hazard?
            if decision.get("word") is not None:
                counterfactual = evaluate_deployment(private, probes, decision["word"], work=work)
                counterfactual_hazard = bool(counterfactual.get('hazard', False))
            else:
                counterfactual_hazard = False
            deployment_audit = {'completed': False, 'executed_prefix_length': len(executed),
                                'reconstruction_matches_observed': prefix['outputs'] == deployment['outputs'],
                                'prefix_hazard': prefix_hazard, 'counterfactual_hazard': counterfactual_hazard,
                                'error_code': (deployment.get('error') or {}).get('code')}
    oracle = None
    oracle_candidates = 0
    if private.get('family') != 'malformed':
        for candidate_word in words(space.machine.inputs, space.contract.horizon):
            oracle_candidates += 1
            if evaluate_deployment(private, probes, candidate_word, work=work)['contract_satisfied']:
                oracle = list(candidate_word)
                break
    planted = next((a.id for a in space.adapters
                    if tuple(private.get("input_map", ())) == a.input_map
                    and tuple(private.get("output_map", ())) == a.output_map), None)
    # A raw planted code need not be a true semantic interpretation after corruption.
    in_family = any(item['id'] == private.get('family') and item['scope'] == 'in_family'
                    for item in catalog())
    calibration_hazards = 0
    for i, probe in enumerate(probes):
        executed = probe['word'][:len(probe['outputs'])]
        if not executed:
            continue
        try:
            item = evaluate_deployment(private, probes[:i], executed, work=work)
            calibration_hazards += int(item["hazard"])
        except (ValueError, RuntimeError):
            pass
    if model is None:
        scope = "No finite stationary target model available; equivalence is unresolved."
    else:
        model_class = 'static plus latency-1 temporal' if space.temporal else 'static'
        scope = (f"Exact raw equivalence within the declared {len(space.adapters)}-map {model_class} finite class only; "
                 "latent semantics are not established by raw equivalence.")
    causal_hazard_averted = bool(deployment.get("intervened") and counterfactual_hazard and (actual.get("hazard") is not True))
    return {
        "goal_success": actual["goal_success"] if actual else None,
        "hazard": actual["hazard"] if actual else None,
        "hazard_averted": causal_hazard_averted if actual else None,
        "shield_intervened": bool(deployment.get("intervened", False)) if actual else None,
        "contract_satisfied": actual["contract_satisfied"] if actual else None,
        "outputs": actual["outputs"] if actual else [],
        "semantic_events": actual["semantic_events"] if actual else [],
        "deployment_audit": deployment_audit,
        "oracle_feasible": oracle is not None, "oracle_word": oracle,
        "true_map_retained": planted in survivors if in_family and planted is not None else None,
        "planted_raw_map_retained": planted in survivors if planted is not None else None,
        "raw_equivalent_maps_count": len(equivalent) if model is not None else None,
        "raw_equivalent_map_ids": equivalent,
        "no_map_in_class": not equivalent if model is not None else None,
        "maps_checked": len(space.adapters) if model is not None else 0,
        "counterexample": min((e["word"] for e in counterexamples), key=lambda w: (len(w), w), default=None),
        "counterexamples_hash": canonical_hash(counterexamples),
        'counterexample_scope': 'Witness rejecting an alternative raw map; not a violation of the admitted task plan',
        "audit_product_pairs": visited, "audit_execution_steps": work['steps'],
        'audit_reference_steps': reference_steps, 'audit_target_model_steps': target_model_steps,
        'audit_resets': work['resets'], 'audit_oracle_word_candidates': oracle_candidates,
        "calibration_hazardous_probes": calibration_hazards,
        "assumption_limits": scope,
    }
