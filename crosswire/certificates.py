"""Independent finite public-evidence checking, without targets or private audit.

This module deliberately does not use CandidateSpace, its caches, its planner,
or the adaptive synthesizer/checker. A valid report checks supplied observations
under a declared model; it does not authenticate them or establish semantics.
"""
from __future__ import annotations

from itertools import permutations, product

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
        anchors = result.get('anchors', {})
        if not isinstance(anchors, dict):
            raise ValueError('Anchors must be an object')
        for raw, semantic in anchors.items():
            if isinstance(raw, str) and raw in {str(i) for i in range(machine.outputs)}:
                raw = int(raw)
            raw = _int(raw, machine.outputs, 'anchor raw output')
            semantic = _int(semantic, machine.outputs, 'anchor semantic output')
            allowed = {a['id'] for a in adapters if a['output_map'][semantic] == raw}
            constraints.append(({'kind': 'anchor', 'raw': raw, 'semantic': semantic}, allowed))
        # Canonical order ensures a certificate survives JSON key normalization.
        constraints.sort(key=lambda pair: (pair[0]['raw'], pair[0]['semantic']))
        probes = result['probes']
        if not isinstance(probes, list) or len(probes) > 512:
            raise ValueError('Invalid or oversized probe collection')
        for index, probe in enumerate(probes):
            if not isinstance(probe, dict) or type(probe.get('complete')) is not bool:
                raise ValueError('Probe must declare boolean completeness')
            word = _sequence(probe['word'], machine.inputs, 'probe word')
            outputs = _sequence(probe['outputs'], machine.outputs, 'probe outputs')
            if len(outputs) > len(word) or (probe['complete'] and len(word) != len(outputs)):
                raise ValueError('Probe word/output lengths differ')
            if not outputs:
                continue
            word = word[:len(outputs)]
            allowed = {a['id'] for a in adapters if _trace(machine, a, word)[0] == outputs}
            constraints.append(({'kind': 'probe', 'index': index, 'word': list(word),
                                 'outputs': list(outputs)}, allowed))

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
        if admission not in ('robust', 'adaptive', 'unique', 'one_best', 'fit', 'identity', 'oracle', 'abstain'):
            raise ValueError('Unknown admission rule')
        diagnostic = baseline or admission in ('one_best', 'fit', 'identity', 'oracle')
        report.update(model_class=model_class, checked_adapters=len(adapters), candidate_count=len(survivors),
                      evidence_count=len(constraints), elimination=elimination)
        status = decision['status']
        if status not in ('IDENTIFIED', 'TASK_ADMISSIBLE', 'ADAPTIVE_ADMISSIBLE', 'FAMILY_CONTRADICTED',
                          'UNRESOLVED', 'SEARCH_LIMIT', 'INTERFACE_ERROR', 'ORACLE_DIAGNOSTIC'):
            raise ValueError('Unknown decision status')
        if diagnostic:
            report.update(kind='diagnostic', reason='Diagnostic baseline; no all-candidate admission guarantee')
        elif decision['admitted']:
            if not survivors or admission == 'abstain':
                raise ValueError('Empty or abstaining belief cannot certify admission')
            if admission == 'unique' and len(survivors) != 1:
                raise ValueError('Unique admission requires one surviving adapter')
            if status not in ('IDENTIFIED', 'TASK_ADMISSIBLE', 'ADAPTIVE_ADMISSIBLE'):
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
            if status in ('IDENTIFIED', 'TASK_ADMISSIBLE', 'ADAPTIVE_ADMISSIBLE'):
                raise ValueError('Positive decision status conflicts with abstention')
            report.update(kind='unresolved', reason='No positive admission claim; not a proof of impossibility')
        report['binding_hash'] = canonical_hash({key: result.get(key) for key in
                                                ('reference', 'contract', 'anchors', 'probes', 'candidates',
                                                 'decision', 'configuration', 'target_id')})
        report['valid'] = True
    except (KeyError, TypeError, ValueError, AttributeError, IndexError, RecursionError, OverflowError) as exc:
        report.update(valid=False, reason=str(exc))
    return report
