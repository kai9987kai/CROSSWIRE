"""Probe safety is checked before dispatch, across the entire live model set."""
import pytest

from crosswire.core import CandidateSpace, Contract, Machine
from crosswire.fixtures import evaluate_word, make_case


POLICIES = ('fixed', 'random', 'disagreement', 'task', 'counterexample', 'entropy', 'ec2')


def _aid(space, inputs=(0, 1, 2), outputs=(0, 1, 2, 3)):
    return next(a.id for a in space.adapters
                if a.input_map == inputs and a.output_map == outputs and not a.delay)


def _diagnostic_space():
    machine = Machine('unsafe first action, safe diagnostics',
                      (((0, 2), (1, 0), (0, 3)), ((0, 2), (1, 1), (0, 0))))
    space = CandidateSpace(machine, Contract())
    return space, (_aid(space), _aid(space, inputs=(0, 2, 1)))


@pytest.mark.parametrize('policy', POLICIES)
def test_every_probe_policy_selects_a_safe_informative_word(policy):
    space, ids = _diagnostic_space()
    word = space.choose_probe(ids, policy, 3, set(), seed=7, safe_only=True)
    assert word is not None
    assert all(2 not in space.semantic(i, word) for i in ids)
    assert len({space.predict(i, word) for i in ids}) == 2


@pytest.mark.parametrize('policy', POLICIES)
def test_safe_probes_abstain_when_every_action_could_be_hazardous(policy):
    public = make_case('latch', 17).public
    space = CandidateSpace(Machine.from_dict(public['reference']), Contract())
    ids = tuple(a.id for a in space.adapters)
    assert space.choose_probe(ids, policy, 6, set(), safe_only=True) is None


@pytest.mark.parametrize('policy', POLICIES)
def test_no_survivors_never_certify_a_probe(policy):
    space, _ = _diagnostic_space()
    assert space.choose_probe((), policy, 3, set(), safe_only=True) is None


def test_safe_filter_rejects_unsafe_counterexample_outside_fixed_pool():
    public = make_case('long_trace', 17).public
    space = CandidateSpace(Machine.from_dict(public['reference']), Contract(goal=2, hazard=1))
    ids, seen = (4, 65), set(space._probes)
    unsafe = space.choose_probe(ids, 'counterexample', 4, seen)
    assert unsafe == (0, 0, 0, 0)
    assert any(1 in space.semantic(i, unsafe) for i in ids)
    assert space.choose_probe(ids, 'counterexample', 4, seen, safe_only=True) is None


def test_safe_filter_preserves_safe_counterexample_outside_fixed_pool():
    public = make_case('long_trace', 17).public
    space = CandidateSpace(Machine.from_dict(public['reference']), Contract())
    word = space.choose_probe((4, 65), 'counterexample', 4, set(space._probes), safe_only=True)
    assert word == (0, 0, 0, 0)
    assert all(2 not in space.semantic(i, word) for i in (4, 65))


def test_safe_acquisition_with_grounded_anchors_can_reach_robust_admission():
    case = make_case('routing', 17, anchors=True)
    public = case.public
    space = CandidateSpace(Machine.from_dict(public['reference']), Contract())
    evidence, seen = [], set()
    ids = space.survivors(evidence, public['anchors'])
    calls = 0
    while calls < 16 and not space.plan(ids)['admitted']:
        word = space.choose_probe(ids, 'task', 15 - calls, seen, safe_only=True)
        assert word is not None
        seen.add(word)
        actual = evaluate_word(case.private, word)
        assert actual['hazard'] is False
        evidence.append({'word': word, 'outputs': actual['outputs'], 'complete': True})
        calls += len(word) + 1
        ids = space.survivors(evidence, public['anchors'])
    assert 0 < calls <= 16
    decision = space.plan(ids)
    assert decision['admitted'] is True
    assert evaluate_word(case.private, decision['word'])['contract_satisfied'] is True


def test_probe_safety_uses_semantics_and_never_an_empty_belief():
    space, ids = _diagnostic_space()
    assert space.probe_is_safe(ids, (1,)) is True
    assert space.probe_is_safe(ids, (0,)) is False
    assert space.probe_is_safe((), (1,)) is False


@pytest.mark.parametrize('value', (0, 1, None, 'yes'))
def test_safe_only_requires_an_actual_boolean(value):
    space, ids = _diagnostic_space()
    with pytest.raises((TypeError, ValueError), match='safe_only'):
        space.choose_probe(ids, 'fixed', 3, set(), safe_only=value)


def test_safe_filter_default_preserves_existing_selection():
    space, ids = _diagnostic_space()
    assert space.choose_probe(ids, 'fixed', 3, set()) == (0,)
    assert space.choose_probe(ids, 'fixed', 3, set(), safe_only=False) == (0,)
    assert space.choose_probe(ids, 'fixed', 3, set(), safe_only=True) == (1,)


@pytest.mark.parametrize('value', (-0.1, 1.0, 2, True, False, '0.2', None,
                                 float('nan'), float('inf'), float('-inf')))
@pytest.mark.parametrize('mode', ('robust', 'risk_controlled'))
def test_core_rejects_invalid_risk_tolerance(value, mode):
    space, ids = _diagnostic_space()
    with pytest.raises((TypeError, ValueError), match='risk_tolerance'):
        space.plan(ids, mode=mode, risk_tolerance=value)


def test_positive_tolerance_admits_an_exact_declared_model_fraction():
    space = CandidateSpace(Machine('three interpretations', (((0, 1), (0, 2), (0, 0)),)), Contract())
    ids = (_aid(space), _aid(space, outputs=(3, 1, 2, 0)), _aid(space, inputs=(1, 0, 2)))
    assert space.plan(ids, 'robust')['admitted'] is False
    decision = space.plan(ids, 'risk_controlled', risk_tolerance=0.4)
    assert decision['admitted'] is True
    assert decision['word'] == [0]
    assert decision['risk_metrics']['hazard_risk'] == pytest.approx(1 / 3)
    assert decision['risk_metrics']['goal_rate'] == pytest.approx(2 / 3)


def test_fraction_threshold_has_no_implicit_risk_allowance():
    space = CandidateSpace(Machine('three interpretations', (((0, 1), (0, 2), (0, 0)),)), Contract(horizon=1))
    ids = (_aid(space), _aid(space, outputs=(3, 1, 2, 0)), _aid(space, inputs=(1, 0, 2)))
    assert space.plan(ids, 'risk_controlled', risk_tolerance=1 / 3 - 1e-10)['admitted'] is False
    assert space.plan(ids, 'risk_controlled', risk_tolerance=1 / 3)['admitted'] is True


def test_unselected_plan_has_no_hazard_or_goal_fraction():
    space, ids = _diagnostic_space()
    decision = space.plan((), 'risk_controlled')
    assert decision['risk_metrics']['hazard_risk'] is None
    assert decision['risk_metrics']['goal_rate'] is None
