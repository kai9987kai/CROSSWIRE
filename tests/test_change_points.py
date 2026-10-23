import pytest
from crosswire.study import RunConfig, run
from crosswire.fixtures import make_case
from crosswire.interfaces import TargetProcess
from crosswire.core import CandidateSpace, Contract, Machine
from crosswire.shield import execute_deployment


def test_change_point_config_validation():
    with pytest.raises(ValueError, match="fault_schedule must be a dict"):
        RunConfig(family='latch', fault_schedule="not-a-dict").check()

    with pytest.raises(ValueError, match="must specify 'step' and 'type'"):
        RunConfig(family='latch', fault_schedule={'step': 1}).check()

    with pytest.raises(ValueError, match="must be a non-negative integer"):
        RunConfig(family='latch', fault_schedule={'step': -1, 'type': 'sensor_drift'}).check()

    with pytest.raises(ValueError, match="must be one of"):
        RunConfig(family='latch', fault_schedule={'step': 1, 'type': 'unknown_fault'}).check()


def test_change_point_sensor_drift_detection_and_latency():
    # 1. Non-zero latency detection: fault injected at step 1 on latch
    # Output at step 1 remains compatible with a surviving adapter, but output at step 2
    # completely refutes all survivors, resulting in detection latency Delta t = 1.
    config_delayed = RunConfig(family='latch', seed=42, budget=16, execution_mode='shielded',
                               fault_schedule={'step': 1, 'type': 'sensor_drift'})
    result_delayed = run(config_delayed)
    dep_delayed = result_delayed['deployment']
    assert dep_delayed['intervened'] is True
    assert dep_delayed['shield_status'] == 'INTERVENED_ANOMALY'
    cp_delayed = dep_delayed['change_point']
    assert cp_delayed['scheduled'] is True
    assert cp_delayed['step'] == 1
    assert cp_delayed['type'] == 'sensor_drift'
    assert cp_delayed['detected'] is True
    assert cp_delayed['detection_step'] == 2
    assert cp_delayed['detection_latency'] == 1
    assert result_delayed['audit']['change_point'] == cp_delayed

    # 2. Instant detection: fault injected at step 2 on latch
    # Output at step 2 immediately refutes all survivors, giving Delta t = 0.
    config_instant = RunConfig(family='latch', seed=42, budget=16, execution_mode='shielded',
                               fault_schedule={'step': 2, 'type': 'sensor_drift'})
    result_instant = run(config_instant)
    dep_instant = result_instant['deployment']
    assert dep_instant['intervened'] is True
    assert dep_instant['shield_status'] == 'INTERVENED_ANOMALY'
    cp_instant = dep_instant['change_point']
    assert cp_instant['scheduled'] is True
    assert cp_instant['step'] == 2
    assert cp_instant['detected'] is True
    assert cp_instant['detection_step'] == 2
    assert cp_instant['detection_latency'] == 0


def test_change_point_stuck_output_detection():
    config = RunConfig(family='latch', seed=42, budget=16, execution_mode='shielded',
                       fault_schedule={'step': 2, 'type': 'stuck_output', 'value': 0})
    result = run(config)
    dep = result['deployment']
    assert dep['intervened'] is True
    assert dep['shield_status'] == 'INTERVENED_ANOMALY'

    cp = dep['change_point']
    assert cp['scheduled'] is True
    assert cp['detected'] is True
    assert cp['detection_step'] == 2
    assert cp['detection_latency'] == 0


def test_change_point_delay_spike_detection():
    config = RunConfig(family='latch', seed=42, budget=16, execution_mode='shielded',
                       fault_schedule={'step': 2, 'type': 'delay_spike'})
    result = run(config)
    dep = result['deployment']
    assert dep['intervened'] is True
    assert dep['shield_status'] == 'INTERVENED_ANOMALY'

    cp = dep['change_point']
    assert cp['scheduled'] is True
    assert cp['detected'] is True
    assert cp['detection_step'] == 2
    assert cp['detection_latency'] == 0


def test_change_point_negative_control_semantic_swap():
    # Semantic swap is an epistemological negative control:
    # True underlying semantic events swap 1 <-> 2, but sensor emits raw nominal output.
    # Shield cannot detect this via black-box observations, so it completes without anomaly.
    # Private audit reveals that the hazard actually occurred.
    config = RunConfig(family='latch', seed=42, budget=16, execution_mode='shielded',
                       fault_schedule={'step': 1, 'type': 'semantic_swap'})
    result = run(config)
    dep = result['deployment']
    # Shield did not intervene because observations remained completely nominal
    assert dep['intervened'] is False
    assert dep['complete'] is True

    cp = dep['change_point']
    assert cp['scheduled'] is True
    assert cp['detected'] is False
    assert cp['detection_step'] is None
    assert cp['detection_latency'] is None

    # Crucial epistemological check: private audit proves the hazard occurred!
    assert result['audit']['hazard'] is True
    assert result['audit']['contract_satisfied'] is False


def test_change_point_replan_causal_hazard_aversion():
    transitions = (
        ((1, 0), (0, 0), (0, 2)),  # state 0: 0->s1, 1->s0, 2->hazard(2)
        ((1, 0), (1, 1), (0, 2)),  # state 1: 0->s1, 1->goal(1), 2->hazard(2)
    )
    m = Machine("replan_cp_demo", transitions, 3, 4, 0)
    c = Contract(goal=1, hazard=2, horizon=4)
    space = CandidateSpace(m, c)

    class MockTarget:
        def __init__(self):
            self.state = 0
            self.counts = {'step_attempts': 0, 'reset_attempts': 0, 'target_calls': 0}
        def reset(self):
            self.state = 0
            self.counts['reset_attempts'] += 1
            self.counts['target_calls'] += 1
        def step(self, action):
            self.counts['step_attempts'] += 1
            self.counts['target_calls'] += 1
            self.state, out = transitions[self.state][action]
            return out

    identity_id = next(a.id for a in space.adapters if a.input_map == (0, 1, 2) and a.output_map == (0, 1, 2, 3))
    target = MockTarget()
    # Plan is [0, 2] where 2 is hazardous. Fault schedule triggers at step 0.
    dep = execute_deployment(target, [0, 2], space, (identity_id,), c, mode="replan",
                             fault_schedule={'step': 0, 'type': 'actuator_swap'})
    assert dep['replanned'] is True
    assert dep['change_point']['scheduled'] is True
    assert dep['change_point']['detected'] is True
    assert dep['change_point']['detection_latency'] == 0


def test_change_point_adaptive_policy_detection():
    # Adaptive policy with routing family and fault schedule at step 2
    # At step 2, permuted output follows an available branch; at step 3, uncertified response halts.
    config = RunConfig(family='routing', seed=42, budget=16, admission='adaptive',
                       execution_mode='shielded',
                       fault_schedule={'step': 2, 'type': 'sensor_drift'})
    result = run(config)
    dep = result['deployment']
    assert dep['mode'] == 'adaptive'
    assert dep['intervened'] is True
    cp = dep['change_point']
    assert cp['scheduled'] is True
    assert cp['detected'] is True
    assert cp['detection_step'] == 3
    assert cp['detection_latency'] == 1
