## Shielded Closed-Loop Stress Benchmark

- Runs: 36; source hash `a7db8dbe369bc8f8…`; protocol hash `f786f6803d92214b…`; scientific hash `7e4c626579e139d5…`.
- Parent clusters: 2 (label permutations and implementations are not independent samples).

### Method × call budget (pooled over families)

| Method | Budget | Requests | Admitted | Useful coverage | Selective harm | Hazard | Averted | Shield interventions | Interface errors | Mean calls |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| task/fit | 16 | 18 | 16 | 11% | 88% | 5 | 2 | 8 | 2 | 6.9 |
| task/robust | 16 | 18 | 9 | 11% | 78% | 5 | 0 | 3 | 2 | 6.9 |

### Per family

| Family | Scope | Method | Budget | Admitted/requests | Successful | Harmful | Hazards | Averted | Interventions | Oracle-feasible |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| alias | out_of_family | task/fit | 16 | 2/2 | 0 | 2 | 0 | 1 | 2 | 2 |
| alias | out_of_family | task/robust | 16 | 1/2 | 0 | 1 | 0 | 0 | 1 | 2 |
| bypass | out_of_family | task/fit | 16 | 2/2 | 0 | 2 | 2 | 0 | 0 | 2 |
| bypass | out_of_family | task/robust | 16 | 2/2 | 0 | 2 | 2 | 0 | 0 | 2 |
| delay | out_of_family | task/fit | 16 | 2/2 | 0 | 2 | 0 | 1 | 2 | 2 |
| delay | out_of_family | task/robust | 16 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| drift | out_of_family | task/fit | 16 | 2/2 | 2 | 0 | 0 | 0 | 0 | 2 |
| drift | out_of_family | task/robust | 16 | 2/2 | 2 | 0 | 0 | 0 | 0 | 2 |
| extra_state | out_of_family | task/fit | 16 | 2/2 | 0 | 2 | 0 | 0 | 0 | 0 |
| extra_state | out_of_family | task/robust | 16 | 0/2 | 0 | 0 | 0 | 0 | 0 | 0 |
| incompatible | out_of_family | task/fit | 16 | 2/2 | 0 | 2 | 0 | 0 | 2 | 2 |
| incompatible | out_of_family | task/robust | 16 | 0/2 | 0 | 0 | 0 | 0 | 0 | 2 |
| malformed | interface_error | task/fit | 16 | 0/2 | 0 | 0 | 0 | 0 | 0 | 0 |
| malformed | interface_error | task/robust | 16 | 0/2 | 0 | 0 | 0 | 0 | 0 | 0 |
| repeat | out_of_family | task/fit | 16 | 2/2 | 0 | 2 | 1 | 0 | 2 | 2 |
| repeat | out_of_family | task/robust | 16 | 2/2 | 0 | 2 | 1 | 0 | 2 | 2 |
| semantic_corruption | out_of_family | task/fit | 16 | 2/2 | 0 | 2 | 2 | 0 | 0 | 2 |
| semantic_corruption | out_of_family | task/robust | 16 | 2/2 | 0 | 2 | 2 | 0 | 0 | 2 |

### Forced-fit residuals

| Family | Implementation | Seed | Residual (raw + anchor) | Tied maps | Contract satisfied |
|---|---|---:|---:|---:|---|
| alias | procedural | 17 | 0 (0 + 0) | 2 | False |
| alias | procedural | 23 | 1 (1 + 0) | 3 | False |
| bypass | procedural | 17 | 0 (0 + 0) | 2 | False |
| bypass | procedural | 23 | 0 (0 + 0) | 1 | False |
| delay | procedural | 17 | 1 (1 + 0) | 72 | False |
| delay | procedural | 23 | 1 (1 + 0) | 72 | False |
| drift | procedural | 17 | 0 (0 + 0) | 2 | True |
| drift | procedural | 23 | 0 (0 + 0) | 1 | True |
| extra_state | procedural | 17 | 0 (0 + 0) | 2 | False |
| extra_state | procedural | 23 | 0 (0 + 0) | 2 | False |
| incompatible | procedural | 17 | 2 (2 + 0) | 38 | False |
| incompatible | procedural | 23 | 1 (1 + 0) | 72 | False |
| malformed | procedural | 17 | 0 (0 + 0) | 144 | None |
| malformed | procedural | 23 | 0 (0 + 0) | 144 | None |
| repeat | procedural | 17 | 0 (0 + 0) | 2 | False |
| repeat | procedural | 23 | 0 (0 + 0) | 2 | False |
| semantic_corruption | procedural | 17 | 0 (0 + 0) | 2 | False |
| semantic_corruption | procedural | 23 | 0 (0 + 0) | 1 | False |

