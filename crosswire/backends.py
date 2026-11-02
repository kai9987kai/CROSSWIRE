"""Candidate construction and actual backend storage/structure telemetry."""
from math import factorial

from .core import CandidateSpace, FactoredCandidateSpace


CANDIDATE_BACKENDS = ('flat', 'factored')


def make_space(machine, contract, backend='flat', temporal=False):
    if backend not in CANDIDATE_BACKENDS:
        raise ValueError('Unknown candidate backend')
    space_type = FactoredCandidateSpace if backend == 'factored' else CandidateSpace
    return space_type(machine, contract, temporal=temporal)


def backend_summary(space, ids):
    """Inspect actual storage without enumerating or materializing lazy adapters."""
    if not isinstance(space, CandidateSpace):
        raise TypeError('backend_summary requires a candidate space')
    ids = space._ids(ids)
    factored = isinstance(space, FactoredCandidateSpace)
    if factored:
        factors = [space.decompose_id(i) for i in ids]
        active_inputs = {factor[0] for factor in factors}
        active_outputs = {factor[1] for factor in factors}
        cached_adapters = len(space._adapter_cache)
    else:
        active_inputs = {space.adapters[i].input_map for i in ids}
        active_outputs = {space.adapters[i].output_map for i in ids}
        cached_adapters = len(space.adapters)
    input_factors, output_factors = factorial(space.machine.inputs), factorial(space.machine.outputs)
    total = len(space.adapters)
    return {
        'backend': 'factored' if factored else 'flat',
        'total_candidates': total, 'active_candidates': len(ids),
        'total_input_factors': input_factors, 'total_output_factors': output_factors,
        'active_input_factors': len(active_inputs), 'active_output_factors': len(active_outputs),
        'cached_adapters': cached_adapters, 'cached_predictions': len(space._predictions),
        'structural_ratio': round(total / (input_factors + output_factors), 2),
        'structural_ratio_scope': ('Candidate count / (input factors + output factors); '
                                   'not measured memory compression.'),
    }
