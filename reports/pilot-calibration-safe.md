## Study results

- Runs: 8; source hash `c39578255ca558de…`; protocol hash `25e80327cf35821a…`; scientific hash `6cd97b3fc725d461…`.
- Parent clusters: 3 (label permutations and implementations are not independent samples).

### Method × call budget (families pooled within scope and conditions)

Controls and out-of-family stress remain separate from in-family results. Calibration costs include resets and action attempts; deployment costs are separate.

| Scope | Method | Budget | Conditions | Requests | Admitted | Useful coverage | Selective harm | Hazard | Averted | Shield interventions | Interface errors | Hazardous calibration runs | Hazardous calibration probes | Mean calibration calls | Mean deployment calls | Mean total calls |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| in_family | entropy/robust | 8 | probe_safety=model_safe; risk_tolerance=0; execution_mode=shielded; anchors=false; split=evaluation; horizon=4; temporal=false; escalate=false | 6 | 4 | 67% | 0% | 0 | 0 | 0 | 0 | 0 | 0 | 1.7 | 3.0 | 4.7 |
| out_of_family | entropy/robust | 8 | probe_safety=model_safe; risk_tolerance=0; execution_mode=shielded; anchors=false; split=evaluation; horizon=4; temporal=false; escalate=false | 2 | 0 | 0% | n/a | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | 0.0 |

### Per family

| Family | Scope | Method | Budget | Conditions | Admitted/requests | Successful | Harmful | Hazards | Averted | Interventions | Oracle-feasible | Hazardous calibration runs | Hazardous calibration probes | Mean calibration calls | Mean deployment calls | Mean total calls |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| latch | in_family | entropy/robust | 8 | probe_safety=model_safe; risk_tolerance=0; execution_mode=shielded; anchors=false; split=evaluation; horizon=4; temporal=false; escalate=false | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0.0 | 0.0 | 0.0 |
| neutral | in_family | entropy/robust | 8 | probe_safety=model_safe; risk_tolerance=0; execution_mode=shielded; anchors=false; split=evaluation; horizon=4; temporal=false; escalate=false | 2/2 | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0.0 | 4.0 | 4.0 |
| routing | in_family | entropy/robust | 8 | probe_safety=model_safe; risk_tolerance=0; execution_mode=shielded; anchors=false; split=evaluation; horizon=4; temporal=false; escalate=false | 2/2 | 2 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 5.0 | 5.0 | 10.0 |
| semantic_corruption | out_of_family | entropy/robust | 8 | probe_safety=model_safe; risk_tolerance=0; execution_mode=shielded; anchors=false; split=evaluation; horizon=4; temporal=false; escalate=false | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0.0 | 0.0 | 0.0 |

### Reliability design and sampling assumptions

Each reliability row retains its exact method, family, call cap and conditions. Independent-parent counts are declarations; interval eligibility and its reason state which sampling assumptions apply.

| Row | Family | Method | Budget | Conditions | Requests | Parent clusters | Independent parents (declared) | Inference eligible | Inference reason | Interval status |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | latch | entropy/robust | 8 | probe_safety=model_safe; risk_tolerance=0; execution_mode=shielded; anchors=false; split=evaluation; horizon=4; temporal=false; escalate=false | 2 | 1 | 0 | false | handpicked_fixtures | descriptive_handpicked_fixtures |
| R2 | neutral | entropy/robust | 8 | probe_safety=model_safe; risk_tolerance=0; execution_mode=shielded; anchors=false; split=evaluation; horizon=4; temporal=false; escalate=false | 2 | 1 | 0 | false | handpicked_fixtures | descriptive_handpicked_fixtures |
| R3 | routing | entropy/robust | 8 | probe_safety=model_safe; risk_tolerance=0; execution_mode=shielded; anchors=false; split=evaluation; horizon=4; temporal=false; escalate=false | 2 | 1 | 0 | false | handpicked_fixtures | descriptive_handpicked_fixtures |
| R4 | semantic_corruption | entropy/robust | 8 | probe_safety=model_safe; risk_tolerance=0; execution_mode=shielded; anchors=false; split=evaluation; horizon=4; temporal=false; escalate=false | 2 | 1 | 0 | false | handpicked_fixtures | descriptive_handpicked_fixtures |

### Target-cluster hazard bounds

Events count semantic parents with any hazard across the saved nuisance-cell design. Targets are the parent denominator; possible rates also include unknown target outcomes. Saved intervals are pointwise bounds under the assumptions listed for each row.

| Row | Outcome | Events | Targets | Unknown targets | Observed rate | Possible rate | Confidence | Pointwise interval |
|---|---|---|---|---|---|---|---|---|
| R1 | Deployment hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R1 | Calibration hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R2 | Deployment hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R2 | Calibration hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R3 | Deployment hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R3 | Calibration hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R4 | Deployment hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R4 | Calibration hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |

### Target-cluster useful coverage and selective harm

Useful coverage gives each semantic parent equal weight. Selective harm is the saved ratio of target-average failure and admission rates; it is undefined when no target admits.

| Row | Target-average useful coverage | Confidence | Pointwise interval | Conditional selective harm |
|---|---|---|---|---|
| R1 | 0% | 95% | unavailable (descriptive) | n/a |
| R2 | 100% | 95% | unavailable (descriptive) | 0% |
| R3 | 100% | 95% | unavailable (descriptive) | 0% |
| R4 | 0% | 95% | unavailable (descriptive) | n/a |

Reliability scope:

- R1, R2, R3, R4: Synthetic target-cluster estimates. Intervals, when present, assume independent generator draws and an identical fixed nuisance-cell design; each interval is pointwise, not a simultaneous guarantee. Structural hashes and planned seed selection do not establish independence or real-world probabilities. Exact binomial bounds describe any hazard across the nuisance design; useful-coverage bounds are Hoeffding bounds for equal-target means. Selective harm is the ratio of equal-target failure and admission means; abstention leaves it undefined when no target admits.

