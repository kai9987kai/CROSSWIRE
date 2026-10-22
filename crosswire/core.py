"""Finite Mealy adapters, exact behavior comparisons and bounded task admission.

Only public reference data and raw transcripts enter CandidateSpace. Work counts
are cumulative: new reference transition executions, new adapter/word expansions,
and actual candidate-pair comparisons. Cached results incur none of those costs.
"""

from collections import deque
from dataclasses import dataclass
from itertools import combinations, permutations, product
from random import Random


def _integer(value, name, minimum=0, maximum=None):
    if type(value) is not int:
        raise TypeError(f'{name} must be an integer')
    if value < minimum or (maximum is not None and value > maximum):
        raise ValueError(f'{name} out of bounds')
    return value


def _word(value, inputs):
    try:
        result = tuple(value)
    except TypeError as exc:
        raise TypeError('word must be a sequence') from exc
    for symbol in result:
        _integer(symbol, 'input', maximum=inputs - 1)
    return result


@dataclass(frozen=True)
class Machine:
    name: str
    transitions: tuple
    inputs: int = 3
    outputs: int = 4
    initial: int = 0

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name:
            raise ValueError('machine name must be a nonempty string')
        _integer(self.inputs, 'inputs', 1)
        _integer(self.outputs, 'outputs', 1)
        rows = tuple(tuple(tuple(cell) for cell in row) for row in self.transitions)
        if not rows:
            raise ValueError('machine needs at least one state')
        _integer(self.initial, 'initial', maximum=len(rows) - 1)
        for row in rows:
            if len(row) != self.inputs:
                raise ValueError('transition rows must match input alphabet')
            for cell in row:
                if len(cell) != 2:
                    raise ValueError('transition cell must contain next state and output')
                _integer(cell[0], 'next state', maximum=len(rows) - 1)
                _integer(cell[1], 'output', maximum=self.outputs - 1)
        object.__setattr__(self, 'transitions', rows)

    def trace(self, word):
        state, result = self.initial, []
        for symbol in _word(word, self.inputs):
            state, output = self.transitions[state][symbol]
            result.append(output)
        return tuple(result)

    def to_dict(self):
        return {'name': self.name, 'transitions': [[list(c) for c in r] for r in self.transitions],
                'inputs': self.inputs, 'outputs': self.outputs, 'initial': self.initial}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass(frozen=True)
class Contract:
    goal: int = 1
    hazard: int = 2
    horizon: int = 4

    def __post_init__(self):
        _integer(self.goal, 'goal', maximum=3)
        _integer(self.hazard, 'hazard', maximum=3)
        _integer(self.horizon, 'horizon', 1, 6)
        if self.goal == self.hazard:
            raise ValueError('goal and hazard must differ')

    def accepts(self, outputs):
        outputs = tuple(outputs)
        for symbol in outputs:
            _integer(symbol, 'semantic output', maximum=3)
        return bool(outputs) and outputs[-1] == self.goal and self.hazard not in outputs

    def to_dict(self):
        return {'goal': self.goal, 'hazard': self.hazard, 'horizon': self.horizon}

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass(frozen=True)
class Adapter:
    id: int
    input_map: tuple
    output_map: tuple
    delay: int = 0
    init_output: int = 0

    def __post_init__(self):
        _integer(self.id, 'adapter id')
        _integer(self.delay, 'delay', minimum=0, maximum=1)
        _integer(self.init_output, 'init_output', minimum=0)
        for name in ('input_map', 'output_map'):
            mapping = tuple(getattr(self, name))
            if not mapping:
                raise ValueError('adapter alphabets cannot be empty')
            for symbol in mapping:
                _integer(symbol, name, maximum=len(mapping) - 1)
            if len(set(mapping)) != len(mapping):
                raise ValueError(f'{name} must be bijective')
            object.__setattr__(self, name, mapping)

    def to_dict(self):
        result = {'id': self.id, 'input_map': list(self.input_map), 'output_map': list(self.output_map)}
        if self.delay:
            result['delay'] = self.delay
            result['init_output'] = self.init_output
        return result


def words(inputs, max_length):
    _integer(inputs, 'inputs', 1)
    _integer(max_length, 'max_length')
    return tuple(word for length in range(1, max_length + 1) for word in product(range(inputs), repeat=length))


class CandidateSpace:
    def __init__(self, machine, contract, temporal=False):
        if not isinstance(machine, Machine) or not isinstance(contract, Contract):
            raise TypeError('CandidateSpace requires a Machine and Contract')
        if max(contract.goal, contract.hazard) >= machine.outputs:
            raise ValueError('contract symbols exceed source alphabet')
        self.machine, self.contract = machine, contract
        self.temporal = bool(temporal)
        adapters = [Adapter(i, a, b) for i, (a, b) in enumerate(
            product(permutations(range(machine.inputs)), permutations(range(machine.outputs))))]
        if self.temporal:
            idx = len(adapters)
            for a, b in product(permutations(range(machine.inputs)), permutations(range(machine.outputs))):
                for init_o in range(machine.outputs):
                    adapters.append(Adapter(idx, a, b, delay=1, init_output=init_o))
                    idx += 1
        self.adapters = tuple(adapters)
        self.work = {'source_steps': 0, 'candidate_expansions': 0, 'pair_checks': 0}
        self._source = {(): (machine.initial, ())}
        self._predictions = {}
        self._semantics = {}
        self._safe = {}
        self._signatures = {}
        self._pair_weights = {}
        self._deployment = words(machine.inputs, contract.horizon)
        self._probes = words(machine.inputs, 3)

    def _adapter(self, identifier):
        return self.adapters[_integer(identifier, 'adapter id', maximum=len(self.adapters) - 1)]

    def _ids(self, ids):
        ids = tuple(ids)
        for identifier in ids:
            self._adapter(identifier)
        return tuple(sorted(set(ids)))

    def _source_trace(self, mapped):
        # Iterative prefixes avoid a recursion bound for imported long traces.
        prefix = ()
        for symbol in mapped:
            next_prefix = prefix + (symbol,)
            if next_prefix not in self._source:
                state, outputs = self._source[prefix]
                state, output = self.machine.transitions[state][symbol]
                self.work['source_steps'] += 1
                self._source[next_prefix] = (state, outputs + (output,))
            prefix = next_prefix
        return self._source[prefix][1]

    def _evaluate(self, identifier, word):
        adapter = self._adapter(identifier)
        word = _word(word, self.machine.inputs)
        key = (identifier, word)
        if key not in self._predictions:
            semantic = self._source_trace(tuple(adapter.input_map[i] for i in word))
            self._semantics[key] = semantic
            if adapter.delay == 1:
                preds = []
                for t in range(len(semantic)):
                    if t == 0:
                        preds.append(adapter.output_map[adapter.init_output])
                    else:
                        preds.append(adapter.output_map[semantic[t - 1]])
                self._predictions[key] = tuple(preds)
            else:
                self._predictions[key] = tuple(adapter.output_map[o] for o in semantic)
            self.work['candidate_expansions'] += 1
        return key

    def predict(self, identifier, word):
        return self._predictions[self._evaluate(identifier, word)]

    def semantic(self, identifier, word):
        return self._semantics[self._evaluate(identifier, word)]

    def safe_words(self, identifier):
        self._adapter(identifier)
        if identifier not in self._safe:
            self._safe[identifier] = frozenset(w for w in self._deployment if self.contract.accepts(self.semantic(identifier, w)))
        return self._safe[identifier]

    def _evidence(self, transcripts, anchors):
        evidence = []
        for transcript in transcripts:
            if type(transcript.get('complete')) is not bool:
                raise ValueError('transcript needs a boolean complete field')
            if not transcript['complete']:
                continue
            word = _word(transcript['word'], self.machine.inputs)
            outputs = tuple(transcript['outputs'])
            if len(outputs) != len(word):
                raise ValueError('complete transcript word/output lengths differ')
            for symbol in outputs:
                _integer(symbol, 'raw output', maximum=self.machine.outputs - 1)
            evidence.append((word, outputs))
        validated = dict(anchors or {})
        for raw, semantic in validated.items():
            _integer(raw, 'anchor raw output', maximum=self.machine.outputs - 1)
            _integer(semantic, 'anchor semantic output', maximum=self.machine.outputs - 1)
        return evidence, validated

    def losses(self, transcripts, anchors=None):
        evidence, anchors = self._evidence(transcripts, anchors)
        result = {}
        for adapter in self.adapters:
            result[adapter.id] = sum(p != o for word, outputs in evidence for p, o in zip(self.predict(adapter.id, word), outputs))
            result[adapter.id] += sum(adapter.output_map[semantic] != raw for raw, semantic in anchors.items())
        return result

    def survivors(self, transcripts, anchors=None):
        return tuple(identifier for identifier, loss in self.losses(transcripts, anchors).items() if loss == 0)

    def choose_probe(self, ids, policy, remaining_steps, seen, seed=0):
        if policy not in ('fixed', 'random', 'disagreement', 'task', 'counterexample'):
            raise ValueError('unknown probe policy')
        ids = self._ids(ids)
        _integer(remaining_steps, 'remaining steps')
        _integer(seed, 'seed', maximum=2**32 - 1)
        seen = {_word(w, self.machine.inputs) for w in seen}
        # remaining_steps is the action allowance after the caller has reserved
        # the reset for this query. Scores still charge reset + actions in their
        # information/cost ratio.
        eligible = [w for w in self._probes if w not in seen and len(w) <= remaining_steps]
        if not eligible:
            return None
        if policy == 'fixed':
            return eligible[0]
        if policy == 'random':
            return Random(seed).choice(sorted(eligible))
        if policy == 'disagreement':
            best, best_score = None, 0
            n = len(ids)
            total_pairs = n * (n - 1) // 2
            for word in eligible:
                counts = {}
                for i in ids:
                    p = self.predict(i, word)
                    counts[p] = counts.get(p, 0) + 1
                agreeing = sum(c * (c - 1) // 2 for c in counts.values())
                separated = total_pairs - agreeing
                self.work['pair_checks'] += total_pairs
                score = separated / (1 + len(word))
                if score > best_score:
                    best, best_score = word, score
            return best
        if policy == 'counterexample':
            # CEGP: Counterexample-Guided Active Probing
            n = len(ids)
            total_pairs = n * (n - 1) // 2
            if not total_pairs:
                return eligible[0]
            # Efficiently find distinguishing probe words that separate maximal candidate pairs
            best, best_score = None, -1.0
            for word in eligible:
                counts = {}
                for i in ids:
                    p = self.predict(i, word)
                    counts[p] = counts.get(p, 0) + 1
                agreeing = sum(c * (c - 1) // 2 for c in counts.values())
                separated = total_pairs - agreeing
                self.work['pair_checks'] += total_pairs
                if separated:
                    score = separated / (1 + len(word))
                    if score > best_score:
                        best, best_score = word, score
            return best if best is not None else eligible[0]
        best, best_score = None, 0
        pairs = tuple(combinations(ids, 2))
        weighted_pairs = []
        for a, b in pairs:
            if policy == 'task':
                pair = (a, b)
                if pair not in self._pair_weights:
                    sa, sb = self.safe_words(a), self.safe_words(b)
                    self._pair_weights[pair] = len(sa ^ sb) / max(1, len(sa | sb))
                weight = self._pair_weights[pair]
            else:
                weight = 1
            if weight:
                weighted_pairs.append((a, b, weight))
        for word in eligible:
            predictions = {i: self.predict(i, word) for i in ids}
            total = 0.0
            self.work['pair_checks'] += len(weighted_pairs)
            for a, b, weight in weighted_pairs:
                if predictions[a] != predictions[b]:
                    total += weight
            score = total / (1 + len(word))
            if score > best_score:
                best, best_score = word, score
        return best

    def plan(self, ids, mode='robust', transcripts=None, anchors=None):
        if mode not in ('robust', 'one_best', 'unique', 'fit', 'identity', 'abstain'):
            raise ValueError('unknown admission mode')
        ids = self._ids(ids)
        chosen = ids
        if mode == 'fit':
            losses = self.losses(transcripts or [], anchors)
            chosen = (min(losses, key=lambda i: (losses[i], i)),)
        elif mode == 'identity':
            chosen = (next(a.id for a in self.adapters if a.input_map == tuple(range(self.machine.inputs))
                           and a.output_map == tuple(range(self.machine.outputs))),)
        elif mode == 'one_best':
            chosen = ids[:1]
        elif mode == 'unique' and len(ids) != 1:
            chosen = ()
        elif mode == 'abstain':
            chosen = ()
        safe = set(self.safe_words(chosen[0])) if chosen else set()
        for identifier in chosen[1:]:
            safe.intersection_update(self.safe_words(identifier))
        word = min(safe, key=lambda w: (len(w), w)) if safe else None
        status = ('IDENTIFIED' if len(ids) == 1 else 'TASK_ADMISSIBLE') if word is not None else (
            'FAMILY_CONTRADICTED' if not ids else 'UNRESOLVED')
        return {'status': status, 'admitted': word is not None, 'word': list(word) if word is not None else None,
                'candidate_count': len(ids)}

    def _signature(self, identifier):
        """Canonical minimized reachable raw transducer, independent of state IDs."""
        if identifier in self._signatures:
            return self._signatures[identifier]
        adapter = self._adapter(identifier)
        states, pending, rows = {self.machine.initial}, deque([self.machine.initial]), {}
        while pending:
            state = pending.popleft()
            row = []
            for symbol in adapter.input_map:
                following, output = self.machine.transitions[state][symbol]
                self.work['source_steps'] += 1
                row.append((following, adapter.output_map[output]))
                if following not in states:
                    states.add(following)
                    pending.append(following)
            rows[state] = tuple(row)
        classes = {state: 0 for state in states}
        while True:
            labels, refined = {}, {}
            for state in sorted(states):
                signature = tuple((output, classes[following]) for following, output in rows[state])
                refined[state] = labels.setdefault(signature, len(labels))
            # Refinement never merges old classes; unchanged count means stable.
            if len(set(refined.values())) == len(set(classes.values())):
                classes = refined
                break
            classes = refined
        representatives = {classes[s]: s for s in sorted(states)}
        start = classes[self.machine.initial]
        canonical, pending, result = {start: 0}, deque([start]), []
        while pending:
            current = pending.popleft()
            row = []
            for following, output in rows[representatives[current]]:
                following = classes[following]
                if following not in canonical:
                    canonical[following] = len(canonical)
                    pending.append(following)
                row.append((canonical[following], output))
            result.append(tuple(row))
        self._signatures[identifier] = tuple(result)
        return self._signatures[identifier]

    def ambiguity(self, ids):
        ids = self._ids(ids)
        return {'map_count': len(ids), 'observational_classes': len({self._signature(i) for i in ids}),
                'contract_classes': len({self.safe_words(i) for i in ids})}


def compare_adapter(machine, adapter, target):
    """Exact product BFS; first mismatch gives a shortest lexicographic witness."""
    if machine.inputs != target.inputs or machine.outputs != target.outputs:
        raise ValueError('comparison machine alphabets differ')
    if len(adapter.input_map) != machine.inputs or len(adapter.output_map) != machine.outputs:
        raise ValueError('adapter alphabets differ')
    is_temporal = bool(getattr(adapter, 'delay', 0))
    initial = (machine.initial, target.initial, adapter.init_output) if is_temporal else (machine.initial, target.initial)
    visited, pending = {initial}, deque([(initial, ())])
    steps = 0
    while pending:
        curr, prefix = pending.popleft()
        source_state, target_state = curr[0], curr[1]
        buffered = curr[2] if is_temporal else None
        for symbol in range(machine.inputs):
            source_next, semantic = machine.transitions[source_state][adapter.input_map[symbol]]
            target_next, raw = target.transitions[target_state][symbol]
            steps += 1
            word = prefix + (symbol,)
            pred_raw = adapter.output_map[buffered if is_temporal else semantic]
            if pred_raw != raw:
                return {'equivalent': False, 'counterexample': list(word), 'visited_pairs': len(visited),
                        'source_steps': steps, 'target_model_steps': steps}
            following = (source_next, target_next, semantic) if is_temporal else (source_next, target_next)
            if following not in visited:
                visited.add(following)
                pending.append((following, word))
    return {'equivalent': True, 'counterexample': None, 'visited_pairs': len(visited),
            'source_steps': steps, 'target_model_steps': steps}
