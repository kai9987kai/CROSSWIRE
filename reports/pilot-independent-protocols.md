## Independent synthetic protocol pilot

- Runs: 128; source hash `c39578255ca558de…`; protocol hash `9d66e5b7df0645b2…`; scientific hash `039cc5257f627ff4…`.
- Parent clusters: 32 (label permutations and implementations are not independent samples).

### Method × call budget (families pooled within scope and conditions)

Controls and out-of-family stress remain separate from in-family results. Calibration costs include resets and action attempts; deployment costs are separate.

| Scope | Method | Budget | Conditions | Requests | Admitted | Useful coverage | Selective harm | Hazard | Averted | Shield interventions | Interface errors | Hazardous calibration runs | Hazardous calibration probes | Mean calibration calls | Mean deployment calls | Mean total calls |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| in_family | entropy/robust | 16 | probe_safety=model_safe; risk_tolerance=0; execution_mode=shielded; anchors=false; split=evaluation; horizon=4; temporal=false; escalate=false | 64 | 52 | 81% | 0% | 0 | 0 | 0 | 0 | 0 | 0 | 7.7 | 3.6 | 11.4 |
| in_family | fixed/robust | 16 | probe_safety=model_safe; risk_tolerance=0; execution_mode=shielded; anchors=false; split=evaluation; horizon=4; temporal=false; escalate=false | 64 | 48 | 75% | 0% | 0 | 0 | 0 | 0 | 0 | 0 | 10.1 | 3.3 | 13.5 |

### Per family

| Family | Scope | Method | Budget | Conditions | Admitted/requests | Successful | Harmful | Hazards | Averted | Interventions | Oracle-feasible | Hazardous calibration runs | Hazardous calibration probes | Mean calibration calls | Mean deployment calls | Mean total calls |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| generated_protocol | in_family | entropy/robust | 16 | probe_safety=model_safe; risk_tolerance=0; execution_mode=shielded; anchors=false; split=evaluation; horizon=4; temporal=false; escalate=false | 52/64 | 52 | 0 | 0 | 0 | 0 | 64 | 0 | 0 | 7.7 | 3.6 | 11.4 |
| generated_protocol | in_family | fixed/robust | 16 | probe_safety=model_safe; risk_tolerance=0; execution_mode=shielded; anchors=false; split=evaluation; horizon=4; temporal=false; escalate=false | 48/64 | 48 | 0 | 0 | 0 | 0 | 64 | 0 | 0 | 10.1 | 3.3 | 13.5 |

### Paired contrasts (useful coverage, within call cap)

| Contrast | Scope | Families | Budget | Conditions | Fixed rule | Parent clusters | Matched cells | Mean Δ | Descriptive 95% interval |
|---|---|---|---|---|---|---|---|---|---|
| entropy - fixed | exploratory parent-cluster paired bootstrap within identical call cap and conditions; in-family fixtures pooled; few clusters, no confirmatory claim | generated_protocol | 16 | probe_safety=model_safe; risk_tolerance=0; execution_mode=shielded; anchors=false; split=evaluation; horizon=4; temporal=false; escalate=false | admission=robust | 32 | 64 | +0.062 | [+0.000, +0.156] |


_Exploratory parent-cluster bootstrap over few fixture clusters; not a confirmatory test._

### Reliability design and sampling assumptions

Each reliability row retains its exact method, family, call cap and conditions. Independent-parent counts are declarations; interval eligibility and its reason state which sampling assumptions apply.

| Row | Family | Method | Budget | Conditions | Requests | Parent clusters | Independent parents (declared) | Inference eligible | Inference reason | Interval status |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | generated_protocol | entropy/robust | 16 | probe_safety=model_safe; risk_tolerance=0; execution_mode=shielded; anchors=false; split=evaluation; horizon=4; temporal=false; escalate=false | 64 | 32 | 32 | true | independent_generator_draws_assumed | conditional_generator_sampling |
| R2 | generated_protocol | fixed/robust | 16 | probe_safety=model_safe; risk_tolerance=0; execution_mode=shielded; anchors=false; split=evaluation; horizon=4; temporal=false; escalate=false | 64 | 32 | 32 | true | independent_generator_draws_assumed | conditional_generator_sampling |

### Target-cluster hazard bounds

Events count semantic parents with any hazard across the saved nuisance-cell design. Targets are the parent denominator; possible rates also include unknown target outcomes. Saved intervals are pointwise bounds under the assumptions listed for each row.

| Row | Outcome | Events | Targets | Unknown targets | Observed rate | Possible rate | Confidence | Pointwise interval |
|---|---|---|---|---|---|---|---|---|
| R1 | Deployment hazard | 0 | 32 | 0 | 0% | 0% | 95% | [0%, 10.89%] |
| R1 | Calibration hazard | 0 | 32 | 0 | 0% | 0% | 95% | [0%, 10.89%] |
| R2 | Deployment hazard | 0 | 32 | 0 | 0% | 0% | 95% | [0%, 10.89%] |
| R2 | Calibration hazard | 0 | 32 | 0 | 0% | 0% | 95% | [0%, 10.89%] |

### Target-cluster useful coverage and selective harm

Useful coverage gives each semantic parent equal weight. Selective harm is the saved ratio of target-average failure and admission rates; it is undefined when no target admits.

| Row | Target-average useful coverage | Confidence | Pointwise interval | Conditional selective harm |
|---|---|---|---|---|
| R1 | 81.25% | 95% | [57.24%, 100%] | 0% |
| R2 | 75% | 95% | [50.99%, 99.01%] | 0% |

Reliability scope:

- R1, R2: Synthetic target-cluster estimates. Intervals, when present, assume independent generator draws and an identical fixed nuisance-cell design; each interval is pointwise, not a simultaneous guarantee. Structural hashes and planned seed selection do not establish independence or real-world probabilities. Exact binomial bounds describe any hazard across the nuisance design; useful-coverage bounds are Hoeffding bounds for equal-target means. Selective harm is the ratio of equal-target failure and admission means; abstention leaves it undefined when no target admits.

