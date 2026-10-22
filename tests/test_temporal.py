import pytest
from crosswire.core import Adapter, CandidateSpace, Contract, Machine, compare_adapter
from crosswire.fixtures import Case, make_case


def _machine():
    transitions = (((1, 0), (0, 3), (1, 2)), ((1, 1), (1, 1), (1, 2)))
    return Machine("test", transitions, 3, 4, 0)


def test_temporal_candidate_space_size():
    m = _machine()
    c = Contract(goal=1, hazard=2, horizon=4)
    static_space = CandidateSpace(m, c, temporal=False)
    assert len(static_space.adapters) == 144

    temporal_space = CandidateSpace(m, c, temporal=True)
    # 144 static + (144 * 4 initial output options) = 720 adapters
    assert len(temporal_space.adapters) == 720


def test_temporal_adapter_predicts_delayed_output():
    m = _machine()
    c = Contract(goal=1, hazard=2, horizon=4)
    space = CandidateSpace(m, c, temporal=True)
    # Pick a temporal adapter (id >= 144)
    temporal_adapter = next(a for a in space.adapters if a.delay == 1)
    word = [0, 0, 1]
    preds = space.predict(temporal_adapter.id, word)
    assert len(preds) == len(word)
    # At t=0, output is the mapped init_output
    assert preds[0] == temporal_adapter.output_map[temporal_adapter.init_output]


def test_temporal_adapter_eliminates_delay_fixture_mismatch():
    case = make_case("delay", seed=17)
    space = CandidateSpace(Machine.from_dict(case.public["reference"]), Contract.from_dict(case.public["contract"]), temporal=True)
    # In delay fixture, an observation delay of 1 exists.
    # Static adapters have non-zero loss or fail to explain delayed traces;
    # with temporal adapters, there exists a delay=1 adapter that matches!
    # Generate a trace from delay fixture
    from crosswire.fixtures import make_engine
    engine = make_engine(case.private)
    probes = [{"word": [0, 1, 0], "outputs": [engine.step(0), engine.step(1), engine.step(0)], "complete": True}]
    losses = space.losses(probes)
    zero_loss = [aid for aid, loss in losses.items() if loss == 0]
    assert len(zero_loss) > 0
    # At least one zero loss adapter has delay == 1
    assert any(space.adapters[aid].delay == 1 for aid in zero_loss)
