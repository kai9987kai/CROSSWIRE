"""Bounded public-model query trees; hypothetical responses are not observations."""
from __future__ import annotations

import json

from .core import CandidateSpace, FactoredCandidateSpace, _integer


def _cancel(cancel):
    if cancel and cancel():
        from .study import Cancelled
        raise Cancelled('Experiment planning cancelled')


def synthesize_experiment(space, ids, budget, *, seen=(), safe_only=False,
                          cancel=None, node_limit=2048):
    """Rank depth-two reset-query trees by finite model-count task readiness.

    Ready beliefs stop immediately. Completeness concerns this finite bank,
    depth and deployment planner, not global conformance or target truth.
    """
    _integer(budget, 'budget', maximum=512)
    _integer(node_limit, 'node_limit', 1, 100000)
    if type(safe_only) is not bool:
        raise TypeError('safe_only must be boolean')
    ids = space._ids(ids)
    seen = {tuple(word) for word in seen}
    pool = tuple(sorted((word for word in space._probes if word not in seen), key=lambda w: (len(w), w)))
    ready_cache, leaf_cache, projections = {}, {}, {}
    memo, partitions, word_partitions, response_keys = {}, {}, {}, {}
    root_bits = {identifier: 1 << offset for offset, identifier in enumerate(ids)}
    root_mask = (1 << len(ids)) - 1
    belief_masks, mask_members = {ids: root_mask}, {root_mask: ids, 0: ()}
    expanded, best_root, readiness_limited = 0, None, False

    class Limit(Exception):
        pass

    def consume():
        nonlocal expanded
        _cancel(cancel)
        if expanded >= node_limit:
            raise Limit
        expanded += 1

    def readiness_inputs(belief):
        if type(space) not in (CandidateSpace, FactoredCandidateSpace):
            return belief, belief
        if belief not in projections:
            representatives = {}
            for identifier in belief:
                mapping = (space.input_perms[space.decompose_id(identifier)[0]]
                           if type(space) is FactoredCandidateSpace else space.adapters[identifier].input_map)
                representatives.setdefault(mapping, identifier)
            key = tuple(sorted(representatives))
            projections[belief] = key, tuple(representatives[mapping] for mapping in key)
        return projections[belief]

    def leaf(belief):
        nonlocal readiness_limited
        _cancel(cancel)
        key, representatives = readiness_inputs(belief)
        if key not in ready_cache:
            plan = space.plan(representatives, 'robust')
            readiness_limited |= plan.get('status') == 'SEARCH_LIMIT'
            ready_cache[key] = tuple(plan['word']) if plan['admitted'] else None
        cache_key = (key, len(belief))
        if cache_key not in leaf_cache:
            word, n = ready_cache[key], len(belief)
            descriptor = ('ready', word) if word is not None else ('unresolved',)
            # Metrics: ready count, largest unresolved, squared leaf sizes, calls.
            leaf_cache[cache_key] = descriptor, (n if word is not None else 0,
                                                0 if word is not None else n, n * n, 0)
        return leaf_cache[cache_key]

    def split(belief, word):
        if belief not in belief_masks:
            belief_masks[belief] = sum(root_bits[identifier] for identifier in belief)
        mask = belief_masks[belief]
        key = (mask, word)
        if key not in partitions:
            if word not in word_partitions:
                groups = {}
                for offset, identifier in enumerate(ids):
                    if offset % 64 == 0:
                        _cancel(cancel)
                    prediction = space.predict(identifier, word)
                    groups[prediction] = groups.get(prediction, 0) | root_bits[identifier]
                word_partitions[word] = tuple(sorted(groups.items()))
            restricted = []
            for prediction, members_mask in word_partitions[word]:
                active = mask & members_mask
                if not active:
                    continue
                if active not in mask_members:
                    remaining, members = active, []
                    while remaining:
                        bit = remaining & -remaining
                        members.append(ids[bit.bit_length() - 1])
                        remaining ^= bit
                    mask_members[active] = tuple(members)
                    belief_masks[mask_members[active]] = active
                restricted.append((prediction, mask_members[active]))
            partitions[key] = tuple(restricted)
        return partitions[key]

    def rank(metrics, word):
        return metrics[0], -metrics[1], -metrics[2], -metrics[3], -len(word)

    def descriptor_word(descriptor):
        return descriptor[1] if descriptor[0] in ('query', 'query_bank') else ()

    def candidate(belief, word, remaining, with_children):
        cost = 1 + len(word)
        if cost > remaining or (safe_only and not space.probe_is_safe(belief, word)):
            return None
        groups = split(belief, word)
        if len(groups) <= 1:
            return None
        if with_children:
            alternatives = []
            for _, members in groups:
                choices = options_for(members, remaining - cost)
                most_ready = max(option[1][0] for option in choices)
                alternatives.append([option for option in choices if option[1][0] == most_ready])
            # The maximum couples branches. Keep alternatives until the global
            # minimax threshold is known, then minimize additive square sums.
            largest = max(min(option[1][1] for option in choices) for choices in alternatives)
            selected = [min((option for option in choices if option[1][1] <= largest),
                            key=lambda option: (option[1][2], option[1][3],
                                                len(descriptor_word(option[0])), descriptor_word(option[0])))
                        for choices in alternatives]
            descriptor = ('query', word, tuple((prediction, option[0])
                                                for (prediction, _), option in zip(groups, selected)))
        else:
            selected = [leaf(members) for _, members in groups]
            # Retain existing partition references, not a copied tree for every
            # alternative. Only the final selected descriptor is materialized.
            descriptor = ('query_bank', word, groups)
        metrics = (sum(option[1][0] for option in selected),
                   max(option[1][1] for option in selected),
                   sum(option[1][2] for option in selected),
                   cost + max(option[1][3] for option in selected))
        return descriptor, metrics

    def options_for(belief, remaining):
        terminal = leaf(belief)
        if terminal[0][0] == 'ready' or not belief or remaining < 2:
            return [terminal]
        key = (belief, remaining)
        if key not in memo:
            consume()
            choices = [terminal]
            for word in pool:
                _cancel(cancel)
                proposed = candidate(belief, word, remaining, False)
                if proposed is not None:
                    choices.append(proposed)
            most_ready = max(option[1][0] for option in choices)
            memo[key] = [option for option in choices if option[1][0] == most_ready]
        return memo[key]

    def search():
        nonlocal best_root
        terminal = leaf(ids)
        if terminal[0][0] == 'ready' or not ids or budget < 2:
            return terminal
        consume()
        score = None
        for word in pool:
            _cancel(cancel)
            proposed = candidate(ids, word, budget, True)
            if proposed is not None and (score is None or rank(proposed[1], word) > score):
                best_root, score = proposed, rank(proposed[1], word)
        return best_root if best_root is not None else terminal

    def materialize(descriptor):
        _cancel(cancel)
        if descriptor[0] == 'ready':
            return {'kind': 'ready', 'deployment_word': list(descriptor[1])}
        if descriptor[0] == 'unresolved':
            return {'kind': 'unresolved'}
        branches = {}
        for prediction, child in descriptor[2]:
            if prediction not in response_keys:
                response_keys[prediction] = json.dumps(list(prediction), separators=(',', ':'))
            child_descriptor = leaf(child)[0] if descriptor[0] == 'query_bank' else child
            branches[response_keys[prediction]] = materialize(child_descriptor)
        return {'kind': 'query', 'word': list(descriptor[1]), 'branches': branches}

    complete, selection = True, 'lookahead'
    try:
        chosen = search()
    except Limit:
        complete, chosen = False, best_root
    if chosen is None:
        selection, score = 'one_query_fallback', None
        for word in pool:
            _cancel(cancel)
            proposed = candidate(ids, word, budget, False)
            if proposed is not None and (score is None or rank(proposed[1], word) > score):
                chosen, score = proposed, rank(proposed[1], word)
    if chosen is None:
        chosen = leaf(ids)
    tree = materialize(chosen[0])
    space.work['experiment_search_nodes'] = space.work.get('experiment_search_nodes', 0) + expanded
    objective = dict(zip(('ready_models', 'largest_unresolved_belief',
                          'terminal_squared_beliefs', 'worst_case_calls'), chosen[1]))
    return {'word': tree.get('word'), 'tree': tree, 'objective': objective,
            'depth_limit': 2, 'node_limit': node_limit, 'expanded_nodes': expanded,
            'search_complete': complete and not readiness_limited, 'selection': selection,
            'remaining_calls': budget,
            'scope': 'Depth-two finite query-bank model-count readiness; hypothetical observations '
                     'are not measured evidence or calibrated target-success probabilities.'}
