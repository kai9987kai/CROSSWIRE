"""Budgeted classical model learning with the same opaque target interface."""
from __future__ import annotations

from importlib.metadata import version
import random

from .core import Machine, Contract, CandidateSpace, compare_adapter
from .interfaces import InterfaceError


class _BudgetExhausted(RuntimeError):
    pass


def acquire_aalpy(public: dict, budget: int, target, cancel=None):
    from aalpy.base import SUL, Oracle
    from aalpy.learning_algs import run_Lstar
    from .study import Cancelled, fit_evidence

    space = CandidateSpace(Machine.from_dict(public['reference']), Contract.from_dict(public['contract']))
    anchors = {int(k): int(v) for k, v in public.get('anchors', {}).items()}
    probes, error = [], None
    detail = {'library': 'aalpy', 'version': version('aalpy'), 'model_complete': False,
              'oracle': 'budgeted local-RNG random words, no exact target equivalence',
              'model_product_pairs': 0, 'equivalence_probe_steps': 0,
              'comparison_source_steps': 0, 'comparison_hypothesis_steps': 0,
              'budget_unit': 'target calls (resets + actions)',
              'completion': 'budget_exhausted'}

    class BoundarySUL(SUL):
        def __init__(self):
            super().__init__()
            self.word, self.outputs = [], []
            self.active = False

        def check(self):
            if cancel and cancel():
                raise Cancelled('Classical baseline cancelled')
            # Same shared system-call cap as other policies: resets and steps both count.
            if target.counts['target_calls'] >= budget:
                raise _BudgetExhausted()

        def pre(self):
            self.post()
            self.check()
            target.reset()
            self.word, self.outputs, self.active = [], [], True

        def post(self):
            if self.active:
                probes.append({'word': list(self.word), 'outputs': list(self.outputs),
                               'complete': len(self.word) == len(self.outputs),
                               'survivors_before': None, 'survivors_after': None})
                self.active = False

        def step(self, letter):
            if letter is None:
                return None
            self.check()
            self.word.append(letter)
            output = target.step(letter)
            self.outputs.append(output)
            return output

    sul = BoundarySUL()

    class BudgetOracle(Oracle):
        def __init__(self):
            super().__init__(list(range(space.machine.inputs)), sul)
            self.rng = random.Random(432871)

        def find_cex(self, hypothesis):
            for _ in range(16):
                remaining = budget - target.counts['target_calls'] - 1  # reserve this query's reset
                if remaining <= 0:
                    break
                word = tuple(self.rng.choice(self.alphabet) for _ in range(self.rng.randint(1, min(3, remaining))))
                hypothesis.reset_to_initial()
                sul.pre()
                mismatched = False
                for symbol in word:
                    actual = sul.step(symbol)
                    expected = hypothesis.step(symbol)
                    detail['equivalence_probe_steps'] += 1
                    if actual != expected:
                        mismatched = True
                        break
                sul.post()
                if mismatched:
                    return list(sul.word)
            return None

    learned = None
    try:
        learned = run_Lstar(list(range(space.machine.inputs)), sul, BudgetOracle(), 'mealy',
                            cache_and_non_det_check=False, print_level=0)
        detail['model_complete'] = True
        detail['completion'] = 'empirical_complete_approximate_oracle'
    except _BudgetExhausted:
        pass
    except InterfaceError as exc:
        error = {'code': exc.code, 'message': str(exc)}
        detail['completion'] = 'interface_error'
    finally:
        sul.post()

    evidence = fit_evidence(probes)
    observed_survivors = space.survivors(evidence, anchors)
    survivors = ()
    if learned is not None:
        states = list(learned.states)
        indices = {id(state): i for i, state in enumerate(states)}
        transitions = tuple(tuple((indices[id(state.transitions[symbol])], state.output_fun[symbol])
                                  for symbol in range(space.machine.inputs)) for state in states)
        raw_model = Machine('aalpy empirical hypothesis', transitions, space.machine.inputs,
                            space.machine.outputs, indices[id(learned.initial_state)])
        matches = []
        for adapter_id in observed_survivors:
            result = compare_adapter(space.machine, space.adapters[adapter_id], raw_model)
            detail['model_product_pairs'] += result['visited_pairs']
            # Product comparison runs outside CandidateSpace; charge it separately.
            detail['comparison_source_steps'] += result['source_steps']
            detail['comparison_hypothesis_steps'] += result['target_model_steps']
            if result['equivalent']:
                matches.append(adapter_id)
        survivors = tuple(matches)
        detail['model_states'] = len(states)
    # Preserve raw transcript and cumulative costs even if learning is incomplete.
    prefix = []
    for entry in probes:
        before = len(space.survivors(fit_evidence(prefix), anchors))
        prefix.append(entry)
        entry['survivors_before'] = before
        entry['survivors_after'] = len(space.survivors(fit_evidence(prefix), anchors))
    detail['observed_survivors'] = len(observed_survivors)
    return space, survivors, probes, error, detail
