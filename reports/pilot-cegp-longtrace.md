## CEGP vs Task Policy on Long-Trace Distinguishability

- Runs: 4; source hash `a7db8dbe369bc8f8…`; protocol hash `968ed5dfe5874e08…`; scientific hash `e931c96b3d027d34…`.
- Parent clusters: 1 (label permutations and implementations are not independent samples).

### Method × call budget (pooled over families)

| Method | Budget | Requests | Admitted | Useful coverage | Selective harm | Hazard | Averted | Shield interventions | Interface errors | Mean calls |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| counterexample/robust | 16 | 2 | 2 | 100% | 0% | 0 | 0 | 0 | 0 | 15.0 |
| task/robust | 16 | 2 | 0 | 0% | n/a | 0 | 0 | 0 | 0 | 10.0 |

### Per family

| Family | Scope | Method | Budget | Admitted/requests | Successful | Harmful | Hazards | Averted | Interventions | Oracle-feasible |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| long_trace | in_family | counterexample/robust | 16 | 2/2 | 2 | 0 | 0 | 0 | 0 | 2 |
| long_trace | in_family | task/robust | 16 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |

### Paired contrasts (useful coverage, within call cap)

| Contrast | Budget | Parent clusters | Matched cells | Mean Δ | Descriptive 95% interval |
|---|---:|---:|---:|---:|---|
| task - counterexample | 16 | 1 | 2 | -1.000 | [-1.000, -1.000] |

_Exploratory parent-cluster bootstrap over few fixture clusters; not a confirmatory test._

