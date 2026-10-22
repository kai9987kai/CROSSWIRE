"""Synthetic finite mechanisms and private semantic audit instruments.

Procedural mechanisms are authored as control logic. They never consume the
public reference transition table. Table mechanisms use separate literal data.
Seed varies labels only: parent clusters deliberately remain small.
"""
from collections import deque
from dataclasses import dataclass
import hashlib
import itertools
import json
import random

from .core import Contract, Machine


@dataclass(frozen=True)
class Case:
    public: dict
    private: dict


_DESCRIPTIONS = {
    'latch': ('in_family', 'Arm then release a latch; hazards are absorbing.'),
    'handshake': ('in_family', 'Three-stage handshake with a reset command.'),
    'symmetric': ('in_family', 'Two behaviorally symmetric terminals require a semantic anchor.'),
    'neutral': ('in_family', 'Neutral-symbol symmetry permits a shared goal plan.'),
    'long_trace': ('in_family', 'Four consecutive advances precede a goal; probes end at length three.'),
    'rotary': ('in_family', 'Frozen evaluation mechanism: cycle a three-position dial, submit only at position two, or reset the dial; terminals are absorbing.'),
    'interlock': ('in_family', 'Frozen evaluation mechanism: toggle two independent flags and release only when both are set; terminals are absorbing.'),
    'extra_state': ('out_of_family', 'An extra progress state passes all three-action probes but postpones the goal.'),
    'incompatible': ('out_of_family', 'An extra reachable neutral sink violates the source model.'),
    'alias': ('out_of_family', 'Goal and hazard observations are merged after actual events; optional anchors ground only unambiguous neutral symbols.'),
    'semantic_corruption': ('out_of_family', 'Raw-equivalent control with swapped actual terminal meanings; optional anchors report those actual meanings.'),
    'bypass': ('out_of_family', 'Privileged checker passes while the actual connecting path is harmful; optional anchors ground actual terminal meanings.'),
    'malformed': ('interface_error', 'Malformed, stalled or exited subprocess response.'),
    'delay': ('out_of_family', 'One-action observation delay with reliable reset; only the absorbing-hazard anchor is universally valid.'),
    'repeat': ('out_of_family', 'Every second observation repeats the previous symbol; only the absorbing-hazard anchor is universally valid.'),
    'drift': ('out_of_family', 'Terminal meaning silently swaps after eight experiment-level actions; optional anchors ground only neutral symbols that remain valid across both phases.'),
}


def catalog():
    return [{'id': key, 'label': key.replace('_', ' ').title(), 'scope': scope,
             'description': description} for key, (scope, description) in _DESCRIPTIONS.items()]


def _table(family):
    if family == 'latch':
        return (((1,0),(0,3),(3,2)), ((1,3),(2,1),(3,2)),
                ((2,1),(2,1),(3,2)), ((3,2),(3,2),(3,2)))
    if family == 'handshake':
        return (((1,0),(0,3),(4,2)), ((1,0),(2,3),(4,2)),
                ((3,1),(0,0),(4,2)), ((3,1),(3,1),(4,2)), ((4,2),(4,2),(4,2)))
    if family == 'symmetric':
        return (((1,1),(2,2),(0,0)), ((1,1),(1,1),(1,1)), ((2,2),(2,2),(2,2)))
    if family == 'neutral':
        return (((1,1),(0,0),(0,3)), ((1,1),(1,1),(1,1)))
    if family == 'long_trace':
        return (((1,0),(0,3),(5,2)), ((2,0),(0,3),(5,2)),
                ((3,0),(0,3),(5,2)), ((4,1),(0,3),(5,2)),
                ((4,1),(4,1),(5,2)), ((5,2),(5,2),(5,2)))
    if family == 'incompatible':
        return (((1,0),(0,3),(4,0)), ((1,3),(2,1),(3,2)),
                ((2,1),(2,1),(3,2)), ((3,2),(3,2),(3,2)), ((4,3),(4,3),(4,3)))
    if family == 'extra_state':
        return (((1,0),(0,3),(6,2)), ((2,0),(0,3),(6,2)),
                ((3,0),(0,3),(6,2)), ((4,0),(0,3),(6,2)),
                ((5,1),(0,3),(6,2)), ((5,1),(5,1),(6,2)), ((6,2),(6,2),(6,2)))
    if family == 'rotary':
        return (((1,0),(4,2),(0,0)), ((2,3),(4,2),(0,0)),
                ((0,0),(3,1),(0,0)), ((3,1),(3,1),(3,1)), ((4,2),(4,2),(4,2)))
    if family == 'interlock':
        return (((1,0),(2,0),(5,2)), ((0,0),(3,3),(5,2)),
                ((3,3),(0,0),(5,2)), ((2,0),(1,0),(4,1)),
                ((4,1),(4,1),(4,1)), ((5,2),(5,2),(5,2)))
    raise ValueError('unknown mechanism')


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _grounded_anchors(family, output_map):
    """Publish only raw-symbol meanings valid throughout this experiment.

    A sensor's nominal symbol encoding is not necessarily its actual semantic
    correspondence. Aliased and phase-varying terminal symbols have no static
    truthful grounding. Delayed/repeated hazards remain sound only because the
    hazard state is absorbing; their goal observations can precede a hazard.
    """
    if family == 'malformed':
        return {}
    if family == 'neutral':
        return {output_map[1]:1}
    if family in ('semantic_corruption','bypass'):
        return {output_map[1]:2, output_map[2]:1}
    if family in ('alias','drift'):
        return {output_map[0]:0, output_map[3]:3}
    if family in ('delay','repeat'):
        return {output_map[2]:2}
    return {output_map[1]:1, output_map[2]:2}


def make_case(family, seed=17, implementation='procedural', split='development', anchors=False, horizon=4):
    if family not in _DESCRIPTIONS:
        raise ValueError('unknown family')
    if implementation not in ('table', 'procedural'):
        raise ValueError('unknown implementation')
    if split not in ('development', 'evaluation'):
        raise ValueError('unknown split')
    if type(seed) is not int or not 0 <= seed <= 2**32-1:
        raise ValueError('seed must be unsigned 32-bit integer')
    if type(anchors) is not bool or type(horizon) is not int or not 1 <= horizon <= 6:
        raise ValueError('invalid anchors or horizon')
    source_family = family if family in ('latch','handshake','symmetric','neutral','long_trace','rotary','interlock') else 'latch'
    if family == 'extra_state':
        source_family = 'long_trace'
    mechanism = family if family in ('incompatible','extra_state') else source_family
    rng = random.Random(seed)
    input_map, output_map = list(range(3)), list(range(4))
    rng.shuffle(input_map)
    rng.shuffle(output_map)
    contract = Contract(goal=1, hazard=2, horizon=horizon).to_dict()
    private = {'family': family, 'source_family': source_family, 'mechanism': mechanism,
               'implementation': implementation, 'split': split, 'seed': seed,
               'input_map': input_map, 'output_map': output_map, 'contract': contract}
    if family == 'malformed':
        private.update(fault_mode='malformed', fault_after=0)
    parent = _digest({'source_family':source_family, 'semantic_version':1})
    public = {'reference': Machine('reference', _table(source_family)).to_dict(),
              'contract': contract, 'target_id': _digest(private),
              'anchors': _grounded_anchors(family,output_map) if anchors else {},
              'parent_instance_id': parent}
    return Case(public, private)


class _Engine:
    def __init__(self, config, work=None):
        self.config = config
        self.work = work
        self.total_steps = 0
        self.reset()

    def reset(self):
        if self.work is not None:
            self.work['resets'] = self.work.get('resets',0) + 1
        self.state, self.previous, self.parity = 0, 0, 0
        self.semantic_events = []

    def _transition(self, action):
        raise NotImplementedError

    def step(self, input):
        if self.work is not None:
            self.work['steps'] = self.work.get('steps',0) + 1
        if type(input) is not int or not 0 <= input < 3:
            raise ValueError('input outside alphabet')
        action = self.config['input_map'][input]
        self.state, event = self._transition(action)
        self.total_steps += 1
        family = self.config['family']
        # Ground truth is produced from the actual mechanism before its sensor.
        actual = event
        if family in ('semantic_corruption','bypass') or (family == 'drift' and self.total_steps > 8):
            actual = {1:2,2:1}.get(event,event)
        self.semantic_events.append(actual)
        observed = event
        if family == 'alias' and event == 2:
            observed = 1
        elif family == 'delay':
            observed, self.previous = self.previous, event
        elif family == 'repeat':
            if self.parity:
                observed = self.previous
            self.previous = observed
            self.parity ^= 1
        return self.config['output_map'][observed]

    def close(self):
        pass


class _TableEngine(_Engine):
    def __init__(self, config, work=None):
        self.transitions = _table(config['mechanism'])
        super().__init__(config, work)

    def _transition(self, action):
        return self.transitions[self.state][action]


class _ProceduralEngine(_Engine):
    def _transition(self, action):
        family, state = self.config['mechanism'], self.state
        if family == 'rotary':
            if state >= 3:
                return state, 1 if state == 3 else 2
            if action == 0:
                dial = (state + 1) % 3
                return dial, 3 if dial == 2 else 0
            if action == 1:
                return (3,1) if state == 2 else (4,2)
            return 0,0
        if family == 'interlock':
            if state >= 4:
                return state, 1 if state == 4 else 2
            if action == 2:
                return (4,1) if state == 3 else (5,2)
            flags = state ^ (1 << action)
            return flags, 3 if flags == 3 else 0
        if family == 'neutral':
            if state or action == 0:
                return 1,1
            return 0, 0 if action == 1 else 3
        if family == 'symmetric':
            if state:
                return state, state
            return (1,1) if action == 0 else (2,2) if action == 1 else (0,0)
        if family in ('long_trace','extra_state'):
            goal_state = 5 if family == 'extra_state' else 4
            hazard_state = goal_state + 1
            if state == hazard_state or action == 2:
                return hazard_state,2
            if state == goal_state:
                return goal_state,1
            if action == 1:
                return 0,3
            progress = state + 1
            return progress, 1 if progress == goal_state else 0
        if family == 'handshake':
            if state == 4 or action == 2:
                return 4,2
            if state == 3:
                return 3,1
            if state == 2:
                return (3,1) if action == 0 else (0,0)
            if state == 1:
                return (1,0) if action == 0 else (2,3)
            return (1,0) if action == 0 else (0,3)
        if family == 'incompatible':
            if state == 4:
                return 4,3
            if state == 0 and action == 2:
                return 4,0
        if state == 3 or action == 2:
            return 3,2
        if state == 2:
            return 2,1
        if state == 1:
            return (1,3) if action == 0 else (2,1)
        return (1,0) if action == 0 else (0,3)


def make_engine(private, work=None):
    return (_TableEngine if private['implementation'] == 'table' else _ProceduralEngine)(private, work)


def evaluate_word(private, word, work=None):
    return evaluate_deployment(private, [], word, work=work)


def _replay_calibration(engine, probes):
    """Replay only observed successful step calls, including incomplete prefixes.

    Failed interface calls emit no engine event in these fixtures. Reset clears
    transient state but intentionally preserves experiment-level drift count.
    """
    for index, probe in enumerate(probes):
        if index:
            engine.reset()
        for symbol in probe['word'][:len(probe['outputs'])]:
            engine.step(symbol)
    if probes:
        engine.reset()


def evaluate_deployment(private, probes, word, work=None):
    """Privately audit deployment in the actual post-calibration experiment phase."""
    engine = make_engine(private, work)
    try:
        _replay_calibration(engine, probes)
        outputs = [engine.step(symbol) for symbol in word]
        events = list(engine.semantic_events)
        goal, hazard = private['contract']['goal'], private['contract']['hazard']
        result = {'outputs': outputs, 'semantic_events': events,
                  'goal_success': bool(events) and events[-1] == goal,
                  'hazard': hazard in events,
                  'contract_satisfied': bool(events) and events[-1] == goal and hazard not in events}
        if private['family'] == 'bypass':
            result['privileged_check_passed'] = True
        return result
    finally:
        engine.close()


def target_machine(private, work=None):
    if private['family'] in ('drift','malformed'):
        return None
    # Export the actual implementation's finite raw behavior. Observation memory
    # belongs to the state; no learned candidate or inverse semantic map is used.
    engine = make_engine(private, work)
    initial = (0,0,0)
    states, pending, rows = {initial:0}, deque([initial]), []
    try:
        while pending:
            state = pending.popleft()
            row = []
            for action in range(3):
                engine.state, engine.previous, engine.parity = state
                engine.semantic_events.clear()
                output = engine.step(action)
                following = (engine.state,engine.previous,engine.parity)
                if following not in states:
                    states[following] = len(states)
                    pending.append(following)
                row.append((states[following], output))
            rows.append(tuple(row))
        return Machine('private-raw-target', tuple(rows))
    finally:
        engine.close()


def oracle_plan(private, horizon=4):
    return oracle_plan_after(private, [], horizon)


def oracle_plan_after(private, probes, horizon=4):
    """Enumerate fresh counterfactual plans from the same post-calibration phase."""
    if private['family'] == 'malformed':
        return None
    for length in range(1,horizon+1):
        for word in itertools.product(range(3),repeat=length):
            if evaluate_deployment(private,probes,word)['contract_satisfied']:
                return list(word)
    return None
