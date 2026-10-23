from copy import deepcopy
from dataclasses import asdict
import json

import pytest

from crosswire import cli
from crosswire.identity import canonical_hash, scientific_view
from crosswire.receipts import pack, replay
from crosswire.study import RunConfig, paired_comparisons, run, run_study, study_configs


def test_structural_instances_are_an_explicit_configuration_dimension():
    cfg = RunConfig.from_dict({'family': 'generated_protocol', 'instance_seed': 12, 'seed': 17})
    assert cfg.instance_seed == 12 and cfg.seed == 17
    assert RunConfig(family='generated_protocol').instance_seed == 0
    for value in (True, -1, 2**32, 1.2, '3'):
        with pytest.raises(ValueError):
            RunConfig.from_dict({'family': 'generated_protocol', 'instance_seed': value})
    with pytest.raises(ValueError, match='instance_seed'):
        RunConfig.from_dict({'family': 'latch', 'instance_seed': 1})


def test_structural_study_grid_is_bounded_and_rejects_duplicate_effective_instances():
    spec = {'families': ['generated_protocol'], 'instance_seeds': [2, 3], 'seeds': [17, 42],
            'budgets': [8], 'policies': ['fixed', 'entropy'], 'admissions': ['robust']}
    cfgs = study_configs(spec)
    assert len(cfgs) == 8
    assert {c.instance_seed for c in cfgs} == {2, 3}
    with pytest.raises(ValueError, match='Duplicate'):
        study_configs({**spec, 'instance_seeds': [None, 0]})
    with pytest.raises(ValueError, match='512'):
        study_configs({**spec, 'instance_seeds': list(range(64)), 'seeds': list(range(9))})


def test_generated_instances_receive_distinct_parent_identity_but_share_nuisance_parent():
    from crosswire.fixtures import make_case
    first = make_case('generated_protocol', 17, instance_seed=1)
    nuisance = make_case('generated_protocol', 42, 'table', instance_seed=1)
    assert first.public['parent_instance_id'] == nuisance.public['parent_instance_id']
    assert first.public['target_id'] != nuisance.public['target_id']
    result = run(RunConfig(family='generated_protocol', instance_seed=1, budget=0, horizon=4))
    assert result['instance_design'] == first.public['instance_design']
    assert result['evidence_certificate']['model_diagnostics']['inclusion_status'] == 'UNKNOWN'
    assert replay(pack(result))['valid'] is True


def test_instance_seed_is_part_of_the_exact_matched_cell():
    # Distinct structural draws may deduplicate to one semantic parent; matching
    # a policy at one draw with another draw's nuisance outcome is still invalid.
    def row(policy, instance):
        cfg = asdict(RunConfig(family='generated_protocol', policy=policy, instance_seed=instance))
        return {'configuration': cfg, 'parent_instance_id': 'shared-dynamics',
                'audit': {'contract_satisfied': True}}
    assert paired_comparisons([row('task', 1), row('fixed', 2)]) == []
    compared = paired_comparisons([row('task', 1), row('fixed', 1), row('task', 2), row('fixed', 2)])
    assert len(compared) == 1
    assert compared[0]['parent_clusters'] == 1 and compared[0]['matched_cells'] == 2


def test_study_includes_reliability_and_replays_all_independent_evidence():
    spec = {'families': ['generated_protocol'], 'instance_seeds': [1, 2], 'seeds': [17],
            'budgets': [0], 'policies': ['entropy'], 'admissions': ['robust'],
            'probe_safety': 'model_safe'}
    result = run_study(spec)
    assert len(result['rows']) == 2
    assert result['reliability']
    assert result['reliability'][0]['independent_parents'] == 2
    assert replay(pack(result))['valid'] is True
    forged = deepcopy(pack(result))
    forged['payload']['reliability'][0]['independent_parents'] = 2000
    forged['payload']['scientific_hash'] = canonical_hash(scientific_view(forged['payload']))
    forged['payload_hash'] = canonical_hash(forged['payload'])
    assert replay(forged)['valid'] is False


def test_cli_accepts_structural_seed_and_passes_it_to_the_runtime(tmp_path, monkeypatch, capsys):
    # Stub only the expensive scientific execution; actual CLI argument plumbing
    # is exercised and the run config is independently checked.
    seen = []
    def capture(cfg):
        cfg.check()
        seen.append(cfg)
        return {'decision': {}, 'audit': {'contract_satisfied': None}, 'scientific_hash': 'test'}
    monkeypatch.setattr(cli, 'run', capture)
    monkeypatch.setattr(cli, 'pack', lambda result: result)
    target = tmp_path / 'run.json'
    assert cli.main(['run', '--family', 'generated_protocol', '--instance-seed', '7', '--out', str(target)]) == 0
    assert seen[0].instance_seed == 7
    assert json.loads(capsys.readouterr().out)['scientific_hash'] == 'test'
