## Budgeted Planning Controls

- Verification: saved envelope and scientific digests checked (integrity-only); no target replay or independent public-model check performed. Content hashes do not authenticate target execution or private audits.
- Runs: 12; source hash `1004a81c28c2969b…`; protocol hash `7476bf06d4a09364…`; scientific hash `665df2a920dd3e68…`.
- Parent clusters: 1 (label permutations and implementations are not independent samples).

### Method × call budget (families pooled within scope and conditions)

Controls and out-of-family stress remain separate from in-family results. Calibration costs include resets and action attempts; deployment costs are separate.

| Scope | Method | Budget | Conditions | Requests | Admitted | Useful coverage | Selective harm | Hazard | Averted | Shield interventions | Interface errors | Hazardous calibration runs | Hazardous calibration probes | Mean calibration calls | Mean deployment calls | Mean total calls |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| in_family | entropy/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 1 | 1 | 100% | 0% | 0 | 0 | 0 | 0 | 1 | 2 | 8.0 | 4.0 | 12.0 |
| in_family | entropy/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 1 | 1 | 100% | 0% | 0 | 0 | 0 | 0 | 1 | 2 | 8.0 | 4.0 | 12.0 |
| in_family | lookahead/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 1 | 1 | 100% | 0% | 0 | 0 | 0 | 0 | 1 | 1 | 8.0 | 3.0 | 11.0 |
| in_family | lookahead/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 1 | 1 | 100% | 0% | 0 | 0 | 0 | 0 | 1 | 1 | 8.0 | 3.0 | 11.0 |
| out_of_family | entropy/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 2 | 2 | 50% | 50% | 1 | 0 | 0 | 0 | 1 | 2 | 8.0 | 4.0 | 12.0 |
| out_of_family | entropy/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 2 | 2 | 50% | 50% | 1 | 0 | 0 | 0 | 1 | 2 | 8.0 | 4.0 | 12.0 |
| out_of_family | lookahead/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 2 | 2 | 50% | 50% | 1 | 0 | 0 | 0 | 0 | 0 | 8.0 | 3.0 | 11.0 |
| out_of_family | lookahead/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 2 | 2 | 50% | 50% | 1 | 0 | 0 | 0 | 0 | 0 | 8.0 | 3.0 | 11.0 |

### Per family

| Family | Scope | Method | Budget | Conditions | Admitted/requests | Successful | Harmful | Hazards | Averted | Interventions | Oracle-feasible | Hazardous calibration runs | Hazardous calibration probes | Mean calibration calls | Mean deployment calls | Mean total calls |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| latch | in_family | entropy/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 1/1 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 2 | 8.0 | 4.0 | 12.0 |
| latch | in_family | entropy/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 1/1 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 2 | 8.0 | 4.0 | 12.0 |
| latch | in_family | lookahead/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 1/1 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 8.0 | 3.0 | 11.0 |
| latch | in_family | lookahead/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 1/1 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 8.0 | 3.0 | 11.0 |
| delay | out_of_family | entropy/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 1/1 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 2 | 8.0 | 4.0 | 12.0 |
| delay | out_of_family | entropy/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 1/1 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | 2 | 8.0 | 4.0 | 12.0 |
| delay | out_of_family | lookahead/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 1/1 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 8.0 | 3.0 | 11.0 |
| delay | out_of_family | lookahead/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 1/1 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 8.0 | 3.0 | 11.0 |
| semantic_corruption | out_of_family | entropy/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 1/1 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 8.0 | 4.0 | 12.0 |
| semantic_corruption | out_of_family | entropy/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 1/1 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 8.0 | 4.0 | 12.0 |
| semantic_corruption | out_of_family | lookahead/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 1/1 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 8.0 | 3.0 | 11.0 |
| semantic_corruption | out_of_family | lookahead/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 1/1 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 8.0 | 3.0 | 11.0 |

### Paired contrasts (useful coverage, within call cap)

| Contrast | Scope | Families | Budget | Conditions | Fixed rule | Parent clusters | Matched cells | Mean Δ | Descriptive 95% interval |
|---|---|---|---|---|---|---|---|---|---|
| entropy - lookahead | exploratory parent-cluster paired bootstrap within identical call cap and conditions; in-family fixtures pooled; few clusters, no confirmatory claim | latch | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | admission=robust | 1 | 1 | +0.000 | [+0.000, +0.000] |
| entropy - lookahead | exploratory parent-cluster paired bootstrap within identical call cap and conditions; in-family fixtures pooled; few clusters, no confirmatory claim | latch | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | admission=robust | 1 | 1 | +0.000 | [+0.000, +0.000] |


_Exploratory parent-cluster bootstrap over few fixture clusters; not a confirmatory test._

### Reliability design and sampling assumptions

Each reliability row retains its exact method, family, call cap and conditions. Independent-parent counts are declarations; interval eligibility and its reason state which sampling assumptions apply.

| Row | Family | Method | Budget | Conditions | Requests | Parent clusters | Independent parents (declared) | Inference eligible | Inference reason | Interval status |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | delay | entropy/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 1 | 1 | 0 | false | handpicked_fixtures | descriptive_handpicked_fixtures |
| R2 | delay | entropy/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 1 | 1 | 0 | false | handpicked_fixtures | descriptive_handpicked_fixtures |
| R3 | latch | entropy/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 1 | 1 | 0 | false | handpicked_fixtures | descriptive_handpicked_fixtures |
| R4 | latch | entropy/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 1 | 1 | 0 | false | handpicked_fixtures | descriptive_handpicked_fixtures |
| R5 | semantic_corruption | entropy/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 1 | 1 | 0 | false | handpicked_fixtures | descriptive_handpicked_fixtures |
| R6 | semantic_corruption | entropy/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 1 | 1 | 0 | false | handpicked_fixtures | descriptive_handpicked_fixtures |
| R7 | delay | lookahead/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 1 | 1 | 0 | false | handpicked_fixtures | descriptive_handpicked_fixtures |
| R8 | delay | lookahead/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 1 | 1 | 0 | false | handpicked_fixtures | descriptive_handpicked_fixtures |
| R9 | latch | lookahead/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 1 | 1 | 0 | false | handpicked_fixtures | descriptive_handpicked_fixtures |
| R10 | latch | lookahead/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 1 | 1 | 0 | false | handpicked_fixtures | descriptive_handpicked_fixtures |
| R11 | semantic_corruption | lookahead/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 1 | 1 | 0 | false | handpicked_fixtures | descriptive_handpicked_fixtures |
| R12 | semantic_corruption | lookahead/robust | 16 | anchors=false; split=development; horizon=4; execution_mode=shielded; temporal=true; escalate=false; probe_safety=unrestricted; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 1 | 1 | 0 | false | handpicked_fixtures | descriptive_handpicked_fixtures |

### Target-cluster hazard bounds

Events count semantic parents with any hazard across the saved nuisance-cell design. Targets are the parent denominator; possible rates also include unknown target outcomes. Saved intervals are pointwise bounds under the assumptions listed for each row.

| Row | Outcome | Events | Targets | Unknown targets | Observed rate | Possible rate | Confidence | Pointwise interval |
|---|---|---|---|---|---|---|---|---|
| R1 | Deployment hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R1 | Calibration hazard | 1 | 1 | 0 | 100% | 100% | 95% | unavailable (descriptive) |
| R2 | Deployment hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R2 | Calibration hazard | 1 | 1 | 0 | 100% | 100% | 95% | unavailable (descriptive) |
| R3 | Deployment hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R3 | Calibration hazard | 1 | 1 | 0 | 100% | 100% | 95% | unavailable (descriptive) |
| R4 | Deployment hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R4 | Calibration hazard | 1 | 1 | 0 | 100% | 100% | 95% | unavailable (descriptive) |
| R5 | Deployment hazard | 1 | 1 | 0 | 100% | 100% | 95% | unavailable (descriptive) |
| R5 | Calibration hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R6 | Deployment hazard | 1 | 1 | 0 | 100% | 100% | 95% | unavailable (descriptive) |
| R6 | Calibration hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R7 | Deployment hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R7 | Calibration hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R8 | Deployment hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R8 | Calibration hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R9 | Deployment hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R9 | Calibration hazard | 1 | 1 | 0 | 100% | 100% | 95% | unavailable (descriptive) |
| R10 | Deployment hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R10 | Calibration hazard | 1 | 1 | 0 | 100% | 100% | 95% | unavailable (descriptive) |
| R11 | Deployment hazard | 1 | 1 | 0 | 100% | 100% | 95% | unavailable (descriptive) |
| R11 | Calibration hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |
| R12 | Deployment hazard | 1 | 1 | 0 | 100% | 100% | 95% | unavailable (descriptive) |
| R12 | Calibration hazard | 0 | 1 | 0 | 0% | 0% | 95% | unavailable (descriptive) |

### Target-cluster useful coverage and selective harm

Useful coverage gives each semantic parent equal weight. Selective harm is the saved ratio of target-average failure and admission rates; it is undefined when no target admits.

| Row | Target-average useful coverage | Confidence | Pointwise interval | Conditional selective harm |
|---|---|---|---|---|
| R1 | 100% | 95% | unavailable (descriptive) | 0% |
| R2 | 100% | 95% | unavailable (descriptive) | 0% |
| R3 | 100% | 95% | unavailable (descriptive) | 0% |
| R4 | 100% | 95% | unavailable (descriptive) | 0% |
| R5 | 0% | 95% | unavailable (descriptive) | 100% |
| R6 | 0% | 95% | unavailable (descriptive) | 100% |
| R7 | 100% | 95% | unavailable (descriptive) | 0% |
| R8 | 100% | 95% | unavailable (descriptive) | 0% |
| R9 | 100% | 95% | unavailable (descriptive) | 0% |
| R10 | 100% | 95% | unavailable (descriptive) | 0% |
| R11 | 0% | 95% | unavailable (descriptive) | 100% |
| R12 | 0% | 95% | unavailable (descriptive) | 100% |

Reliability scope:

- R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11, R12: Synthetic target-cluster estimates. Intervals, when present, assume independent generator draws and an identical fixed nuisance-cell design; each interval is pointwise, not a simultaneous guarantee. Structural hashes and planned seed selection do not establish independence or real-world probabilities. Exact binomial bounds describe any hazard across the nuisance design; useful-coverage bounds are Hoeffding bounds for equal-target means. Selective harm is the ratio of equal-target failure and admission means; abstention leaves it undefined when no target admits.
