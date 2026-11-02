"""Experiment certificates reconstruct every branch from public model data."""
from copy import deepcopy

import pytest


REFERENCE = {'name': 'goal-or-neutral', 'inputs': 2, 'outputs': 3, 'initial': 0,
             'transitions': [[[0, 1], [0, 0]]]}
CONTRACT = {'goal': 1, 'hazard': 2, 'horizon': 2}
ANCHORS = {1: 1}


def check(tree, *, reference=REFERENCE, contract=CONTRACT, **context):
    from crosswire.experiment_checks import verify_experiment_tree
    return verify_experiment_tree(reference, contract, tree, **{'budget': 4, **context})


def ready(word):
    return {'kind': 'ready', 'deployment_word': word}


def query(branches, word=None):
    return {'kind': 'query', 'word': [0] if word is None else word, 'branches': branches}


def informative_tree():
    return query({'[0]': ready([1]), '[1]': ready([0]), '[2]': ready([1])})


def test_checker_reconstructs_readiness_and_model_count_metrics():
    tree = informative_tree()
    before = deepcopy(tree)
    checked = check(tree, anchors=ANCHORS, safe_only=True, budget=2)
    assert checked['valid'] is True
    assert checked['schema'] == 'crosswire-experiment-certificate-v1'
    assert {key: checked[key] for key in ('candidate_count', 'ready_models',
            'largest_unresolved_belief', 'terminal_squared_beliefs',
            'worst_case_calls', 'checked_nodes', 'depth')} == {
        'candidate_count': 4, 'ready_models': 4, 'largest_unresolved_belief': 0,
        'terminal_squared_beliefs': 6, 'worst_case_calls': 2, 'checked_nodes': 4, 'depth': 1}
    assert 'conditional' in checked['scope'].lower()
    assert 'authenticate' in checked['scope'].lower()
    assert 'semantic' in checked['scope'].lower()
    assert tree == before


def test_unresolved_leaf_makes_no_readiness_or_impossibility_claim():
    result = check({'kind': 'unresolved'}, anchors=ANCHORS, budget=0)
    assert result['valid'] is True
    assert result['candidate_count'] == result['largest_unresolved_belief'] == 4
    assert result['ready_models'] == result['worst_case_calls'] == result['depth'] == 0
    assert result['terminal_squared_beliefs'] == 16


@pytest.mark.parametrize('mutation', ['omit', 'extra', 'noncanonical_raw_key', 'wrong_ready_word',
                                      'claimed_candidate_count'])
def test_checker_rejects_tampered_branches_and_readiness(mutation):
    tree = informative_tree()
    if mutation == 'omit':
        tree['branches'].pop('[0]')
    elif mutation == 'extra':
        tree['branches']['[3]'] = {'kind': 'unresolved'}
    elif mutation == 'noncanonical_raw_key':
        tree['branches']['[ 0 ]'] = tree['branches'].pop('[0]')
    elif mutation == 'wrong_ready_word':
        tree['branches']['[1]']['deployment_word'] = [1]
    else:
        tree['candidate_count'] = 4
    assert check(tree, anchors=ANCHORS)['valid'] is False


def test_full_raw_response_is_required_including_delayed_outputs():
    reference = {'name': 'always-goal', 'inputs': 1, 'outputs': 3,
                 'transitions': [[[0, 1]]]}
    tree = query({f'[{raw}]': {'kind': 'unresolved'} for raw in range(3)})
    checked = check(tree, reference=reference, temporal=True)
    assert checked['valid'] is True
    assert checked['candidate_count'] == 24
    assert checked['largest_unresolved_belief'] == 8
    assert checked['terminal_squared_beliefs'] == 192
    # Two-action temporal responses include initial buffer and delayed goal.
    tree['word'] = [0, 0]
    assert check(tree, reference=reference, temporal=True)['valid'] is False


def test_temporal_evidence_reconstructs_initial_buffer_independently():
    reference = {'name': 'always-goal', 'inputs': 1, 'outputs': 3,
                 'transitions': [[[0, 1]]]}
    context = {'reference': reference, 'anchors': {0: 0, 1: 1, 2: 2},
               'evidence': [{'word': [0, 0], 'outputs': [0, 1], 'complete': True}]}
    checked = check(ready([0]), temporal=True, **context)
    assert checked['valid'] is True and checked['candidate_count'] == checked['ready_models'] == 1
    assert check(ready([0]), temporal=False, **context)['valid'] is False


def test_incomplete_observed_prefix_is_evidence_and_has_canonical_binding():
    incomplete = [{'word': [0, 1], 'outputs': [1], 'complete': False}]
    complete_prefix = [{'word': [0], 'outputs': [1], 'complete': True}]
    left = check(ready([0]), anchors=ANCHORS, evidence=incomplete)
    right = check(ready([0]), anchors={'1': 1}, evidence=complete_prefix)
    assert left['valid'] is True and left['candidate_count'] == 2
    assert left == right
    assert check(ready([1]), anchors=ANCHORS, evidence=incomplete)['valid'] is False


def test_empty_incomplete_observation_supplies_no_evidence():
    plain = check({'kind': 'unresolved'})
    interrupted = check({'kind': 'unresolved'}, evidence=[{'word': [0], 'outputs': [], 'complete': False}])
    assert plain == interrupted


def test_empty_belief_never_certifies_readiness_or_a_query():
    evidence = [{'word': [0], 'outputs': [0], 'complete': True},
                {'word': [0], 'outputs': [1], 'complete': True}]
    assert check(ready([0]), evidence=evidence)['valid'] is False
    assert check(query({}), evidence=evidence)['valid'] is False
    result = check({'kind': 'unresolved'}, evidence=evidence)
    assert result['valid'] is True and result['candidate_count'] == result['terminal_squared_beliefs'] == 0


def test_safe_mode_checks_semantics_even_when_delayed_raw_response_looks_safe():
    reference = {'name': 'hazard', 'inputs': 1, 'outputs': 3, 'transitions': [[[0, 2]]]}
    tree = query({f'[{raw}]': {'kind': 'unresolved'} for raw in range(3)})
    assert check(tree, reference=reference, temporal=True, safe_only=False)['valid'] is True
    guarded = check(tree, reference=reference, temporal=True, safe_only=True)
    assert guarded['valid'] is False and 'hazard' in guarded['reason'].lower()


def test_hypothetical_query_safety_uses_its_reconstructed_branch_belief():
    reference = {'name': 'diagnose-before-hazard', 'inputs': 2, 'outputs': 3,
                 'transitions': [[[1, 0], [1, 1]], [[1, 2], [1, 0]]]}
    tree = query({'[0]': query({'[1,0]': {'kind': 'unresolved'}}, word=[1, 1]),
                  '[1]': query({'[1,0]': {'kind': 'unresolved'}}, word=[0, 0])})
    context = {'reference': reference, 'anchors': {0: 0, 1: 1, 2: 2}, 'budget': 5}
    checked = check(tree, safe_only=True, **context)
    assert checked['valid'] is True and checked['candidate_count'] == 2
    assert checked['worst_case_calls'] == 5 and checked['depth'] == 2
    tree['branches']['[0]'] = query({'[0,2]': {'kind': 'unresolved'}}, word=[0, 0])
    assert check(tree, safe_only=False, **context)['valid'] is True
    assert check(tree, safe_only=True, **context)['valid'] is False


def test_checker_enumerates_the_full_existing_static_and_temporal_classes():
    reference = {'name': 'always-goal', 'inputs': 3, 'outputs': 4,
                 'transitions': [[[0, 1], [0, 1], [0, 1]]]}
    static = check(ready([0]), reference=reference)
    temporal = check(ready([0]), reference=reference, temporal=True)
    assert static['valid'] is True and static['candidate_count'] == static['ready_models'] == 144
    assert temporal['valid'] is True and temporal['candidate_count'] == temporal['ready_models'] == 720
    assert temporal['terminal_squared_beliefs'] == 518400


def test_ready_leaf_requires_hazard_free_goal_within_deployment_horizon():
    reference = {'name': 'hazard-then-goal', 'inputs': 1, 'outputs': 3,
                 'transitions': [[[1, 2]], [[1, 1]]]}
    assert check(ready([0, 0]), reference=reference)['valid'] is False
    reference['transitions'][0][0][1] = 0
    assert check(ready([0, 0]), reference=reference)['valid'] is True
    assert check(ready([0, 0]), reference=reference, contract={**CONTRACT, 'horizon': 1})['valid'] is False


def repeated_query_tree(levels):
    def same_response(raw, left):
        return {'kind': 'unresolved'} if not left else query({f'[{raw}]': same_response(raw, left - 1)})
    return query({f'[{raw}]': same_response(raw, levels - 1) for raw in range(3)})


def test_path_budget_counts_resets_and_depth_is_bounded():
    reference = {'name': 'always-goal', 'inputs': 1, 'outputs': 3, 'transitions': [[[0, 1]]]}
    tree = repeated_query_tree(2)
    checked = check(tree, reference=reference, budget=4)
    assert checked['valid'] is True
    assert checked['worst_case_calls'] == 4 and checked['depth'] == 2 and checked['checked_nodes'] == 7
    assert check(tree, reference=reference, budget=3)['valid'] is False
    assert check(repeated_query_tree(3), reference=reference, budget=8)['valid'] is False


@pytest.mark.parametrize('word', [[], [0] * 4, [True], [-1], [2], '0'])
def test_only_bounded_probe_bank_words_are_accepted(word):
    tree = query({f'[{raw}]': {'kind': 'unresolved'} for raw in range(3)}, word=word)
    assert check(tree)['valid'] is False


@pytest.mark.parametrize('budget', [True, -1, 513, 1.0, '4'])
def test_malformed_budget_is_rejected(budget):
    assert check({'kind': 'unresolved'}, budget=budget)['valid'] is False


@pytest.mark.parametrize('entry', [{'word': [0], 'outputs': [0]},
                                  {'word': [0], 'outputs': [0], 'complete': 1},
                                  {'word': [0], 'outputs': [], 'complete': True},
                                  {'word': [], 'outputs': [0], 'complete': False},
                                  {'word': [0], 'outputs': [True], 'complete': True}])
def test_malformed_evidence_is_rejected(entry):
    assert check({'kind': 'unresolved'}, evidence=[entry])['valid'] is False


def test_evidence_step_cap_is_enforced_before_enumeration():
    entry = {'word': [0] * 512, 'outputs': [0] * 512, 'complete': True}
    checked = check({'kind': 'unresolved'}, evidence=[entry, {'word': [0], 'outputs': [0], 'complete': True}])
    assert checked['valid'] is False and '512' in checked['reason']


def test_binding_changes_when_public_budget_or_safety_context_changes():
    tree = {'kind': 'unresolved'}
    results = [check(tree), check(tree, budget=3), check(tree, safe_only=True), check(tree, temporal=True)]
    assert all(result['valid'] for result in results)
    assert len({result['binding_hash'] for result in results}) == 4


@pytest.mark.parametrize('context', [{'temporal': 1}, {'safe_only': 'yes'}, {'anchors': {True: 1}},
                                    {'anchors': {'01': 1}}, {'anchors': {1: True}},
                                    {'reference': {**REFERENCE, 'inputs': 4}},
                                    {'contract': {**CONTRACT, 'goal': 3}}])
def test_malformed_public_context_is_rejected(context):
    assert check({'kind': 'unresolved'}, **context)['valid'] is False
