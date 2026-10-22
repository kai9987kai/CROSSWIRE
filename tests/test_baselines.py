from crosswire.study import RunConfig, run


def test_classical_learner_cannot_spend_past_cap_to_finish_model():
    result = run(RunConfig(family='latch', policy='aalpy', budget=4))
    assert result['metrics']['target_steps'] <= 4
    assert result['metrics']['target_calls'] <= 4
    assert result['baseline']['library'] == 'aalpy'
    assert result['baseline']['version'] == '1.6.2'
    if not result['baseline']['model_complete']:
        assert result['decision']['admitted'] is False


def test_classical_baseline_is_reproducible_without_global_rng_changes():
    import random
    random.seed(813)
    before = random.getstate()
    a = run(RunConfig(family='latch', policy='aalpy', budget=32))
    b = run(RunConfig(family='latch', policy='aalpy', budget=32))
    assert a['scientific_hash'] == b['scientific_hash']
    assert random.getstate() == before


def test_completed_classical_model_reports_comparison_transition_work():
    result = run(RunConfig(family='latch', policy='aalpy', budget=256))
    detail = result['baseline']
    assert result['metrics']['target_calls'] <= 256
    if detail['model_complete'] and detail['model_product_pairs']:
        assert detail['comparison_source_steps'] > 0
        assert detail['comparison_hypothesis_steps'] > 0
