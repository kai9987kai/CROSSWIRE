## Budgeted Planning Pilot

- Verification: saved envelope and scientific digests checked (integrity-only); no target replay or independent public-model check performed. Content hashes do not authenticate target execution or private audits.
- Runs: 24; source hash `1004a81c28c2969b…`; protocol hash `d529142f1cfcec39…`; scientific hash `5ad3444a94d76c0f…`.
- Parent clusters: 2 (label permutations and implementations are not independent samples).

### Method × call budget (families pooled within scope and conditions)

Controls and out-of-family stress remain separate from in-family results. Calibration costs include resets and action attempts; deployment costs are separate.

| Scope | Method | Budget | Conditions | Requests | Admitted | Useful coverage | Selective harm | Hazard | Averted | Shield interventions | Interface errors | Hazardous calibration runs | Hazardous calibration probes | Mean calibration calls | Mean deployment calls | Mean total calls |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| in_family | branching/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 2 | 0 | 0% | n/a | 0 | 0 | 0 | 0 | 0 | 0 | 3.0 | 0.0 | 3.0 |
| in_family | branching/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 2 | 0 | 0% | n/a | 0 | 0 | 0 | 0 | 0 | 0 | 3.0 | 0.0 | 3.0 |
| in_family | branching/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 2 | 1 | 50% | 0% | 0 | 0 | 0 | 0 | 0 | 0 | 7.0 | 2.5 | 9.5 |
| in_family | branching/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 2 | 1 | 50% | 0% | 0 | 0 | 0 | 0 | 0 | 0 | 7.0 | 2.5 | 9.5 |
| in_family | entropy/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 2 | 0 | 0% | n/a | 0 | 0 | 0 | 0 | 0 | 0 | 3.0 | 0.0 | 3.0 |
| in_family | entropy/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 2 | 0 | 0% | n/a | 0 | 0 | 0 | 0 | 0 | 0 | 3.0 | 0.0 | 3.0 |
| in_family | entropy/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 2 | 1 | 50% | 0% | 0 | 0 | 0 | 0 | 0 | 0 | 7.0 | 2.5 | 9.5 |
| in_family | entropy/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 2 | 1 | 50% | 0% | 0 | 0 | 0 | 0 | 0 | 0 | 7.0 | 2.5 | 9.5 |
| in_family | lookahead/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 2 | 0 | 0% | n/a | 0 | 0 | 0 | 0 | 0 | 0 | 3.5 | 0.0 | 3.5 |
| in_family | lookahead/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 2 | 0 | 0% | n/a | 0 | 0 | 0 | 0 | 0 | 0 | 3.5 | 0.0 | 3.5 |
| in_family | lookahead/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 2 | 1 | 50% | 0% | 0 | 0 | 0 | 0 | 0 | 0 | 6.0 | 2.5 | 8.5 |
| in_family | lookahead/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 2 | 1 | 50% | 0% | 0 | 0 | 0 | 0 | 0 | 0 | 6.0 | 2.5 | 8.5 |

### Per family

| Family | Scope | Method | Budget | Conditions | Admitted/requests | Successful | Harmful | Hazards | Averted | Interventions | Oracle-feasible | Hazardous calibration runs | Hazardous calibration probes | Mean calibration calls | Mean deployment calls | Mean total calls |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| generated_protocol | in_family | branching/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 3.0 | 0.0 | 3.0 |
| generated_protocol | in_family | branching/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 3.0 | 0.0 | 3.0 |
| generated_protocol | in_family | branching/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 1/2 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 7.0 | 2.5 | 9.5 |
| generated_protocol | in_family | branching/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 1/2 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 7.0 | 2.5 | 9.5 |
| generated_protocol | in_family | entropy/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 3.0 | 0.0 | 3.0 |
| generated_protocol | in_family | entropy/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 3.0 | 0.0 | 3.0 |
| generated_protocol | in_family | entropy/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 1/2 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 7.0 | 2.5 | 9.5 |
| generated_protocol | in_family | entropy/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 1/2 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 7.0 | 2.5 | 9.5 |
| generated_protocol | in_family | lookahead/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 3.5 | 0.0 | 3.5 |
| generated_protocol | in_family | lookahead/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 3.5 | 0.0 | 3.5 |
| generated_protocol | in_family | lookahead/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 1/2 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 6.0 | 2.5 | 8.5 |
| generated_protocol | in_family | lookahead/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 1/2 | 1 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 6.0 | 2.5 | 8.5 |

### Paired contrasts (useful coverage, within call cap)

| Contrast | Scope | Families | Budget | Conditions | Fixed rule | Parent clusters | Matched cells | Mean Δ | Descriptive 95% interval |
|---|---|---|---|---|---|---|---|---|---|
| branching - entropy | exploratory parent-cluster paired bootstrap within identical call cap and conditions; in-family fixtures pooled; few clusters, no confirmatory claim | generated_protocol | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | admission=robust | 2 | 2 | +0.000 | [+0.000, +0.000] |
| branching - lookahead | exploratory parent-cluster paired bootstrap within identical call cap and conditions; in-family fixtures pooled; few clusters, no confirmatory claim | generated_protocol | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | admission=robust | 2 | 2 | +0.000 | [+0.000, +0.000] |
| entropy - lookahead | exploratory parent-cluster paired bootstrap within identical call cap and conditions; in-family fixtures pooled; few clusters, no confirmatory claim | generated_protocol | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | admission=robust | 2 | 2 | +0.000 | [+0.000, +0.000] |
| branching - entropy | exploratory parent-cluster paired bootstrap within identical call cap and conditions; in-family fixtures pooled; few clusters, no confirmatory claim | generated_protocol | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | admission=robust | 2 | 2 | +0.000 | [+0.000, +0.000] |
| branching - lookahead | exploratory parent-cluster paired bootstrap within identical call cap and conditions; in-family fixtures pooled; few clusters, no confirmatory claim | generated_protocol | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | admission=robust | 2 | 2 | +0.000 | [+0.000, +0.000] |
| entropy - lookahead | exploratory parent-cluster paired bootstrap within identical call cap and conditions; in-family fixtures pooled; few clusters, no confirmatory claim | generated_protocol | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | admission=robust | 2 | 2 | +0.000 | [+0.000, +0.000] |
| branching - entropy | exploratory parent-cluster paired bootstrap within identical call cap and conditions; in-family fixtures pooled; few clusters, no confirmatory claim | generated_protocol | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | admission=robust | 2 | 2 | +0.000 | [+0.000, +0.000] |
| branching - lookahead | exploratory parent-cluster paired bootstrap within identical call cap and conditions; in-family fixtures pooled; few clusters, no confirmatory claim | generated_protocol | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | admission=robust | 2 | 2 | +0.000 | [+0.000, +0.000] |
| entropy - lookahead | exploratory parent-cluster paired bootstrap within identical call cap and conditions; in-family fixtures pooled; few clusters, no confirmatory claim | generated_protocol | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | admission=robust | 2 | 2 | +0.000 | [+0.000, +0.000] |
| branching - entropy | exploratory parent-cluster paired bootstrap within identical call cap and conditions; in-family fixtures pooled; few clusters, no confirmatory claim | generated_protocol | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | admission=robust | 2 | 2 | +0.000 | [+0.000, +0.000] |
| branching - lookahead | exploratory parent-cluster paired bootstrap within identical call cap and conditions; in-family fixtures pooled; few clusters, no confirmatory claim | generated_protocol | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | admission=robust | 2 | 2 | +0.000 | [+0.000, +0.000] |
| entropy - lookahead | exploratory parent-cluster paired bootstrap within identical call cap and conditions; in-family fixtures pooled; few clusters, no confirmatory claim | generated_protocol | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | admission=robust | 2 | 2 | +0.000 | [+0.000, +0.000] |


_Exploratory parent-cluster bootstrap over few fixture clusters; not a confirmatory test._

### Reliability design and sampling assumptions

Each reliability row retains its exact method, family, call cap and conditions. Independent-parent counts are declarations; interval eligibility and its reason state which sampling assumptions apply.

| Row | Family | Method | Budget | Conditions | Requests | Parent clusters | Independent parents (declared) | Inference eligible | Inference reason | Interval status |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | generated_protocol | branching/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 2 | 2 | 2 | true | independent_generator_draws_assumed | conditional_generator_sampling |
| R2 | generated_protocol | branching/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 2 | 2 | 2 | true | independent_generator_draws_assumed | conditional_generator_sampling |
| R3 | generated_protocol | branching/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 2 | 2 | 2 | true | independent_generator_draws_assumed | conditional_generator_sampling |
| R4 | generated_protocol | branching/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 2 | 2 | 2 | true | independent_generator_draws_assumed | conditional_generator_sampling |
| R5 | generated_protocol | entropy/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 2 | 2 | 2 | true | independent_generator_draws_assumed | conditional_generator_sampling |
| R6 | generated_protocol | entropy/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 2 | 2 | 2 | true | independent_generator_draws_assumed | conditional_generator_sampling |
| R7 | generated_protocol | entropy/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 2 | 2 | 2 | true | independent_generator_draws_assumed | conditional_generator_sampling |
| R8 | generated_protocol | entropy/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 2 | 2 | 2 | true | independent_generator_draws_assumed | conditional_generator_sampling |
| R9 | generated_protocol | lookahead/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 2 | 2 | 2 | true | independent_generator_draws_assumed | conditional_generator_sampling |
| R10 | generated_protocol | lookahead/robust | 4 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 2 | 2 | 2 | true | independent_generator_draws_assumed | conditional_generator_sampling |
| R11 | generated_protocol | lookahead/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=factored | 2 | 2 | 2 | true | independent_generator_draws_assumed | conditional_generator_sampling |
| R12 | generated_protocol | lookahead/robust | 8 | anchors=false; split=evaluation; horizon=4; execution_mode=shielded; temporal=false; escalate=false; probe_safety=model_safe; risk_tolerance=0; fault_schedule=null; candidate_backend=flat | 2 | 2 | 2 | true | independent_generator_draws_assumed | conditional_generator_sampling |

### Target-cluster hazard bounds

Events count semantic parents with any hazard across the saved nuisance-cell design. Targets are the parent denominator; possible rates also include unknown target outcomes. Saved intervals are pointwise bounds under the assumptions listed for each row.

| Row | Outcome | Events | Targets | Unknown targets | Observed rate | Possible rate | Confidence | Pointwise interval |
|---|---|---|---|---|---|---|---|---|
| R1 | Deployment hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R1 | Calibration hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R2 | Deployment hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R2 | Calibration hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R3 | Deployment hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R3 | Calibration hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R4 | Deployment hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R4 | Calibration hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R5 | Deployment hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R5 | Calibration hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R6 | Deployment hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R6 | Calibration hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R7 | Deployment hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R7 | Calibration hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R8 | Deployment hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R8 | Calibration hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R9 | Deployment hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R9 | Calibration hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R10 | Deployment hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R10 | Calibration hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R11 | Deployment hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R11 | Calibration hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R12 | Deployment hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |
| R12 | Calibration hazard | 0 | 2 | 0 | 0% | 0% | 95% | [0%, 84.19%] |

### Target-cluster useful coverage and selective harm

Useful coverage gives each semantic parent equal weight. Selective harm is the saved ratio of target-average failure and admission rates; it is undefined when no target admits.

| Row | Target-average useful coverage | Confidence | Pointwise interval | Conditional selective harm |
|---|---|---|---|---|
| R1 | 0% | 95% | [0%, 96.03%] | n/a |
| R2 | 0% | 95% | [0%, 96.03%] | n/a |
| R3 | 50% | 95% | [0%, 100%] | 0% |
| R4 | 50% | 95% | [0%, 100%] | 0% |
| R5 | 0% | 95% | [0%, 96.03%] | n/a |
| R6 | 0% | 95% | [0%, 96.03%] | n/a |
| R7 | 50% | 95% | [0%, 100%] | 0% |
| R8 | 50% | 95% | [0%, 100%] | 0% |
| R9 | 0% | 95% | [0%, 96.03%] | n/a |
| R10 | 0% | 95% | [0%, 96.03%] | n/a |
| R11 | 50% | 95% | [0%, 100%] | 0% |
| R12 | 50% | 95% | [0%, 100%] | 0% |

Reliability scope:

- R1, R2, R3, R4, R5, R6, R7, R8, R9, R10, R11, R12: Synthetic target-cluster estimates. Intervals, when present, assume independent generator draws and an identical fixed nuisance-cell design; each interval is pointwise, not a simultaneous guarantee. Structural hashes and planned seed selection do not establish independence or real-world probabilities. Exact binomial bounds describe any hazard across the nuisance design; useful-coverage bounds are Hoeffding bounds for equal-target means. Selective harm is the ratio of equal-target failure and admission means; abstention leaves it undefined when no target admits.
