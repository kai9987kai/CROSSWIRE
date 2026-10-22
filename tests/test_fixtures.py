import importlib
import itertools
import random

import pytest


def api():
    assert importlib.util.find_spec('crosswire.fixtures') is not None, 'fixture implementation missing'
    return importlib.import_module('crosswire.fixtures')


def test_catalog_public_privacy_and_local_rng():
    f = api()
    random.seed(901)
    state = random.getstate()
    a = f.make_case('latch', seed=7)
    b = f.make_case('latch', seed=8, implementation='table')
    assert random.getstate() == state
    assert set(a.public) == {'reference', 'contract', 'target_id', 'anchors', 'parent_instance_id'}
    assert a.public['reference']['name'] == 'reference'
    assert a.public['parent_instance_id'] == b.public['parent_instance_id']
    assert a.public['target_id'] != b.public['target_id']
    assert len(a.public['target_id']) >= 16
    assert {x['id'] for x in f.catalog()} >= {'latch','handshake','symmetric','neutral','long_trace','incompatible','alias','semantic_corruption','bypass','malformed'}


@pytest.mark.parametrize('family', ['latch','handshake','symmetric','neutral','long_trace','incompatible','alias','semantic_corruption','bypass','delay','repeat'])
def test_independent_engines_match_actual_finite_machine_exhaustively(family):
    f = api()
    cases = [f.make_case(family, seed=31, implementation=kind) for kind in ('table','procedural')]
    machine = f.target_machine(cases[0].private)
    assert machine is not None
    for length in range(1, 5):
        for word in itertools.product(range(3), repeat=length):
            table, proc = [f.evaluate_word(c.private, word) for c in cases]
            assert table == proc
            assert tuple(table['outputs']) == machine.trace(word)


def test_procedural_does_not_need_source_table():
    f = api()
    case = f.make_case('latch', seed=17)
    assert 'transitions' not in case.private and 'reference' not in case.private
    assert f.evaluate_word(case.private, [0,1,2,0])['semantic_events']


def test_literal_semantic_paths_and_corruption_before_observation():
    f = api()
    case = f.make_case('latch', seed=17)
    inverse = {value: key for key, value in enumerate(case.private['input_map'])}
    word = [inverse[0], inverse[1]]
    good = f.evaluate_word(case.private, word)
    assert good['semantic_events'] == [0,1]
    assert good['contract_satisfied']
    bad = f.make_case('semantic_corruption', seed=17)
    corrupted = f.evaluate_word(bad.private, word)
    assert corrupted['outputs'] == good['outputs']
    assert corrupted['semantic_events'] == [0,2]
    assert corrupted['hazard'] and not corrupted['contract_satisfied']
    assert f.target_machine(bad.private).transitions == f.target_machine(case.private).transitions


def test_long_trace_oracle_and_alias_ground_truth():
    f = api()
    case = f.make_case('long_trace', seed=17)
    assert f.oracle_plan(case.private, 3) is None
    word = f.oracle_plan(case.private, 4)
    assert len(word) == 4
    assert f.evaluate_word(case.private, word)['contract_satisfied']
    alias = f.make_case('alias', seed=17)
    inverse = {value: key for key, value in enumerate(alias.private['input_map'])}
    danger = f.evaluate_word(alias.private, [inverse[2]])
    assert danger['semantic_events'] == [2] and danger['hazard']


def test_symmetric_needs_anchor_but_neutral_admits_shared_task():
    f = api()
    from crosswire.core import CandidateSpace, Machine, Contract, words
    for family, expected in [('symmetric',False), ('neutral',True)]:
        case = f.make_case(family, seed=13)
        space = CandidateSpace(Machine.from_dict(case.public['reference']), Contract.from_dict(case.public['contract']))
        transcripts = [{'word':list(w),'outputs':f.evaluate_word(case.private,w)['outputs'],'complete':True} for w in words(3,3)]
        ids = space.survivors(transcripts)
        assert len(ids) > 1
        assert space.plan(ids)['admitted'] is expected
        if family == 'symmetric':
            anchored = f.make_case(family,seed=13,anchors=True)
            ids = space.survivors(transcripts,anchored.public['anchors'])
            assert space.plan(ids)['admitted']


def test_extra_state_passes_all_shallow_probes_then_fails_four_action_task():
    f = api()
    supported = f.make_case('long_trace',seed=17)
    extra = f.make_case('extra_state',seed=17)
    for length in range(1,4):
        for word in itertools.product(range(3),repeat=length):
            assert f.evaluate_word(supported.private,word)['outputs'] == f.evaluate_word(extra.private,word)['outputs']
    word = f.oracle_plan(supported.private,4)
    assert f.evaluate_word(supported.private,word)['contract_satisfied']
    assert not f.evaluate_word(extra.private,word)['contract_satisfied']
    assert f.oracle_plan(extra.private,4) is None
    assert len(f.oracle_plan(extra.private,5)) == 5


def test_drift_persists_across_resets_and_bypass_exposes_checker_limit():
    f = api()
    case = f.make_case('drift',seed=17)
    engine = f.make_engine(case.private)
    inverse = {value:key for key,value in enumerate(case.private['input_map'])}
    for _ in range(8):
        engine.step(inverse[0])
    engine.reset()
    engine.step(inverse[0])
    engine.step(inverse[1])
    assert engine.semantic_events == [0,2]
    assert f.target_machine(case.private) is None
    bypass = f.make_case('bypass',seed=17)
    outcome = f.evaluate_word(bypass.private,[inverse[0],inverse[1]])
    assert outcome['privileged_check_passed'] and outcome['hazard']


def test_deployment_reconstructs_drift_phase_from_successful_probe_prefixes():
    f = api()
    case = f.make_case('drift',seed=17)
    inverse = {value:key for key,value in enumerate(case.private['input_map'])}
    word = [inverse[0],inverse[1]]
    probes = [{'word':[inverse[0]]*6, 'outputs':[0]*6,'complete':True},
              {'word':[inverse[0]]*3,'outputs':[0]*2,'complete':False}]
    assert f.evaluate_word(case.private,word)['contract_satisfied']
    deployment = f.evaluate_deployment(case.private,probes,word)
    assert deployment['semantic_events'] == [0,2]
    assert deployment['hazard'] and not deployment['contract_satisfied']
    # After drift, a command that used to emit hazard is now the true goal.
    assert f.oracle_plan_after(case.private,probes,horizon=4) == [inverse[2]]


def test_private_audit_counts_actual_resets_replayed_steps_and_export_work():
    f = api()
    case = f.make_case('latch')
    probes = [{'word':[0,1,2],'outputs':[0,0,0],'complete':True},
              {'word':[1,2],'outputs':[0],'complete':False}]
    work = {}
    f.evaluate_deployment(case.private,probes,[0,1],work=work)
    assert work == {'resets':3,'steps':6}
    f.evaluate_word(case.private,[2],work=work)
    assert work == {'resets':4,'steps':7}
    exported = {}
    model = f.target_machine(case.private,work=exported)
    assert len(model.transitions) == 4
    assert exported == {'resets':1,'steps':12}


@pytest.mark.parametrize('family', ['latch','handshake','symmetric','neutral','long_trace','extra_state','incompatible','alias','semantic_corruption','bypass','delay','repeat','drift'])
def test_every_supplied_anchor_matches_actual_reachable_semantic_events(family):
    f = api()
    case = f.make_case(family,seed=17,anchors=True)
    seen_anchors = set()
    # The longest supported mechanism reaches every terminal by depth five;
    # repeated prefixes also exercise delayed/repeated terminal transitions.
    for length in range(1,6):
        for word in itertools.product(range(3),repeat=length):
            result = f.evaluate_word(case.private,word)
            for raw,actual in zip(result['outputs'],result['semantic_events']):
                if raw in case.public['anchors']:
                    assert case.public['anchors'][raw] == actual
                    seen_anchors.add(raw)
    assert seen_anchors == set(case.public['anchors'])
    if family == 'drift':
        engine = f.make_engine(case.private)
        for _ in range(8):
            engine.step(0)
        engine.reset()
        for action in (0,1,2)*3:
            raw = engine.step(action)
            if raw in case.public['anchors']:
                assert case.public['anchors'][raw] == engine.semantic_events[-1]


def test_corruption_grounding_contradicts_raw_equivalent_nominal_interpretation():
    f = api()
    from crosswire.core import CandidateSpace, Machine, Contract, words
    for family in ('semantic_corruption','bypass'):
        case = f.make_case(family,seed=17,anchors=True)
        maps = case.private['output_map']
        assert case.public['anchors'] == {maps[1]:2,maps[2]:1}
        space = CandidateSpace(Machine.from_dict(case.public['reference']),Contract.from_dict(case.public['contract']))
        probes = [{'word':list(word),'outputs':f.evaluate_word(case.private,word)['outputs'],'complete':True} for word in words(3,3)]
        assert space.survivors(probes)
        assert not space.survivors(probes,case.public['anchors'])


def test_noninvertible_and_phase_varying_controls_publish_only_sound_anchor_subset():
    f = api()
    for family in ('alias','drift'):
        case = f.make_case(family,anchors=True)
        maps = case.private['output_map']
        assert case.public['anchors'] == {maps[0]:0,maps[3]:3}
    for family in ('delay','repeat'):
        case = f.make_case(family,anchors=True)
        assert case.public['anchors'] == {case.private['output_map'][2]:2}
    assert f.make_case('malformed',anchors=True).public['anchors'] == {}


@pytest.mark.parametrize('family,success_word,success_events,reset_word,reset_events,state_count', [
    ('rotary',(0,0,1),(0,3,1),(0,0,2,1),(0,3,0,2),5),
    ('interlock',(0,1,2),(0,3,1),(0,0,1,2),(0,0,0,2),6),
])
def test_frozen_evaluation_mechanisms_match_hand_derived_semantics_and_exact_implementations(
        family,success_word,success_events,reset_word,reset_events,state_count):
    f = api()
    cases = [f.make_case(family,seed=31,implementation=implementation,
                         split='evaluation',anchors=True) for implementation in ('table','procedural')]
    assert cases[0].public['parent_instance_id'] == cases[1].public['parent_instance_id']
    assert cases[0].public['parent_instance_id'] != f.make_case('latch').public['parent_instance_id']
    for case in cases:
        inverse = {value:key for key,value in enumerate(case.private['input_map'])}
        word = [inverse[value] for value in success_word]
        result = f.evaluate_word(case.private,word)
        assert result['semantic_events'] == list(success_events)
        assert result['contract_satisfied'] and not result['hazard']
        wrong = f.evaluate_word(case.private,[inverse[value] for value in reset_word])
        assert wrong['semantic_events'] == list(reset_events)
        assert wrong['hazard'] and not wrong['contract_satisfied']
        hazard = f.evaluate_word(case.private,[inverse[2 if family=='interlock' else 1]]+[inverse[0]]*3)
        assert hazard['semantic_events'] == [2,2,2,2]
        goal = f.evaluate_word(case.private,word+[inverse[0],inverse[2]])
        assert goal['semantic_events'][-2:] == [1,1]
        for raw,actual in zip(goal['outputs'],goal['semantic_events']):
            if raw in case.public['anchors']:
                assert case.public['anchors'][raw] == actual
    # Compare every reachable transition of independently exported complete
    # implementations. No learner, probe policy or comparative study is run.
    models = [f.target_machine(case.private) for case in cases]
    assert len(models[0].transitions) == state_count
    assert models[0].transitions == models[1].transitions
    assert len(cases[0].public['reference']['transitions']) == state_count
    entry = next(row for row in f.catalog() if row['id']==family)
    assert entry['scope'] == 'in_family'
