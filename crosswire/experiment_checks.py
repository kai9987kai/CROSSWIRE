"""Independent finite checks for bounded, reset-separated experiment trees.

Only canonical content hashing is shared with the scientific runtime. Candidate
enumeration, reference execution, belief updates and goal checks are reconstructed
here without importing candidate spaces, experiment search or adaptive planners.
"""
from __future__ import annotations

from itertools import permutations, product
import json

from .identity import canonical_hash


SCOPE = ('Conditional finite public-model check: assumes target inclusion, stationarity, '
         'deterministic resets and truthful anchors. Does not authenticate observations '
         'or target execution, validate private audits, or establish semantic grounding. '
         'Model counts are not calibrated probabilities; unresolved leaves make no '
         'impossibility claim.')


def _integer(value, maximum, name, minimum=0):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f'Invalid {name}: expected an integer in {minimum}..{maximum}')
    return value


def _sequence(value, alphabet, name, maximum=512):
    if not isinstance(value, (list, tuple)) or len(value) > maximum:
        raise ValueError(f'Invalid or oversized {name}')
    return tuple(_integer(symbol, alphabet - 1, name) for symbol in value)


def _public_model(reference, contract):
    if (not isinstance(reference, dict) or set(reference) -
            {'name', 'transitions', 'inputs', 'outputs', 'initial'}):
        raise ValueError('Invalid public reference')
    name = reference['name']
    if not isinstance(name, str) or not name:
        raise ValueError('Reference name must be a nonempty string')
    inputs = _integer(reference.get('inputs', 3), 3, 'reference inputs', 1)
    outputs = _integer(reference.get('outputs', 4), 4, 'reference outputs', 1)
    rows = reference['transitions']
    if not isinstance(rows, (list, tuple)) or not 1 <= len(rows) <= 128:
        raise ValueError('Reference must contain 1..128 states')
    initial = _integer(reference.get('initial', 0), len(rows) - 1, 'initial state')
    transitions = []
    for row in rows:
        if not isinstance(row, (list, tuple)) or len(row) != inputs:
            raise ValueError('Reference transition row does not match input alphabet')
        checked_row = []
        for cell in row:
            if not isinstance(cell, (list, tuple)) or len(cell) != 2:
                raise ValueError('Reference transition needs a state and output')
            checked_row.append([_integer(cell[0], len(rows) - 1, 'successor state'),
                                _integer(cell[1], outputs - 1, 'semantic output')])
        transitions.append(checked_row)
    if not isinstance(contract, dict) or set(contract) - {'goal', 'hazard', 'horizon'}:
        raise ValueError('Invalid public contract')
    goal = _integer(contract.get('goal', 1), outputs - 1, 'contract goal')
    hazard = _integer(contract.get('hazard', 2), outputs - 1, 'contract hazard')
    horizon = _integer(contract.get('horizon', 4), 6, 'contract horizon', 1)
    if goal == hazard:
        raise ValueError('Contract goal and hazard must differ')
    return ({'name': name, 'inputs': inputs, 'outputs': outputs, 'initial': initial,
             'transitions': transitions}, {'goal': goal, 'hazard': hazard, 'horizon': horizon})


def _observations(evidence, inputs, outputs):
    if not isinstance(evidence, (list, tuple)) or len(evidence) > 512:
        raise ValueError('Evidence must contain at most 512 entries')
    normalized, steps = [], 0
    for entry in evidence:
        if not isinstance(entry, dict) or type(entry.get('complete')) is not bool:
            raise ValueError('Evidence must declare boolean completeness')
        word = _sequence(entry['word'], inputs, 'evidence word')
        observed = _sequence(entry['outputs'], outputs, 'evidence output')
        if len(observed) > len(word) or (entry['complete'] and len(observed) != len(word)):
            raise ValueError('Evidence word/output lengths differ')
        steps += len(observed)
        if steps > 512:
            raise ValueError('Evidence exceeds 512 observed steps')
        if observed:
            normalized.append({'word': list(word[:len(observed)]),
                               'outputs': list(observed), 'complete': True})
    return normalized


def _anchors(anchors, outputs):
    if anchors is None:
        anchors = {}
    if not isinstance(anchors, dict):
        raise ValueError('Anchors must be an object')
    normalized = {}
    for raw, semantic in anchors.items():
        if isinstance(raw, str) and raw in {str(i) for i in range(outputs)}:
            raw = int(raw)
        raw = _integer(raw, outputs - 1, 'anchor raw output')
        semantic = _integer(semantic, outputs - 1, 'anchor semantic output')
        if raw in normalized and normalized[raw] != semantic:
            raise ValueError('Conflicting normalized anchor keys')
        normalized[raw] = semantic
    return sorted(normalized.items())


def verify_experiment_tree(reference: dict, contract: dict, tree: dict, *,
                           temporal=False, evidence=(), anchors=None,
                           budget: int, safe_only=False) -> dict:
    """Reconstruct beliefs, branch coverage, readiness and reset/action costs.

    ``budget`` is the remaining acquisition-call budget for this proposed tree.
    Deployment words have their separate contract horizon. Incomplete evidence
    contributes every observed prefix; its unobserved suffix is never evidence.
    """
    report = {'schema': 'crosswire-experiment-certificate-v1', 'valid': False,
              'checked_nodes': 0, 'scope': SCOPE}
    try:
        if type(temporal) is not bool or type(safe_only) is not bool:
            raise ValueError('Temporal and safe_only settings must be booleans')
        budget = _integer(budget, 512, 'remaining acquisition budget')
        reference, contract = _public_model(reference, contract)
        inputs, outputs = reference['inputs'], reference['outputs']
        observed = _observations(evidence, inputs, outputs)
        anchor_pairs = _anchors(anchors, outputs)
        pairs = list(product(permutations(range(inputs)), permutations(range(outputs))))
        adapters = [(input_map, output_map, 0, 0) for input_map, output_map in pairs]
        if temporal:
            adapters.extend((input_map, output_map, 1, initial)
                            for input_map, output_map in pairs for initial in range(outputs))
        semantic_cache = {}

        def trace(identifier, word):
            input_map, output_map, delay, initial_buffer = adapters[identifier]
            cache_key = (input_map, word)
            if cache_key not in semantic_cache:
                state, semantic = reference['initial'], []
                for action in word:
                    state, output = reference['transitions'][state][input_map[action]]
                    semantic.append(output)
                semantic_cache[cache_key] = tuple(semantic)
            semantic = semantic_cache[cache_key]
            emitted = (initial_buffer,) + semantic[:-1] if delay and word else semantic
            return tuple(output_map[output] for output in emitted), semantic

        belief = tuple(i for i, adapter in enumerate(adapters)
                       if all(adapter[1][semantic] == raw for raw, semantic in anchor_pairs))
        for entry in observed:
            word, response = tuple(entry['word']), tuple(entry['outputs'])
            belief = tuple(i for i in belief if trace(i, word)[0] == response)
        report['candidate_count'] = len(belief)
        ready_models = largest_unresolved = terminal_squared = worst_case_calls = depth = 0

        def visit(node, members, calls, query_depth):
            nonlocal ready_models, largest_unresolved, terminal_squared, worst_case_calls, depth
            if report['checked_nodes'] >= 10000:
                raise ValueError('Experiment tree exceeds the 10000 checked-node limit')
            report['checked_nodes'] += 1
            if not isinstance(node, dict):
                raise ValueError('Experiment nodes must be objects')
            kind = node.get('kind')
            if kind == 'ready' and set(node) == {'kind', 'deployment_word'}:
                word = _sequence(node['deployment_word'], inputs, 'deployment word', contract['horizon'])
                if not members or not word:
                    raise ValueError('Empty belief or deployment word cannot certify readiness')
                for identifier in members:
                    semantic = trace(identifier, word)[1]
                    if contract['hazard'] in semantic or semantic[-1] != contract['goal']:
                        raise ValueError('Ready leaf does not satisfy every surviving interpretation')
                ready_models += len(members)
                normalized = {'kind': 'ready', 'deployment_word': list(word)}
            elif kind == 'unresolved' and set(node) == {'kind'}:
                largest_unresolved = max(largest_unresolved, len(members))
                normalized = {'kind': 'unresolved'}
            elif kind == 'query' and set(node) == {'kind', 'word', 'branches'}:
                if not members:
                    raise ValueError('An empty belief cannot certify an experiment query')
                if query_depth >= 2:
                    raise ValueError('Experiment tree exceeds query depth two')
                word = _sequence(node['word'], inputs, 'query word', 3)
                if not word:
                    raise ValueError('Query word must have length 1..3')
                next_calls = calls + 1 + len(word)
                if next_calls > budget:
                    raise ValueError('Experiment path exceeds remaining acquisition budget')
                expected = {}
                for identifier in members:
                    response, semantic = trace(identifier, word)
                    if safe_only and contract['hazard'] in semantic:
                        raise ValueError('Query risks a hazard under its pre-query surviving belief')
                    key = json.dumps(response, separators=(',', ':'))
                    expected.setdefault(key, []).append(identifier)
                branches = node['branches']
                if (not isinstance(branches, dict) or len(branches) != len(expected)
                        or set(branches) != set(expected)):
                    raise ValueError('Branches must cover exactly every complete predicted raw response')
                depth = max(depth, query_depth + 1)
                normalized_branches = {key: visit(branches[key], tuple(expected[key]), next_calls, query_depth + 1)
                                       for key in sorted(expected)}
                return {'kind': 'query', 'word': list(word), 'branches': normalized_branches}
            else:
                raise ValueError('Malformed or unsupported experiment node')
            terminal_squared += len(members) ** 2
            worst_case_calls = max(worst_case_calls, calls)
            return normalized

        normalized_tree = visit(tree, belief, 0, 0)
        binding = {'reference': reference, 'contract': contract, 'tree': normalized_tree,
                   'temporal': temporal, 'evidence': observed,
                   'anchors': anchor_pairs, 'budget': budget, 'safe_only': safe_only}
        report.update(valid=True, ready_models=ready_models,
                      largest_unresolved_belief=largest_unresolved,
                      terminal_squared_beliefs=terminal_squared,
                      worst_case_calls=worst_case_calls, depth=depth,
                      binding_hash=canonical_hash(binding))
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError) as exc:
        report['reason'] = str(exc)
    return report
