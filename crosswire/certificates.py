"""Independent finite public-evidence checking, without targets or private audit.

This module deliberately does not use CandidateSpace, its caches, its planner,
or the adaptive synthesizer/checker. A valid report checks supplied observations
under a declared model; it does not authenticate them or establish semantics.
"""
from __future__ import annotations

from itertools import permutations, product
import math

from .core import Contract, Machine
from .identity import canonical_hash


SCOPE = ('Finite public-model evidence only; conditional on target inclusion, stationarity, '
         'deterministic reset and truthful anchors; does not authenticate observations, '
         'validate private audit/runtime accounting, or establish real-world safety.')


def _int(value, limit, name):
    if type(value) is not int or not 0 <= value < limit:
        raise ValueError(f'Invalid {name}')
    return value


def _sequence(value, limit, name):
    if not isinstance(value, (list, tuple)) or len(value) > 512:
        raise ValueError(f'Invalid or oversized {name}')
    return tuple(_int(v, limit, name) for v in value)


def _fraction(value, name, upper_inclusive=False):
    if (type(value) not in (int, float) or value < 0
            or (value > 1 if upper_inclusive else value >= 1) or not math.isfinite(value)):
        raise ValueError(f'Invalid {name}: expected a finite numeric fraction')
    return value


def _adapters(machine, temporal):
    pairs = list(product(permutations(range(machine.inputs)), permutations(range(machine.outputs))))
    result = [{'id': i, 'input_map': list(a), 'output_map': list(b)} for i, (a, b) in enumerate(pairs)]
    if temporal:
        for a, b in pairs:
            for initial in range(machine.outputs):
                result.append({'id': len(result), 'input_map': list(a), 'output_map': list(b),
                               'delay': 1, 'init_output': initial})
    return result


def _trace(machine, adapter, word):
    state = machine.initial
    semantics, raw = [], []
    buffered = adapter.get('init_output', 0)
    for action in word:
        state, semantic = machine.transitions[state][adapter['input_map'][action]]
        semantics.append(semantic)
        raw.append(adapter['output_map'][buffered if adapter.get('delay') else semantic])
        buffered = semantic
    return tuple(raw), tuple(semantics)


def _reset_consistency(probes):
    """Check equal reset action prefixes without assuming the reference model.

    A trie shares action prefixes, so long observations do not require storing
    a separate tuple for every prefix. Only the first conflict carries its word.
    """
    nodes = [{'children': {}, 'observation': None}]
    repeated, conflicts, first = 0, 0, None
    for index, (word, outputs) in enumerate(probes):
        current = 0
        for offset, (action, output) in enumerate(zip(word, outputs)):
            children = nodes[current]['children']
            if action not in children:
                children[action] = len(nodes)
                nodes.append({'children': {}, 'observation': None})
            current = children[action]
            previous = nodes[current]['observation']
            if previous is None:
                nodes[current]['observation'] = (output, index)
                continue
            repeated += 1
            if previous[0] != output:
                conflicts += 1
                if first is None:
                    first = {'probe_index': index, 'step': offset + 1,
                             'word_prefix': list(word[:offset + 1]),
                             'observed_output': output, 'previous_output': previous[0],
                             'previous_probe_index': previous[1]}
    return {'status': 'REFUTED' if conflicts else 'UNKNOWN',
            'repeated_prefix_observations': repeated,
            'conflicting_prefix_observations': conflicts, 'first_conflict': first,
            'scope': 'Equal action prefixes after reset must have equal raw outputs in a '
                     'stationary deterministic target with reliable resets. A conflict '
                     'does not identify drift, stochasticity or reset failure as its cause; '
                     'absence of a conflict does not establish those assumptions.'}


def _model_diagnostics(machine, anchors, probes, temporal):
    """Replay public forecasts using only evidence preceding each observation.

    Every enabled class is checked from the beginning, independently of the
    acquisition class or a diagnostic baseline's selected model. Predictions
    are computed once per live model and observed word, never once per prefix.
    No private target information or CandidateSpace machinery enters here.
    """
    enabled = ['static', 'temporal'] if temporal else ['static']
    adapters = _adapters(machine, temporal)
    classes, beliefs = {}, {}
    total_symbols = sum(len(outputs) for _, outputs in probes)
    for name in enabled:
        belief = {a['id'] for a in adapters if name == 'temporal' or not a.get('delay')}
        model_count = len(belief)
        first_refutation = None
        for raw, semantic in anchors:
            before = len(belief)
            belief = {i for i in belief if adapters[i]['output_map'][semantic] == raw}
            if before and not belief:
                first_refutation = {'kind': 'anchor', 'raw': raw, 'semantic': semantic,
                                    'survivors_before': before, 'survivors_after': 0}
        beliefs[name] = belief
        classes[name] = {'inclusion_status': 'UNKNOWN' if belief else 'REFUTED',
                         'model_count': model_count, 'models_after_anchors': len(belief),
                         'candidate_count': len(belief), 'scored_symbols': 0,
                         'unscored_symbols': total_symbols,
                         'first_refutation': first_refutation, 'events': []}
    for index, (word, outputs) in enumerate(probes):
        if not outputs:
            continue
        # Static models are shared with the temporal envelope. Trace their
        # union once for this observed word, without quadratic prefix replay.
        live_ids = set().union(*beliefs.values())
        predictions = {i: _trace(machine, adapters[i], word)[0] for i in live_ids}
        for name in enabled:
            belief, diagnostic = beliefs[name], classes[name]
            # Full deterministic traces may be computed up front, but support
            # at offset t is counted before filtering on observation t.
            for offset, (action, output) in enumerate(zip(word, outputs)):
                before = len(belief)
                counts = {}
                for i in belief:
                    prediction = predictions[i][offset]
                    counts[prediction] = counts.get(prediction, 0) + 1
                supported = output in counts
                belief = {i for i in belief if predictions[i][offset] == output}
                event = {'probe_index': index, 'step': offset + 1, 'action': action,
                         'predicted_output_counts': {str(raw): counts[raw] for raw in sorted(counts)},
                         'observed_output': output, 'survivors_before': before,
                         'survivors_after': len(belief),
                         'prediction_status': ('SUPPORTED' if supported else 'UNSUPPORTED')
                         if before else 'UNSCORED'}
                diagnostic['events'].append(event)
                if before:
                    diagnostic['scored_symbols'] += 1
                    if not belief:
                        diagnostic['first_refutation'] = {'kind': 'probe', **event,
                                                          'word_prefix': list(word[:offset + 1])}
            beliefs[name] = belief
            diagnostic.update(inclusion_status='UNKNOWN' if belief else 'REFUTED',
                              candidate_count=len(belief),
                              unscored_symbols=total_symbols - diagnostic['scored_symbols'])
    return {'schema': 'crosswire-model-diagnostics-v1',
            'inclusion_status': 'UNKNOWN' if any(c['candidate_count'] for c in classes.values()) else 'REFUTED',
            'enabled_classes': enabled, 'classes': classes,
            'observed_symbols': total_symbols,
            'reset_consistency': _reset_consistency(probes),
            'scope': 'Calibration observations and supplied anchors only. UNKNOWN means '
                     'not refuted by the observed evidence, including when a task is admitted; '
                     'it never establishes actual model inclusion. REFUTED means every enabled '
                     'finite class is inconsistent. Each forecast uses only earlier evidence; '
                     'outputs after class refutation are unscored. No extra target calls are made.',
            'blind_spots': [
                'Raw-equivalent semantic corruption, hidden privileged paths and semantic-only drift can remain undetected.',
                'Unqueried action branches and behavior deeper than observed prefixes remain unknown.',
                'Agreement does not authenticate observations, reset reliability or semantic anchors.',
                'Prediction support counts are finite model counts, not calibrated probabilities or real-world safety bounds.',
            ]}


def check_result(result: dict) -> dict:
    """Recompute an evidence certificate; never trust a stored certificate/hash.

    Diagnostic baselines may deliberately restrict the evidence-compatible set.
    Their report validates that declaration but makes no admission safety claim.
    Unresolved means no positive claim was made, not a proof of impossibility.
    """
    report = {'schema': 'crosswire-evidence-certificate-v1', 'valid': False,
              'kind': 'unresolved', 'scope': SCOPE}
    try:
        if not isinstance(result, dict) or result.get('schema') != 'crosswire-result-v1':
            raise ValueError('Expected one completed run result')
        machine = Machine.from_dict(result['reference'])
        contract = Contract.from_dict(result['contract'])
        if machine.inputs > 3 or machine.outputs > 4 or len(machine.transitions) > 128:
            raise ValueError('Reference exceeds the bounded checker alphabet/state limits')
        if max(contract.goal, contract.hazard) >= machine.outputs:
            raise ValueError('Contract output outside reference alphabet')
        decision, config = result['decision'], result['configuration']
        if not isinstance(decision, dict) or not isinstance(config, dict):
            raise ValueError('Invalid configuration or decision')
        safety_mode = config.get('probe_safety', 'unrestricted')
        if safety_mode not in ('unrestricted', 'model_safe'):
            raise ValueError('Unknown calibration safety mode')
        tolerance = _fraction(config.get('risk_tolerance', 0.0), 'configured risk tolerance')
        if tolerance and config.get('admission') != 'risk_controlled':
            raise ValueError('Positive risk tolerance requires risk_controlled admission')
        if safety_mode == 'model_safe' and config.get('policy') == 'aalpy':
            raise ValueError('Classical learner does not support model-safe calibration')
        temporal = config.get('temporal', False)
        if type(temporal) is not bool:
            raise ValueError('Invalid temporal setting')
        model_class = decision.get('escalation', {}).get('model_class', 'temporal' if temporal else 'static')
        if model_class not in ('static', 'temporal'):
            raise ValueError('Unknown model class')
        if temporal and model_class != 'temporal':
            raise ValueError('Declared model class conflicts with configuration')
        if model_class == 'temporal' and not (temporal or config.get('escalate') is True):
            raise ValueError('Temporal class was not enabled')
        adapters = _adapters(machine, model_class == 'temporal')
        all_ids = set(range(len(adapters)))
        constraints = []
        normalized_anchors = []
        anchors = result.get('anchors', {})
        if not isinstance(anchors, dict):
            raise ValueError('Anchors must be an object')
        for raw, semantic in anchors.items():
            if isinstance(raw, str) and raw in {str(i) for i in range(machine.outputs)}:
                raw = int(raw)
            raw = _int(raw, machine.outputs, 'anchor raw output')
            semantic = _int(semantic, machine.outputs, 'anchor semantic output')
            normalized_anchors.append((raw, semantic))
            allowed = {a['id'] for a in adapters if a['output_map'][semantic] == raw}
            constraints.append(({'kind': 'anchor', 'raw': raw, 'semantic': semantic}, allowed))
        # Canonical order ensures a certificate survives JSON key normalization.
        constraints.sort(key=lambda pair: (pair[0]['raw'], pair[0]['semantic']))
        normalized_anchors.sort()
        safety_temporal = temporal or config.get('escalate') is True
        safety_adapters = (_adapters(machine, safety_temporal) if safety_mode == 'model_safe' else [])
        safety_belief = set(range(len(safety_adapters)))
        for raw, semantic in anchors.items():
            safety_belief = {i for i in safety_belief if safety_adapters[i]['output_map'][semantic] == int(raw)}
        probes = result['probes']
        if not isinstance(probes, list) or len(probes) > 512:
            raise ValueError('Invalid or oversized probe collection')
        observed_probes = []
        for index, probe in enumerate(probes):
            if not isinstance(probe, dict) or type(probe.get('complete')) is not bool:
                raise ValueError('Probe must declare boolean completeness')
            word = _sequence(probe['word'], machine.inputs, 'probe word')
            outputs = _sequence(probe['outputs'], machine.outputs, 'probe outputs')
            if len(outputs) > len(word) or (probe['complete'] and len(word) != len(outputs)):
                raise ValueError('Probe word/output lengths differ')
            observed_probes.append((word[:len(outputs)], outputs))
            if safety_mode == 'model_safe':
                if not word or not safety_belief or any(
                        contract.hazard in _trace(machine, safety_adapters[i], word)[1] for i in safety_belief):
                    raise ValueError('Unsafe calibration query under a pre-probe surviving model')
                declared = probe.get('safety')
                expected_safety = {'model_class': 'temporal' if safety_temporal else 'static',
                                   'candidate_count': len(safety_belief), 'model_safe': True}
                if declared is not None and canonical_hash(declared) != canonical_hash(expected_safety):
                    raise ValueError('Calibration safety metadata differs from pre-probe evidence')
                if outputs:
                    safety_belief = {i for i in safety_belief
                                     if _trace(machine, safety_adapters[i], word[:len(outputs)])[0] == outputs}
            if not outputs:
                continue
            word = word[:len(outputs)]
            allowed = {a['id'] for a in adapters if _trace(machine, a, word)[0] == outputs}
            constraints.append(({'kind': 'probe', 'index': index, 'word': list(word),
                                 'outputs': list(outputs)}, allowed))
        report['calibration_safety'] = {
            'mode': safety_mode, 'checked_probes': len(probes) if safety_mode == 'model_safe' else 0,
            'safe': True if safety_mode == 'model_safe' else None,
            'model_class': 'temporal' if safety_temporal else 'static',
            'scope': 'Entire dispatched words checked before their outputs, including interrupted suffixes. '
                     'Conditional on enabled model inclusion, stationarity, reset semantics and truthful anchors; '
                     'unrestricted calibration makes no safety claim.'}
        report['model_diagnostics'] = _model_diagnostics(
            machine, normalized_anchors, observed_probes, safety_temporal)

        survivors = set(all_ids)
        elimination = []
        for evidence, allowed in constraints:
            before = len(survivors)
            survivors &= allowed
            elimination.append({**evidence, 'before': before, 'after': len(survivors)})
        expected = [a for a in adapters if a['id'] in survivors]
        candidates = result['candidates']
        if not isinstance(candidates, list):
            raise ValueError('Candidates must be a list')
        # Compare canonical JSON so bool/int aliases cannot pass Python equality.
        baseline = config.get('policy') == 'aalpy' and config.get('admission') != 'oracle'
        if baseline:
            ids = []
            for candidate in candidates:
                identifier = _int(candidate['id'], len(adapters), 'candidate id')
                if identifier not in survivors or canonical_hash(candidate) != canonical_hash(adapters[identifier]):
                    raise ValueError('Classical-model candidate contradicts public evidence')
                ids.append(identifier)
            if ids != sorted(set(ids)):
                raise ValueError('Duplicate or unordered candidate list')
        elif canonical_hash(candidates) != canonical_hash(expected):
            raise ValueError('Declared candidates are not the complete evidence-compatible set')
        _int(decision['candidate_count'], len(adapters) + 1, 'candidate count')
        if decision['candidate_count'] != len(candidates):
            raise ValueError('Decision candidate count does not match the evidence')
        if type(decision['admitted']) is not bool:
            raise ValueError('Admission must be boolean')
        admission = config.get('admission', 'robust')
        if admission not in ('robust', 'adaptive', 'unique', 'one_best', 'fit', 'identity', 'oracle', 'abstain', 'risk_controlled'):
            raise ValueError('Unknown admission rule')
        diagnostic = baseline or admission in ('one_best', 'fit', 'identity', 'oracle')
        report.update(model_class=model_class, checked_adapters=len(adapters), candidate_count=len(survivors),
                      evidence_count=len(constraints), elimination=elimination)
        status = decision['status']
        if status not in ('IDENTIFIED', 'TASK_ADMISSIBLE', 'ADAPTIVE_ADMISSIBLE', 'RISK_CONTROLLED_ADMISSIBLE',
                          'FAMILY_CONTRADICTED', 'UNRESOLVED', 'SEARCH_LIMIT', 'INTERFACE_ERROR', 'ORACLE_DIAGNOSTIC'):
            raise ValueError('Unknown decision status')
        if admission == 'risk_controlled' and not decision['admitted'] and 'risk_metrics' in decision:
            metrics = decision['risk_metrics']
            if _fraction(metrics['tolerance'], 'reported risk tolerance') != tolerance:
                raise ValueError('Reported risk tolerance differs from configuration')
            if metrics['hazard_risk'] is not None or metrics['goal_rate'] is not None or decision.get('word') is not None:
                raise ValueError('No selected plan: hazard/goal fractions must be undefined')
        if diagnostic:
            report.update(kind='diagnostic', reason='Diagnostic baseline; no all-candidate admission guarantee')
        elif decision['admitted']:
            if not survivors or admission == 'abstain':
                raise ValueError('Empty or abstaining belief cannot certify admission')
            if admission == 'unique' and len(survivors) != 1:
                raise ValueError('Unique admission requires one surviving adapter')
            if status not in ('IDENTIFIED', 'TASK_ADMISSIBLE', 'ADAPTIVE_ADMISSIBLE', 'RISK_CONTROLLED_ADMISSIBLE'):
                raise ValueError('Admission conflicts with decision status')
            checked_nodes = 0

            def check_prefix(word, belief, terminal=False):
                traces = {i: _trace(machine, adapters[i], word) for i in belief}
                for _, semantic in traces.values():
                    if contract.hazard in semantic:
                        raise ValueError('Admitted action risks a hazard under a surviving model')
                    if terminal and (not semantic or semantic[-1] != contract.goal):
                        raise ValueError('Admitted terminal does not achieve every surviving goal')
                return traces

            def visit(node, belief, prefix):
                nonlocal checked_nodes
                checked_nodes += 1
                if checked_nodes > 20000 or not isinstance(node, dict):
                    raise ValueError('Invalid or oversized policy')
                if set(node) == {'stop'} and node['stop'] is True:
                    check_prefix(prefix, belief, terminal=True)
                    return
                if set(node) != {'action', 'branches'} or len(prefix) >= contract.horizon:
                    raise ValueError('Malformed policy or exhausted horizon')
                action = _int(node['action'], machine.inputs, 'policy action')
                word = prefix + (action,)
                partitions = {}
                for i, (raw, _) in check_prefix(word, belief).items():
                    partitions.setdefault(str(raw[-1]), set()).add(i)
                if not isinstance(node['branches'], dict) or set(node['branches']) != set(partitions):
                    raise ValueError('Policy branches do not cover exactly the possible outputs')
                for raw, members in sorted(partitions.items()):
                    visit(node['branches'][raw], members, word)

            if admission == 'adaptive':
                if decision.get('word') is not None:
                    raise ValueError('Adaptive policy must not claim a fixed word')
                visit(decision['policy'], survivors, ())
                report.update(kind='admission', checked_policy_nodes=checked_nodes,
                              reason='Every surviving interpretation satisfies the declared finite contract')
            elif admission == 'risk_controlled':
                risk_metrics = decision.get('risk_metrics', {})
                declared_tolerance = _fraction(risk_metrics['tolerance'], 'reported risk tolerance')
                if declared_tolerance != tolerance:
                    raise ValueError('Reported risk tolerance differs from configuration')
                word = _sequence(decision['word'], machine.inputs, 'admitted word')
                if not 1 <= len(word) <= contract.horizon:
                    raise ValueError('Admitted word exceeds the contract horizon')
                traces = {i: _trace(machine, adapters[i], word) for i in survivors}
                h_count = sum(contract.hazard in semantic for _, semantic in traces.values())
                g_count = sum(bool(semantic and semantic[-1] == contract.goal and contract.hazard not in semantic)
                              for _, semantic in traces.values())
                h_risk = h_count / len(survivors)
                g_rate = g_count / len(survivors)
                reported_hazard = _fraction(risk_metrics['hazard_risk'], 'reported hazard fraction', True)
                reported_goal = _fraction(risk_metrics['goal_rate'], 'reported goal fraction', True)
                if reported_hazard != h_risk or reported_goal != g_rate:
                    raise ValueError('Reported hazard/goal fractions differ from independently computed candidate fractions')
                if 'candidate_count' in risk_metrics and (
                        type(risk_metrics['candidate_count']) is not int or risk_metrics['candidate_count'] != len(survivors)):
                    raise ValueError('Risk metric candidate count differs from evidence')
                if h_risk > tolerance or (len(survivors) - g_count) / len(survivors) > tolerance:
                    raise ValueError(f'Admitted word violates risk tolerance: hazard_risk={h_risk}, goal_rate={g_rate}, tolerance={tolerance}')
                report.update(kind='risk_controlled' if tolerance > 0 else 'admission',
                              risk_metrics={'hazard_risk': h_risk, 'goal_rate': g_rate, 'tolerance': tolerance},
                              reason=f'Uniform candidate fractions checked: hazard={h_risk:.4f} <= {tolerance}, goal={g_rate:.4f}; '
                                     'not a calibrated real-world risk bound')
            else:
                word = _sequence(decision['word'], machine.inputs, 'admitted word')
                if not 1 <= len(word) <= contract.horizon:
                    raise ValueError('Admitted word exceeds the contract horizon')
                check_prefix(word, survivors, terminal=True)
                report.update(kind='admission', checked_policy_nodes=checked_nodes,
                              reason='Every surviving interpretation satisfies the declared finite contract')
        elif status == 'FAMILY_CONTRADICTED':
            if survivors:
                raise ValueError('Contradiction claimed while consistent adapters remain')
            # Deletion-minimal, not globally minimum-cardinality. Removing any one
            # retained constraint makes this core satisfiable in the finite class.
            core = list(range(len(constraints)))
            for remove in reversed(core[:]):
                remaining = set(all_ids)
                for index in core:
                    if index != remove:
                        remaining &= constraints[index][1]
                if not remaining:
                    core.remove(remove)
            report.update(kind='contradiction', contradiction_core=[constraints[i][0] for i in core],
                          core_irreducible=True, reason='Public evidence refutes the entire declared finite class')
        else:
            if status in ('IDENTIFIED', 'TASK_ADMISSIBLE', 'ADAPTIVE_ADMISSIBLE', 'RISK_CONTROLLED_ADMISSIBLE'):
                raise ValueError('Positive decision status conflicts with abstention')
            report.update(kind='unresolved', reason='No positive admission claim; not a proof of impossibility')
        report['binding_hash'] = canonical_hash({key: result.get(key) for key in
                                                ('reference', 'contract', 'anchors', 'probes', 'candidates',
                                                 'decision', 'configuration', 'target_id')})
        report['valid'] = True
    except (KeyError, TypeError, ValueError, AttributeError, IndexError, RecursionError, OverflowError) as exc:
        report.update(valid=False, reason=str(exc))
    return report
