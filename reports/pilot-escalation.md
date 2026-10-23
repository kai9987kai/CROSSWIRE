## Pilot Escalation, Entropy & Recovery Study

- Runs: 36; source hash `2b4e91062652f06a…`; protocol hash `74257f9947c445e3…`; scientific hash `741aac4f5f86eb51…`.
- Parent clusters: 1 (label permutations and implementations are not independent samples).

### Method × call budget (pooled over families)

| Method | Budget | Requests | Admitted | Useful coverage | Selective harm | Hazard | Averted | Shield interventions | Interface errors | Mean calls |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| entropy/robust | 0 | 6 | 0 | 0% | n/a | 0 | 0 | 0 | 0 | 0.0 |
| entropy/robust | 16 | 6 | 4 | 50% | 25% | 0 | 1 | 1 | 0 | 7.0 |
| fixed/robust | 0 | 6 | 0 | 0% | n/a | 0 | 0 | 0 | 0 | 0.0 |
| fixed/robust | 16 | 6 | 2 | 33% | 0% | 0 | 0 | 0 | 0 | 10.5 |
| task/robust | 0 | 6 | 0 | 0% | n/a | 0 | 0 | 0 | 0 | 0.0 |
| task/robust | 16 | 6 | 4 | 67% | 0% | 0 | 0 | 0 | 0 | 10.2 |

### Per family

| Family | Scope | Method | Budget | Admitted/requests | Successful | Harmful | Hazards | Averted | Interventions | Oracle-feasible |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| delay | out_of_family | entropy/robust | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| delay | out_of_family | entropy/robust | 16 | 2/2 | 1 | 1 | 0 | 1 | 1 | 2 |
| delay | out_of_family | fixed/robust | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| delay | out_of_family | fixed/robust | 16 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| delay | out_of_family | task/robust | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| delay | out_of_family | task/robust | 16 | 2/2 | 2 | 0 | 0 | 0 | 0 | 2 |
| incompatible | out_of_family | entropy/robust | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| incompatible | out_of_family | entropy/robust | 16 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| incompatible | out_of_family | fixed/robust | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| incompatible | out_of_family | fixed/robust | 16 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| incompatible | out_of_family | task/robust | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| incompatible | out_of_family | task/robust | 16 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| latch | in_family | entropy/robust | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| latch | in_family | entropy/robust | 16 | 2/2 | 2 | 0 | 0 | 0 | 0 | 2 |
| latch | in_family | fixed/robust | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| latch | in_family | fixed/robust | 16 | 2/2 | 2 | 0 | 0 | 0 | 0 | 2 |
| latch | in_family | task/robust | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| latch | in_family | task/robust | 16 | 2/2 | 2 | 0 | 0 | 0 | 0 | 2 |

### Paired contrasts (useful coverage, within call cap)

| Contrast | Budget | Parent clusters | Matched cells | Mean Δ | Descriptive 95% interval |
|---|---:|---:|---:|---:|---|
| task - entropy | 0 | 1 | 2 | +0.000 | [+0.000, +0.000] |
| task - fixed | 0 | 1 | 2 | +0.000 | [+0.000, +0.000] |
| task - entropy | 16 | 1 | 2 | +0.000 | [+0.000, +0.000] |
| task - fixed | 16 | 1 | 2 | +0.000 | [+0.000, +0.000] |

_Exploratory parent-cluster bootstrap over few fixture clusters; not a confirmatory test._

