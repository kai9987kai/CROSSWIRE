"""Target-cluster reliability summaries with explicit sampling assumptions.

These intervals concern the declared synthetic generator and fixed nuisance
design. A seed, hash, or metadata field cannot establish independent sampling.
Exact binomial intervals follow the NIST Engineering Statistics Handbook,
section 7.2.4.1; bounded target averages use Hoeffding's inequality (1963).
"""
from collections import defaultdict
import math
from .conditions import condition_key, condition_fields


def _binomial_cdf(events, trials, probability):
    if probability <= 0:
        return 1.0
    if probability >= 1:
        return float(events >= trials)
    log_p, log_q = math.log(probability), math.log1p(-probability)
    # Log probabilities avoid overflow in the integer binomial coefficients
    # and underflow of the starting term for the bounded study sizes.
    return min(1.0, math.fsum(math.exp(math.lgamma(trials + 1) - math.lgamma(index + 1)
                                      - math.lgamma(trials - index + 1)
                                      + index * log_p + (trials - index) * log_q)
                              for index in range(events + 1)))


def _binomial_quantile(events, trials, tail):
    low, high = 0.0, 1.0
    for _ in range(70):
        middle = (low + high) / 2
        if _binomial_cdf(events, trials, middle) > tail:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def _exact_interval(events, trials, confidence):
    alpha = 1 - confidence
    lower = 0.0 if events == 0 else _binomial_quantile(events - 1, trials, 1 - alpha / 2)
    upper = 1.0 if events == trials else _binomial_quantile(events, trials, alpha / 2)
    return [lower, upper]


def _outcome(row):
    audit, admitted = row['audit'], bool(row['decision']['admitted'])
    hazard = audit.get('hazard') if admitted else False
    return (admitted, audit.get('contract_satisfied') is True,
            admitted and audit.get('contract_satisfied') is not True,
            hazard, audit.get('calibration_hazardous_probes', 0) > 0)


def _event_metric(events, targets, unknown, eligible, confidence):
    interval = None
    if eligible:
        # Missing deployment outcomes cannot count as negative observations.
        interval = [_exact_interval(events, targets, confidence)[0],
                    _exact_interval(events + unknown, targets, confidence)[1]]
    return {'events': events, 'targets': targets, 'unknown_targets': unknown,
            'rate': events / targets, 'possible_rate': (events + unknown) / targets, 'interval': interval}


def reliability_summary(rows, confidence=0.95):
    """Equal-weight semantic-parent summaries, conditional on explicit draws.

    Duplicate nuisance cells are collapsed only when their audit outcomes
    agree. Structural-seed collisions or unequal label/implementation designs
    withhold sampling intervals. Planned seed selection is not observational
    evidence of a real-world target distribution or independent draws.
    """
    if (type(confidence) not in (int, float) or not math.isfinite(confidence)
            or not 0 < confidence < 1):
        raise ValueError('confidence must be finite and strictly between zero and one')
    groups = defaultdict(list)
    for row in rows:
        cfg = row['configuration']
        conditions = condition_key(cfg)
        groups[(cfg['policy'] + '/' + cfg['admission'], cfg['family'], cfg['budget'], conditions)].append(row)
    output = []
    for (method, family, budget, conditions), members in sorted(groups.items()):
        parents, structural_seeds, seed_parents = defaultdict(dict), defaultdict(set), {}
        declared = True
        for row in members:
            cfg, parent = row['configuration'], row['parent_instance_id']
            seed = cfg.get('instance_seed')
            if type(seed) is int and 0 <= seed <= 2**32 - 1:
                if family == 'generated_protocol' and seed in seed_parents and seed_parents[seed] != parent:
                    raise ValueError('A structural seed identifies inconsistent semantic target dynamics')
                seed_parents[seed] = parent
                structural_seeds[parent].add(seed)
            else:
                declared = False
            cell = (cfg['seed'], cfg['implementation'])
            outcome = _outcome(row)
            if cell in parents[parent] and parents[parent][cell] != outcome:
                raise ValueError('Inconsistent duplicate nuisance-cell audit outcomes')
            parents[parent][cell] = outcome
        targets = len(parents)
        collisions = sum(max(0, len(seeds) - 1) for seeds in structural_seeds.values())
        nuisance_designs = {frozenset(cells) for cells in parents.values()}
        if family != 'generated_protocol':
            reason = 'handpicked_fixtures'
        elif not declared:
            reason = 'undeclared_structural_seed'
        elif collisions:
            reason = 'structural_seed_collision'
        elif len(nuisance_designs) != 1:
            reason = 'unequal_nuisance_design'
        else:
            reason = 'independent_generator_draws_assumed'
        eligible = reason == 'independent_generator_draws_assumed'
        useful, admitted, harmful = [], [], []
        deployment_events = calibration_events = unknown_deployment = 0
        for cells in parents.values():
            values = list(cells.values())
            useful.append(sum(value[1] for value in values) / len(values))
            admitted.append(sum(value[0] for value in values) / len(values))
            harmful.append(sum(value[2] for value in values) / len(values))
            any_hazard = any(value[3] is True for value in values)
            deployment_events += any_hazard
            unknown_deployment += not any_hazard and any(value[3] is None for value in values)
            calibration_events += any(value[4] for value in values)
        useful_mean = math.fsum(useful) / targets
        admitted_mean, harmful_mean = math.fsum(admitted) / targets, math.fsum(harmful) / targets
        useful_interval = None
        if eligible:
            radius = math.sqrt(math.log(2 / (1 - confidence)) / (2 * targets))
            useful_interval = [max(0.0, useful_mean - radius), min(1.0, useful_mean + radius)]
        output.append({
            'method': method, 'family': family, 'budget': budget,
            **condition_fields(conditions), 'confidence': confidence,
            'requests': len(members), 'unique_nuisance_requests': sum(len(cells) for cells in parents.values()),
            'parent_clusters': targets,
            'independent_parents': targets if family == 'generated_protocol' and declared else 0,
            'structural_seed_collisions': collisions, 'inference_eligible': eligible,
            'inference_reason': reason,
            'interval_status': 'conditional_generator_sampling' if eligible else 'descriptive_' + reason,
            'target_any_deployment_hazard': _event_metric(deployment_events, targets, unknown_deployment,
                                                        eligible, confidence),
            'target_any_calibration_hazard': _event_metric(calibration_events, targets, 0, eligible, confidence),
            'target_average_useful_coverage': {'estimate': useful_mean, 'interval': useful_interval},
            'conditional_selective_harm': harmful_mean / admitted_mean if admitted_mean else None,
            'scope': ('Synthetic target-cluster estimates. Intervals, when present, assume independent generator '
                      'draws and an identical fixed nuisance-cell design; each interval is pointwise, not a '
                      'simultaneous guarantee. Structural hashes and planned seed selection do not establish '
                      'independence or real-world probabilities. Exact binomial bounds describe any hazard '
                      'across the nuisance design; useful-coverage bounds are Hoeffding bounds for equal-target '
                      'means. Selective harm is the ratio of equal-target failure and admission means; '
                      'abstention leaves it undefined when no target admits.')})
    return output
