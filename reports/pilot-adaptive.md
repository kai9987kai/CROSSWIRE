## Adaptive Contingent Policy Benchmark

- Runs: 48; source hash `dbbbc06af21bc05b…`; protocol hash `6e07673c27941fc7…`; scientific hash `cbc85a6cbc260e98…`.
- Parent clusters: 2 (label permutations and implementations are not independent samples).

### Method × call budget (pooled over families)

| Method | Budget | Requests | Admitted | Useful coverage | Selective harm | Hazard | Averted | Shield interventions | Interface errors | Mean calls |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fixed/adaptive | 0 | 6 | 2 | 33% | 0% | 0 | 0 | 0 | 0 | 0.0 |
| fixed/adaptive | 8 | 6 | 2 | 33% | 0% | 0 | 0 | 0 | 0 | 4.0 |
| fixed/robust | 0 | 6 | 0 | 0% | n/a | 0 | 0 | 0 | 0 | 0.0 |
| fixed/robust | 8 | 6 | 2 | 33% | 0% | 0 | 0 | 0 | 0 | 6.0 |
| task/adaptive | 0 | 6 | 2 | 33% | 0% | 0 | 0 | 0 | 0 | 0.0 |
| task/adaptive | 8 | 6 | 4 | 50% | 25% | 1 | 0 | 0 | 0 | 4.7 |
| task/robust | 0 | 6 | 0 | 0% | n/a | 0 | 0 | 0 | 0 | 0.0 |
| task/robust | 8 | 6 | 4 | 50% | 25% | 1 | 0 | 0 | 0 | 6.7 |

### Per family

| Family | Scope | Method | Budget | Admitted/requests | Successful | Harmful | Hazards | Averted | Interventions | Oracle-feasible |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| latch | in_family | fixed/adaptive | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| latch | in_family | fixed/adaptive | 8 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| latch | in_family | fixed/robust | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| latch | in_family | fixed/robust | 8 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| latch | in_family | task/adaptive | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| latch | in_family | task/adaptive | 8 | 1/2 | 1 | 0 | 0 | 0 | 0 | 2 |
| latch | in_family | task/robust | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| latch | in_family | task/robust | 8 | 1/2 | 1 | 0 | 0 | 0 | 0 | 2 |
| routing | in_family | fixed/adaptive | 0 | 2/2 | 2 | 0 | 0 | 0 | 0 | 2 |
| routing | in_family | fixed/adaptive | 8 | 2/2 | 2 | 0 | 0 | 0 | 0 | 2 |
| routing | in_family | fixed/robust | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| routing | in_family | fixed/robust | 8 | 2/2 | 2 | 0 | 0 | 0 | 0 | 2 |
| routing | in_family | task/adaptive | 0 | 2/2 | 2 | 0 | 0 | 0 | 0 | 2 |
| routing | in_family | task/adaptive | 8 | 2/2 | 2 | 0 | 0 | 0 | 0 | 2 |
| routing | in_family | task/robust | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| routing | in_family | task/robust | 8 | 2/2 | 2 | 0 | 0 | 0 | 0 | 2 |
| semantic_corruption | out_of_family | fixed/adaptive | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| semantic_corruption | out_of_family | fixed/adaptive | 8 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| semantic_corruption | out_of_family | fixed/robust | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| semantic_corruption | out_of_family | fixed/robust | 8 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| semantic_corruption | out_of_family | task/adaptive | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| semantic_corruption | out_of_family | task/adaptive | 8 | 1/2 | 0 | 1 | 1 | 0 | 0 | 2 |
| semantic_corruption | out_of_family | task/robust | 0 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| semantic_corruption | out_of_family | task/robust | 8 | 1/2 | 0 | 1 | 1 | 0 | 0 | 2 |

### Paired contrasts (useful coverage, within call cap)

| Contrast | Budget | Parent clusters | Matched cells | Mean Δ | Descriptive 95% interval |
|---|---:|---:|---:|---:|---|
| task - fixed | 0 | 2 | 4 | +0.000 | [+0.000, +0.000] |
| task - fixed | 8 | 2 | 4 | +0.250 | [+0.000, +0.500] |
| adaptive - robust | 0 | 2 | 8 | +0.500 | [+0.000, +1.000] |
| adaptive - robust | 8 | 2 | 8 | +0.000 | [+0.000, +0.000] |

_Exploratory parent-cluster bootstrap over few fixture clusters; not a confirmatory test._
