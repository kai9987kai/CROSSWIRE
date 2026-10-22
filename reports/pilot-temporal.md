## Temporal Adapter Synthesis on Pipeline-Delayed Interfaces

- Runs: 4; source hash `c6f7501cef90c4aa…`; protocol hash `674907c7f02dcdb7…`; scientific hash `f0eee9109c032893…`.
- Parent clusters: 1 (label permutations and implementations are not independent samples).

### Method × call budget (pooled over families)

| Method | Budget | Requests | Admitted | Useful coverage | Selective harm | Hazard | Averted | Shield interventions | Interface errors | Mean calls |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| counterexample/robust | 16 | 2 | 2 | 100% | 0% | 0 | 0 | 0 | 0 | 14.0 |
| task/robust | 16 | 2 | 2 | 100% | 0% | 0 | 0 | 0 | 0 | 11.0 |

### Per family

| Family | Scope | Method | Budget | Admitted/requests | Successful | Harmful | Hazards | Averted | Interventions | Oracle-feasible |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| delay | out_of_family | counterexample/robust | 16 | 2/2 | 2 | 0 | 0 | 0 | 0 | 2 |
| delay | out_of_family | task/robust | 16 | 2/2 | 2 | 0 | 0 | 0 | 0 | 2 |

