import pytest
from crosswire.certificates import check_result
from crosswire.core import CandidateSpace, Contract, Machine
from crosswire.fixtures import make_case
from crosswire.study import RunConfig, run


def test_risk_controlled_zero_tolerance_matches_robust():
    # When tolerance = 0.0, risk_controlled requires zero hazard and 100% goal, exactly matching robust
    case = make_case('latch', seed=42)
    space = CandidateSpace(Machine.from_dict(case.public['reference']),
                           Contract.from_dict(case.public['contract']))
    survivors = tuple(a.id for a in space.adapters[:10])
    plan_robust = space.plan(survivors, mode='robust')
    plan_risk = space.plan(survivors, mode='risk_controlled', risk_tolerance=0.0)
    assert plan_risk['admitted'] == plan_robust['admitted']
    assert plan_risk['word'] == plan_robust['word']
    if plan_risk['admitted']:
        assert plan_risk['status'] in ('TASK_ADMISSIBLE', 'IDENTIFIED', 'RISK_CONTROLLED_ADMISSIBLE')
        assert 'risk_metrics' in plan_risk
        assert plan_risk['risk_metrics']['hazard_risk'] == 0.0
        assert plan_risk['risk_metrics']['goal_rate'] == 1.0


def test_risk_controlled_admits_majority_goal_under_positive_tolerance():
    # If tolerance is 0.3, a plan with 80% goal rate and 0% hazard can be admitted
    case = make_case('latch', seed=42)
    space = CandidateSpace(Machine.from_dict(case.public['reference']),
                           Contract.from_dict(case.public['contract']))
    survivors = tuple(a.id for a in space.adapters[:20])
    plan_risk = space.plan(survivors, mode='risk_controlled', risk_tolerance=0.4)
    if plan_risk['admitted']:
        assert 'risk_metrics' in plan_risk
        assert plan_risk['risk_metrics']['hazard_risk'] <= 0.4
        assert plan_risk['risk_metrics']['goal_rate'] >= 0.6


def test_risk_controlled_run_and_certificate():
    config = RunConfig(family='latch', seed=42, budget=16, policy='ec2', admission='risk_controlled')
    result = run(config)
    assert result['schema'] == 'crosswire-result-v1'
    assert result['configuration']['admission'] == 'risk_controlled'
    assert result['decision']['admitted'] is True
    assert 'risk_metrics' in result['decision']
    # Check that independent certificate validates
    cert = result['evidence_certificate']
    assert cert['valid'] is True
    assert cert['kind'] in ('admission', 'risk_controlled', 'diagnostic')


def test_risk_controlled_rejects_forged_tolerance_in_certificate():
    case = make_case('latch', seed=42)
    space = CandidateSpace(Machine.from_dict(case.public['reference']),
                           Contract.from_dict(case.public['contract']))
    # Pick a plan that is hazardous under some survivor
    survivors = tuple(a.id for a in space.adapters[:10])
    result_template = run(RunConfig(family='latch', seed=42, budget=16, policy='ec2', admission='risk_controlled'))
    # Tamper with decision to claim tolerance 0.0 when word has hazard under survivors
    result_tampered = dict(result_template)
    decision = dict(result_template['decision'])
    # Set word to an action that hits hazard
    decision['word'] = [2]  # Action 2 in latch transitions to hazard
    decision['risk_metrics'] = {'hazard_risk': 0.0, 'goal_rate': 1.0, 'tolerance': 0.0}
    result_tampered['decision'] = decision
    cert = check_result(result_tampered)
    assert cert['valid'] is False
    assert 'hazard' in cert['reason'].lower() or 'tolerance' in cert['reason'].lower()
