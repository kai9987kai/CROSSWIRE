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
        for name in ('input_map', 'output_map'):
            mapping = tuple(getattr(self, name))
            if not mapping:
                raise ValueError('adapter alphabets cannot be empty')
            for symbol in mapping:
                _integer(symbol, name, maximum=len(mapping) - 1)
            if len(set(mapping)) != len(mapping):
                raise ValueError(f'{name} must be bijective')
            object.__setattr__(self, name, mapping)
        _integer(self.init_output, 'init_output', maximum=len(self.output_map) - 1)

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

    def level_ids(self, level):
        """Nested hypothesis classes: 'static' (144 memoryless maps) ⊂ 'temporal' (all)."""
        if level == 'static':
            return tuple(a.id for a in self.adapters if a.delay == 0)
        if level == 'temporal':
            return tuple(a.id for a in self.adapters)
        raise ValueError('unknown hypothesis level')

    def _decision_classes(self, ids):
        """Group survivors by their contract-relevant behaviour (safe deployment set)."""
        classes = {}
        for identifier in ids:
            classes.setdefault(self.safe_words(identifier), []).append(identifier)
        return list(classes.items())

    def distinguishing_word(self, a, b, max_length):
        """Shortest lexicographic input word on which adapters a and b predict different raw outputs.

        Exact BFS over the joint state (reference state under a, under b, and each
        adapter's one-step output buffer). Unlike the fixed probe pool, the witness
        may be longer than three actions; it is bounded only by ``max_length``.
        """
        A, B = self._adapter(a), self._adapter(b)
        start = (self.machine.initial, self.machine.initial,
                 A.init_output if A.delay else None, B.init_output if B.delay else None)
        visited, pending = {start}, deque([(start, ())])
        while pending:
            (qa, qb, ba, bb), prefix = pending.popleft()
            if len(prefix) >= max_length:
                continue
            for symbol in range(self.machine.inputs):
                na, sa = self.machine.transitions[qa][A.input_map[symbol]]
                nb, sb = self.machine.transitions[qb][B.input_map[symbol]]
                self.work['source_steps'] += 2
                oa = A.output_map[ba if A.delay else sa]
                ob = B.output_map[bb if B.delay else sb]
                word = prefix + (symbol,)
                if oa != ob:
                    return word
                state = (na, nb, sa if A.delay else None, sb if B.delay else None)
                if state not in visited:
                    visited.add(state)
                    pending.append((state, word))
        return None

    def _weighted_separation(self, classes, word, weights):
        """Sum of weights of survivor pairs separated by ``word`` (class-level, O(N + C^2 P))."""
        counts = []
        for _, members in classes:
            tally = {}
            for identifier in members:
                p = self.predict(identifier, word)
                tally[p] = tally.get(p, 0) + 1
            counts.append((len(members), tally))
        total = 0.0
        for i in range(len(counts)):
            for j in range(i + 1, len(counts)):
                w = weights[i][j]
                if not w:
                    continue
                (na, ta), (nb, tb) = counts[i], counts[j]
                agree = sum(c * tb.get(p, 0) for p, c in ta.items())
                total += w * (na * nb - agree)
                self.work['pair_checks'] += na * nb
        return total

    def probe_is_safe(self, ids, word):
        """Check prefix hazard freedom under every live semantic interpretation.

        This is conditional on inclusion in the declared finite model family;
        raw response agreement alone does not certify the target's semantics.
        """
        ids = self._ids(ids)
        word = _word(word, self.machine.inputs)
        return bool(ids) and all(self.contract.hazard not in self.semantic(i, word) for i in ids)

    def choose_branching_step(self, ids, word_prefix=(), safe_only=False, safe_ids=None, seed=0):
        """Select the next within-query action conditioned on the live belief and query prefix.

        Chooses an action maximizing predictive output entropy across surviving models.
        If safe_only=True, only actions where all surviving models in safe_ids predict zero hazard on
        this step are considered eligible.
        """
        import math
        ids = self._ids(ids)
        if not ids or len(ids) <= 1:
            return None
        if safe_ids is None:
            safe_ids = ids
        prefix = _word(word_prefix, self.machine.inputs)
        best_action, best_score = None, -1.0
        n = len(ids)
        order = [(seed + offset) % self.machine.inputs for offset in range(self.machine.inputs)]
        for a in order:
            extended = prefix + (a,)
            if safe_only and not self.probe_is_safe(safe_ids, extended):
                continue
            counts = {}
            for i in ids:
                p = self.predict(i, extended)[-1]
                counts[p] = counts.get(p, 0) + 1
            h = 0.0
            for c in counts.values():
                prob = c / n
                h -= prob * math.log2(prob)
            self.work['pair_checks'] += n
            if h > best_score:
                best_action, best_score = a, h
        if best_score <= 0.0:
            # When models agree on predicted outputs, fall back to the rotating
            # eligible action to test the hypothesis against target observations.
            for a in order:
                extended = prefix + (a,)
                if not safe_only or self.probe_is_safe(safe_ids, extended):
                    return a
            return None
        return best_action

    def choose_probe(self, ids, policy, remaining_steps, seen, seed=0, safe_only=False):
        if policy not in ('fixed', 'random', 'disagreement', 'task', 'counterexample', 'entropy', 'ec2', 'branching'):
            raise ValueError('unknown probe policy')
        if type(safe_only) is not bool:
            raise TypeError('safe_only must be a boolean')
        ids = self._ids(ids)
        _integer(remaining_steps, 'remaining steps')
        _integer(seed, 'seed', maximum=2**32 - 1)
        seen = {_word(w, self.machine.inputs) for w in seen}
        if not ids:
            return None
        # remaining_steps is the action allowance after the caller has reserved
        # the reset for this query. Scores still charge reset + actions in their
        # information/cost ratio.
        eligible = [w for w in self._probes if w not in seen and len(w) <= remaining_steps]
        if safe_only:
            eligible = [w for w in eligible if self.probe_is_safe(ids, w)]
        if not eligible and policy != 'counterexample':
            return None
        if policy == 'fixed':
            return eligible[0]
        if policy == 'random':
            return Random(seed).choice(sorted(eligible))
        if policy == 'entropy':
            import math
            best, best_score = None, -1.0
            n = len(ids)
            if not ids:
                return None
            if n == 1:
                return eligible[0] if eligible else None
            for word in eligible:
                counts = {}
                for i in ids:
                    p = self.predict(i, word)
                    counts[p] = counts.get(p, 0) + 1
                h = 0.0
                for c in counts.values():
                    prob = c / n
                    h -= prob * math.log2(prob)
                self.work['pair_checks'] += n
                score = h / (1 + len(word))
                if score > best_score:
                    best, best_score = word, score
            return best
        if policy == 'ec2':
            # Equivalence Class Edge Cutting (EC2):
            # Prioritizes probes that cut edges between differing contract decision classes.
            classes = self._decision_classes(ids)
            if len(classes) <= 1:
                return min(eligible, key=lambda w: (len(w), w)) if eligible else None
            weights = [[len(sa ^ sb) / max(1, len(sa | sb)) for sb, _ in classes] for sa, _ in classes]
            best, best_score = None, -1.0
            for word in eligible:
                score = self._weighted_separation(classes, word, weights) / (1 + len(word))
                if score > best_score:
                    best, best_score = word, score
            if best_score <= 0.0:
                return min(eligible, key=lambda w: (len(w), w)) if eligible else None
            return best
        if policy == 'branching':
            step_action = self.choose_branching_step(ids, (), safe_only=safe_only)
            if step_action is not None and (step_action,) in eligible:
                return (step_action,)
            return eligible[0] if eligible else None
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
            # Decision-focused counterexample-guided probing. Candidate words are
            # the fixed pool plus exact shortest witnesses separating one
            # representative pair for every pair of *decision classes* (survivors
            # whose admissible deployment sets differ). Witnesses may exceed the
            # three-action pool. Pairs are weighted as in the task policy
            # (Jaccard distance of safe sets), computed per class, not per pair.
            classes = self._decision_classes(ids)
            if len(classes) > 1:
                weights = [[len(sa ^ sb) / max(1, len(sa | sb)) for sb, _ in classes] for sa, _ in classes]
            else:
                # No decision-relevant disagreement: fall back to plain separation.
                classes = [(frozenset(), [i]) for i in ids]
                weights = [[0 if i == j else 1 for j in range(len(classes))] for i in range(len(classes))]
                if len(classes) > 64:
                    classes = classes[:64]
                    weights = [row[:64] for row in weights[:64]]
            pool = list(eligible)
            if len(classes) > 1:
                limit = min(remaining_steps, self.contract.horizon + 4)
                for i in range(len(classes)):
                    for j in range(i + 1, len(classes)):
                        if not weights[i][j]:
                            continue
                        witness = self.distinguishing_word(classes[i][1][0], classes[j][1][0], limit)
                        if (witness is not None and witness not in seen and witness not in pool
                                and (not safe_only or self.probe_is_safe(ids, witness))):
                            pool.append(witness)
            best, best_score = None, 0.0
            for word in pool:
                score = self._weighted_separation(classes, word, weights) / (1 + len(word))
                if score > best_score:
                    best, best_score = word, score
            return best
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

    def plan(self, ids, mode='robust', transcripts=None, anchors=None, risk_tolerance=0.0):
        if mode not in ('robust', 'one_best', 'unique', 'fit', 'identity', 'abstain', 'risk_controlled'):
            raise ValueError('unknown admission mode')
        # The bounds reject NaN/infinity as well as unsupported numeric aliases;
        # validating before any empty-belief return keeps the public API strict.
        if type(risk_tolerance) not in (int, float) or not 0 <= risk_tolerance < 1:
            raise ValueError('risk_tolerance must be a finite number in [0, 1)')
        ids = self._ids(ids)
        if mode == 'risk_controlled':
            if not ids:
                return {'status': 'FAMILY_CONTRADICTED', 'admitted': False, 'word': None,
                        'candidate_count': 0, 'risk_metrics': {'hazard_risk': None, 'goal_rate': None, 'tolerance': risk_tolerance}}
            n = len(ids)
            admissible_candidates = []
            for w in self._deployment:
                h_count = sum(self.contract.hazard in self.semantic(i, w) for i in ids)
                g_count = sum(self.contract.accepts(self.semantic(i, w)) for i in ids)
                h_risk = h_count / n
                g_rate = g_count / n
                if h_risk <= risk_tolerance and (n - g_count) / n <= risk_tolerance:
                    admissible_candidates.append((w, h_risk, g_rate))
            if not admissible_candidates:
                return {'status': 'UNRESOLVED', 'admitted': False, 'word': None,
                        'candidate_count': n, 'risk_metrics': {'hazard_risk': None, 'goal_rate': None, 'tolerance': risk_tolerance}}
            best_w, best_h_risk, best_g_rate = min(
                admissible_candidates,
                key=lambda item: (len(item[0]), item[1], -item[2], item[0])
            )
            status = 'IDENTIFIED' if n == 1 else ('TASK_ADMISSIBLE' if best_h_risk == 0.0 and best_g_rate == 1.0 else 'RISK_CONTROLLED_ADMISSIBLE')
            return {
                'status': status,
                'admitted': True,
                'word': list(best_w),
                'candidate_count': n,
                'risk_metrics': {
                    'hazard_risk': best_h_risk,
                    'goal_rate': best_g_rate,
                    'tolerance': risk_tolerance,
                    'candidate_count': n
                }
            }
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
        # Delayed observations depend on both the source state and the previous
        # semantic output. Minimize that augmented transducer, so raw-equivalent
        # static/delayed models can merge while distinct buffers remain separate.
        initial = (self.machine.initial, adapter.init_output if adapter.delay else None)
        states, pending, rows = {initial}, deque([initial]), {}
        while pending:
            state = pending.popleft()
            source_state, buffered = state
            row = []
            for symbol in adapter.input_map:
                source_next, output = self.machine.transitions[source_state][symbol]
                self.work['source_steps'] += 1
                following = (source_next, output if adapter.delay else None)
                row.append((following, adapter.output_map[buffered if adapter.delay else output]))
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
        start = classes[initial]
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



class _LazyAdapters:
    def __init__(self, space):
        self._space = space

    def __len__(self):
        return self._space.total_adapters

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return [self[i] for i in range(*idx.indices(len(self)))]
        return self._space.adapter(idx)

    def __iter__(self):
        for i in range(len(self)):
            yield self._space.adapter(i)


class FactoredCandidateSpace:
    """Factored permutation space decomposing candidate adapters into orthogonal input/output factors.

    Instead of enumerating N_I * N_O * (1 + N_O) adapters in flat memory, decomposes
    the hypothesis space into P_I x P_O (and temporal initial delay buffers).
    Semantic evaluation depends strictly on P_I; anchors prune P_O independently;
    and combined survivor filtering scales beyond 17,280+ models with complete survivor semantics.
    """

    def __init__(self, machine: Machine, contract: Contract, temporal: bool = False):
        if not isinstance(machine, Machine) or not isinstance(contract, Contract):
            raise TypeError('FactoredCandidateSpace requires a Machine and Contract')
        if max(contract.goal, contract.hazard) >= machine.outputs:
            raise ValueError('contract symbols exceed source alphabet')
        self.machine, self.contract = machine, contract
        self.temporal = bool(temporal)

        self.input_perms = tuple(permutations(range(machine.inputs)))
        self.output_perms = tuple(permutations(range(machine.outputs)))
        self.num_input_perms = len(self.input_perms)
        self.num_output_perms = len(self.output_perms)
        self.static_count = self.num_input_perms * self.num_output_perms

        if self.temporal:
            self.temporal_count = self.static_count * machine.outputs
            self.total_adapters = self.static_count + self.temporal_count
        else:
            self.temporal_count = 0
            self.total_adapters = self.static_count

        self.work = {'source_steps': 0, 'candidate_expansions': 0, 'pair_checks': 0}
        self._source = {(): (machine.initial, ())}
        self._input_traces = {}
        self._safe_input_factors = {}
        self._adapter_cache = {}
        self._deployment = words(machine.inputs, contract.horizon)
        self._probes = words(machine.inputs, 3)
        self._adapters_proxy = _LazyAdapters(self)

    @property
    def adapters(self):
        return self._adapters_proxy

    def decompose_id(self, identifier: int) -> tuple[int, int, int, int]:
        """Convert linear adapter id into (input_perm_idx, output_perm_idx, delay, init_output)."""
        _integer(identifier, 'adapter id', maximum=self.total_adapters - 1)
        if identifier < self.static_count:
            i_idx = identifier // self.num_output_perms
            o_idx = identifier % self.num_output_perms
            return i_idx, o_idx, 0, 0
        else:
            rem = identifier - self.static_count
            init_output = rem % self.machine.outputs
            pair_idx = rem // self.machine.outputs
            i_idx = pair_idx // self.num_output_perms
            o_idx = pair_idx % self.num_output_perms
            return i_idx, o_idx, 1, init_output

    def compose_id(self, i_idx: int, o_idx: int, delay: int = 0, init_output: int = 0) -> int:
        """Compose (input_perm_idx, output_perm_idx, delay, init_output) into canonical linear id."""
        if delay == 0:
            return i_idx * self.num_output_perms + o_idx
        pair_idx = i_idx * self.num_output_perms + o_idx
        return self.static_count + pair_idx * self.machine.outputs + init_output

    def adapter(self, identifier: int) -> Adapter:
        if identifier not in self._adapter_cache:
            i_idx, o_idx, delay, init_output = self.decompose_id(identifier)
            self._adapter_cache[identifier] = Adapter(
                id=identifier,
                input_map=self.input_perms[i_idx],
                output_map=self.output_perms[o_idx],
                delay=delay,
                init_output=init_output
            )
        return self._adapter_cache[identifier]

    def _ids(self, ids):
        ids = tuple(ids)
        for identifier in ids:
            _integer(identifier, 'adapter id', maximum=self.total_adapters - 1)
        return tuple(sorted(set(ids)))

    def _source_trace(self, mapped):
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

    def _input_trace(self, i_idx: int, word: tuple[int, ...]) -> tuple[int, ...]:
        key = (i_idx, word)
        if key not in self._input_traces:
            input_map = self.input_perms[i_idx]
            mapped = tuple(input_map[x] for x in word)
            self._input_traces[key] = self._source_trace(mapped)
        return self._input_traces[key]

    def semantic(self, identifier: int, word: tuple[int, ...]) -> tuple[int, ...]:
        i_idx, _, _, _ = self.decompose_id(identifier)
        word = _word(word, self.machine.inputs)
        return self._input_trace(i_idx, word)

    def predict(self, identifier: int, word: tuple[int, ...]) -> tuple[int, ...]:
        i_idx, o_idx, delay, init_o = self.decompose_id(identifier)
        word = _word(word, self.machine.inputs)
        semantic = self._input_trace(i_idx, word)
        out_map = self.output_perms[o_idx]
        self.work['candidate_expansions'] += 1
        if delay == 0:
            return tuple(out_map[s] for s in semantic)
        preds = []
        for t in range(len(semantic)):
            if t == 0:
                preds.append(out_map[init_o])
            else:
                preds.append(out_map[semantic[t - 1]])
        return tuple(preds)

    def safe_words(self, identifier: int) -> frozenset:
        i_idx, _, _, _ = self.decompose_id(identifier)
        if i_idx not in self._safe_input_factors:
            self._safe_input_factors[i_idx] = frozenset(
                w for w in self._deployment if self.contract.accepts(self._input_trace(i_idx, w))
            )
        return self._safe_input_factors[i_idx]

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

    def survivors(self, transcripts, anchors=None) -> tuple[int, ...]:
        evidence, anchors = self._evidence(transcripts, anchors)

        valid_o_indices = []
        for o_idx, o_perm in enumerate(self.output_perms):
            if all(o_perm[sem] == raw for raw, sem in anchors.items()):
                valid_o_indices.append(o_idx)

        if not valid_o_indices:
            return ()

        surviving_ids = []

        # Check static adapters
        for i_idx in range(self.num_input_perms):
            sem_traces = [self._input_trace(i_idx, word) for word, _ in evidence]
            for o_idx in valid_o_indices:
                o_perm = self.output_perms[o_idx]
                match = True
                for sem, (_, outputs) in zip(sem_traces, evidence):
                    if any(o_perm[s] != out for s, out in zip(sem, outputs)):
                        match = False
                        break
                if match:
                    surviving_ids.append(self.compose_id(i_idx, o_idx, delay=0))

        # Check temporal adapters if enabled
        if self.temporal:
            for i_idx in range(self.num_input_perms):
                sem_traces = [self._input_trace(i_idx, word) for word, _ in evidence]
                for o_idx in valid_o_indices:
                    o_perm = self.output_perms[o_idx]
                    for init_o in range(self.machine.outputs):
                        match = True
                        for sem, (_, outputs) in zip(sem_traces, evidence):
                            for t, out in enumerate(outputs):
                                pred_s = init_o if t == 0 else sem[t - 1]
                                if o_perm[pred_s] != out:
                                    match = False
                                    break
                            if not match:
                                break
                        if match:
                            surviving_ids.append(self.compose_id(i_idx, o_idx, delay=1, init_output=init_o))

        return tuple(sorted(surviving_ids))

    def ambiguity(self, survivors):
        survivors = self._ids(survivors)
        if not survivors:
            return {'candidate_count': 0, 'entropy': 0.0, 'complete': False}
        entropy = math.log2(len(survivors)) if survivors else 0.0
        return {'candidate_count': len(survivors), 'entropy': entropy, 'complete': len(survivors) == 1}

    def plan(self, survivors, admission='robust', transcripts=None, anchors=None, risk_tolerance=0.0):
        survivors = self._ids(survivors)
        if not survivors:
            return {'status': 'FAMILY_CONTRADICTED', 'admitted': False, 'word': None, 'candidate_count': 0}
        if admission == 'robust':
            common = None
            for s in survivors:
                sw = self.safe_words(s)
                if common is None:
                    common = set(sw)
                else:
                    common &= sw
                if not common:
                    break
            chosen = min(common, key=lambda w: (len(w), w)) if common else None
            status = ('IDENTIFIED' if len(survivors) == 1 else 'TASK_ADMISSIBLE') if chosen is not None else (
                'FAMILY_CONTRADICTED' if not survivors else 'UNRESOLVED'
            )
            return {'status': status, 'admitted': chosen is not None, 'word': list(chosen) if chosen is not None else None,
                    'candidate_count': len(survivors)}
        raise ValueError(f'Unsupported admission {admission}')

    def factor_summary(self, survivors=None) -> dict:
        """Report factored structure, memory footprint, and active factor counts."""
        if survivors is None:
            survivors = tuple(range(self.total_adapters))
        else:
            survivors = self._ids(survivors)
        active_i = set()
        active_o = set()
        active_delay = set()
        for sid in survivors:
            i_idx, o_idx, delay, _ = self.decompose_id(sid)
            active_i.add(i_idx)
            active_o.add(o_idx)
            active_delay.add(delay)
        return {
            'total_models': self.total_adapters,
            'static_models': self.static_count,
            'temporal_models': self.temporal_count,
            'input_alphabet': self.machine.inputs,
            'output_alphabet': self.machine.outputs,
            'input_permutations': self.num_input_perms,
            'output_permutations': self.num_output_perms,
            'survivors_count': len(survivors),
            'active_input_factors': len(active_i),
            'active_output_factors': len(active_o),
            'active_delay_modes': sorted(active_delay),
            'compression_ratio': round(self.total_adapters / max(1, (self.num_input_perms + self.num_output_perms)), 2),
        }
