import copy

import pytest

from crosswire.core import CandidateSpace, Contract, Machine


def routing_space(temporal=False):
    rows = (((1, 0), (1, 3), (1, 3)),
            ((2, 0), (2, 3), (2, 3)),
            ((3, 0), (3, 3), (3, 3)),
            ((4, 1), (5, 2), (5, 2)),
            ((4, 1), (4, 1), (4, 1)),
            ((5, 2), (5, 2), (5, 2)))
    return CandidateSpace(Machine('routing', rows), Contract(horizon=4), temporal)


def test_contingent_policy_succeeds_where_no_fixed_word_exists():
    from crosswire.adaptive import synthesize_policy, verify_policy
    space = routing_space()
    ids = space.survivors([])
    assert not space.plan(ids)['admitted']
    result = synthesize_policy(space, ids)
    assert result['admitted'] and result['word'] is None
    checked = verify_policy(space, ids, result['policy'])
    assert checked['valid'] and checked['worst_case_steps'] == 4
    # Independently execute the tree against every candidate, not just one seed.
    for aid in ids:
        node, word = result['policy'], ()
        while 'action' in node:
            word += (node['action'],)
            assert space.contract.hazard not in space.semantic(aid, word)
            node = node['branches'][str(space.predict(aid, word)[-1])]
        assert node == {'stop': True}
        assert space.contract.accepts(space.semantic(aid, word))


def test_certificate_rejects_missing_extra_unsafe_and_early_stop_branches():
    from crosswire.adaptive import synthesize_policy, verify_policy
    space = routing_space()
    ids = space.survivors([])
    tree = synthesize_policy(space, ids)['policy']
    missing = copy.deepcopy(tree)
    missing['branches'].pop(next(iter(missing['branches'])))
    assert not verify_policy(space, ids, missing)['valid']
    extra = copy.deepcopy(tree)
    extra['branches']['99'] = {'stop': True}
    assert not verify_policy(space, ids, extra)['valid']
    assert not verify_policy(space, ids, {'stop': True})['valid']
    assert not verify_policy(space, (), tree)['valid']
    damaged = copy.deepcopy(tree)
    node = damaged
    while 'action' in node:
        if all('stop' in child for child in node['branches'].values()):
            node['action'] = (node['action'] + 1) % 3
            break
        node = next(iter(node['branches'].values()))
    assert not verify_policy(space, ids, damaged)['valid']


def test_search_limit_and_empty_belief_never_admit():
    from crosswire.adaptive import synthesize_policy
    space = routing_space()
    result = synthesize_policy(space, space.survivors([]), node_limit=1)
    assert not result['admitted'] and result['status'] == 'SEARCH_LIMIT'
    assert not result['search']['complete']
    assert synthesize_policy(space, ())['status'] == 'FAMILY_CONTRADICTED'
    with pytest.raises((ValueError, TypeError)):
        synthesize_policy(space, (0,), node_limit=True)


def test_temporal_policy_checks_current_hazard_not_delayed_symbol():
    from crosswire.adaptive import verify_policy
    space = routing_space(True)
    aid = next(a.id for a in space.adapters if a.delay == 1
               and a.input_map == (0, 1, 2) and a.output_map == (0, 1, 2, 3)
               and a.init_output == 0)
    leaf = {'stop': True}
    for raw, action in reversed(list(zip([0, 0, 0, 0], [0, 0, 0, 1]))):
        leaf = {'action': action, 'branches': {str(raw): leaf}}
    assert not verify_policy(space, (aid,), leaf)['valid']


def test_run_routing_adaptive_is_audited_and_replayed():
    from crosswire.study import RunConfig, run
    from crosswire.receipts import pack, replay
    fixed = run(RunConfig(family='routing', budget=0))
    result = run(RunConfig(family='routing', budget=0, admission='adaptive', execution_mode='shielded'))
    assert not fixed['decision']['admitted']
    assert result['decision']['admitted']
    assert result['audit']['contract_satisfied'] is True
    assert result['metrics']['target_calls'] == 0
    assert result['deployment']['target_calls'] == 5
    assert result['decision']['certificate']['valid']
    assert replay(pack(result))['valid']
