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


def test_observational_classes_distinguish_delay_and_initial_buffer():
    space = CandidateSpace(_machine(), Contract(), temporal=True)
    ids = (0, 144, 147)  # identity maps: static, delay with initial 0, initial 3
    assert space.predict(0, (0, 0)) != space.predict(144, (0, 0))
    assert space.predict(144, (0,)) != space.predict(147, (0,))
    assert space.ambiguity(ids)['observational_classes'] == 3


def test_observational_classes_merge_equivalent_static_and_delayed_models():
    machine = Machine('constant observation', (((0, 0), (0, 0), (0, 0)),))
    space = CandidateSpace(machine, Contract(), temporal=True)
    assert space.ambiguity((0, 144))['observational_classes'] == 1
    assert space.ambiguity((0, 144, 145))['observational_classes'] == 2


def test_temporal_classes_match_independent_exact_product_comparisons():
    machine = _machine()
    space = CandidateSpace(machine, Contract(horizon=1), temporal=True)
    selected = (0, 1, 24, 144, 145, 147, 148, 240, 241, 288)
    representatives = []
    for identifier in selected:
        adapter = space.adapters[identifier]
        if adapter.delay:
            # Independently materialize all source-state/output-buffer states.
            rows = tuple(tuple((following * machine.outputs + output, adapter.output_map[buffer])
                               for following, output in (machine.transitions[state][symbol]
                                                          for symbol in adapter.input_map))
                         for state in range(len(machine.transitions)) for buffer in range(machine.outputs))
            initial = machine.initial * machine.outputs + adapter.init_output
        else:
            rows = tuple(tuple((row[symbol][0], adapter.output_map[row[symbol][1]])
                               for symbol in adapter.input_map) for row in machine.transitions)
            initial = machine.initial
        target = Machine('materialized adapter', rows, initial=initial)
        if not any(compare_adapter(machine, space.adapters[other], target)['equivalent']
                   for other in representatives):
            representatives.append(identifier)
    assert space.ambiguity(selected)['observational_classes'] == len(representatives)


@pytest.mark.parametrize('delay', [0, 1])
@pytest.mark.parametrize('initial', [4, 100])
def test_adapter_rejects_initial_buffer_outside_output_alphabet(delay, initial):
    with pytest.raises(ValueError, match='init_output'):
        Adapter(0, (0, 1, 2), (0, 1, 2, 3), delay=delay, init_output=initial)
