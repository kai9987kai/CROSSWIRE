"""Bounded robust policies over public adapter beliefs, with a separate checker.

The tree is contingent on raw observations, never private fixture state. Guarantees
are conditional on the real system being represented by the initial belief.
"""
from __future__ import annotations

from .core import CandidateSpace, _integer
from .identity import canonical_hash
from .interfaces import InterfaceError


def _cancelled(cancel):
    if cancel and cancel():
        # Local import avoids a study/adaptive import cycle.
        from .study import Cancelled
        raise Cancelled('Adaptive policy computation cancelled')


def synthesize_policy(space: CandidateSpace, ids, node_limit=20000, cancel=None) -> dict:
    """Find a minimum worst-case-depth tree, then lexicographic actions.

    Iterative deepening searches an OR over actions and an AND over all response
    partitions. A hard node cap returns SEARCH_LIMIT, never a negative proof.
    All actions, including diagnostic ones, count toward the contract horizon.
    """
    ids = space._ids(ids)
    _integer(node_limit, 'node_limit', 1, 1000000)
    expanded = 0

    class Limit(Exception):
        pass

    def search(belief, prefix, remaining):
        nonlocal expanded
        _cancelled(cancel)
        if expanded >= node_limit:
            raise Limit
        expanded += 1
        if prefix and all(space.contract.accepts(space.semantic(i, prefix)) for i in belief):
            return {'stop': True}
        if not remaining:
            return None
        for action in range(space.machine.inputs):
            word = prefix + (action,)
            if any(space.contract.hazard in space.semantic(i, word) for i in belief):
                continue
            partitions = {}
            for i in belief:
                partitions.setdefault(space.predict(i, word)[-1], []).append(i)
            branches = {}
            for raw, members in sorted(partitions.items()):
                child = search(tuple(members), word, remaining - 1)
                if child is None:
                    break
                branches[str(raw)] = child
            else:
                return {'action': action, 'branches': branches}
        return None

    tree, complete = None, True
    if ids:
        try:
            for depth in range(1, space.contract.horizon + 1):
                tree = search(ids, (), depth)
                if tree is not None:
                    break
        except Limit:
            complete = False
    certificate = verify_policy(space, ids, tree) if tree is not None else None
    if tree is not None and not certificate['valid']:
        raise RuntimeError('Synthesized policy failed independent model checking')
    return {'status': 'ADAPTIVE_ADMISSIBLE' if tree is not None else
            'FAMILY_CONTRADICTED' if not ids else 'UNRESOLVED' if complete else 'SEARCH_LIMIT',
            'admitted': tree is not None, 'word': None, 'policy': tree,
            'candidate_count': len(ids), 'certificate': certificate,
            'search': {'expanded_nodes': expanded, 'node_limit': node_limit,
                       'complete': complete, 'horizon': space.contract.horizon}}


def verify_policy(space: CandidateSpace, ids, policy) -> dict:
    """Check a supplied tree without calling the synthesizer.

    Derive every branch belief anew from predictions; never trust stored survivor
    counts, hashes, claimed leaf goals, or search metadata. This checks a finite
    public model, not truth of its assumptions or real-world semantic grounding.
    """
    ids = space._ids(ids)
    checked, leaves, worst = 0, 0, 0

    def visit(node, belief, prefix):
        nonlocal checked, leaves, worst
        checked += 1
        if not belief:
            raise ValueError('An empty belief cannot certify a policy')
        if not isinstance(node, dict):
            raise ValueError('Policy nodes must be objects')
        if len(prefix) > space.contract.horizon:
            raise ValueError('Policy exceeds the contract horizon')
        if set(node) == {'stop'} and node['stop'] is True:
            if not prefix or not all(space.contract.accepts(space.semantic(i, prefix)) for i in belief):
                raise ValueError('Stop leaf does not satisfy every surviving interpretation')
            leaves += 1
            worst = max(worst, len(prefix))
            return
        if set(node) != {'action', 'branches'} or len(prefix) >= space.contract.horizon:
            raise ValueError('Malformed action node or horizon exhausted')
        action = _integer(node['action'], 'policy action', maximum=space.machine.inputs - 1)
        branches = node['branches']
        if not isinstance(branches, dict):
            raise ValueError('Branches must be an object keyed by raw output')
        word = prefix + (action,)
        expected = {}
        for i in belief:
            if space.contract.hazard in space.semantic(i, word):
                raise ValueError('An action risks a hazard under a surviving interpretation')
            expected.setdefault(str(space.predict(i, word)[-1]), []).append(i)
        if set(branches) != set(expected):
            raise ValueError('Branches must cover exactly every possible raw output')
        for raw, members in sorted(expected.items()):
            visit(branches[raw], tuple(members), word)

    try:
        visit(policy, ids, ())
    except (ValueError, TypeError, RecursionError) as exc:
        return {'valid': False, 'reason': str(exc), 'checked_nodes': checked}
    return {'schema': 'crosswire-policy-certificate-v1', 'valid': True,
            'checked_nodes': checked, 'leaves': leaves, 'worst_case_steps': worst,
            'candidate_count': len(ids),
            'binding_hash': canonical_hash({'reference': space.machine.to_dict(),
                                           'contract': space.contract.to_dict(),
                                           'adapters': [space.adapters[i].to_dict() for i in ids],
                                           'policy': policy}),
            'scope': 'All branches in the declared finite candidate family; conditional on target inclusion, '
                     'stationarity, deterministic reset and truthful anchors. Not semantic grounding.'}


def execute_policy(target, policy, space: CandidateSpace, ids, cancel=None) -> dict:
    """Verify before reset, then execute only certified observation branches."""
    ids = space._ids(ids)
    certificate = verify_policy(space, ids, policy)
    if not certificate['valid']:
        raise ValueError('Refusing uncertified policy: ' + certificate['reason'])
    deployment = {'word': None, 'executed_word': [], 'outputs': [], 'complete': False,
                  'mode': 'adaptive', 'shield_status': 'ACTIVE', 'intervened': False,
                  'hazard_averted': False, 'reasons': [], 'survivor_history': [len(ids)],
                  'target_steps': 0, 'resets': 0, 'target_calls': 0, 'error': None,
                  'certificate': certificate}
    before = dict(target.counts)
    node, active = policy, ids
    try:
        _cancelled(cancel)
        target.reset()
        while 'action' in node:
            _cancelled(cancel)
            action = node['action']
            word = tuple(deployment['executed_word']) + (action,)
            if not active or any(space.contract.hazard in space.semantic(i, word) for i in active):
                deployment.update(intervened=True, shield_status='INTERVENED_MODEL_RISK')
                deployment['reasons'].append('No unanimously safe continuation')
                break
            raw = target.step(action)
            deployment['executed_word'].append(action)
            deployment['outputs'].append(raw)
            active = tuple(i for i in active if space.predict(i, word) == tuple(deployment['outputs']))
            deployment['survivor_history'].append(len(active))
            if not active or str(raw) not in node['branches']:
                deployment.update(intervened=True, shield_status='INTERVENED_ANOMALY')
                deployment['reasons'].append('Observed response has no certified continuation')
                break
            node = node['branches'][str(raw)]
        else:
            deployment.update(complete=True, shield_status='COMPLETED')
    except InterfaceError as exc:
        deployment['error'] = {'code': exc.code, 'message': str(exc)}
        deployment['shield_status'] = 'INTERFACE_ERROR'
    finally:
        deployment.update(target_steps=target.counts['step_attempts'] - before['step_attempts'],
                          resets=target.counts['reset_attempts'] - before['reset_attempts'],
                          target_calls=target.counts['target_calls'] - before['target_calls'])
    return deployment
