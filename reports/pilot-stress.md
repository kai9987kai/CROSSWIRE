## Pilot Study: Out-of-Family Stress & Falsification Benchmark

- Runs: 216; source hash `12ccc80deeacb472…`; protocol hash `1dc8cc430b960163…`; scientific hash `ad1c49f782e756cb…`.
- Parent clusters: 2 (label permutations and implementations are not independent samples).

### Method × call budget (pooled over families)

| Method | Budget | Requests | Admitted | Useful coverage | Selective harm | Hazard | Interface errors | Mean calls |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| task/abstain | 16 | 36 | 0 | 0% | n/a | 0 | 4 | 6.9 |
| task/fit | 16 | 36 | 32 | 33% | 62% | 14 | 4 | 6.9 |
| task/identity | 16 | 36 | 32 | 39% | 56% | 14 | 4 | 6.9 |
| task/one_best | 16 | 36 | 22 | 22% | 64% | 10 | 4 | 6.9 |
| task/oracle | 16 | 36 | 28 | 78% | 0% | 0 | 0 | 0.0 |
| task/robust | 16 | 36 | 18 | 22% | 56% | 10 | 4 | 6.9 |

### Per family

| Family | Scope | Method | Budget | Admitted/requests | Successful | Harmful | Oracle-feasible |
|---|---|---|---:|---:|---:|---:|---:|
| alias | out_of_family | task/abstain | 16 | 0/4 | 0 | 0 | 4 |
| alias | out_of_family | task/fit | 16 | 4/4 | 2 | 2 | 4 |
| alias | out_of_family | task/identity | 16 | 4/4 | 2 | 2 | 4 |
| alias | out_of_family | task/one_best | 16 | 2/4 | 2 | 0 | 4 |
| alias | out_of_family | task/oracle | 16 | 4/4 | 4 | 0 | 4 |
| alias | out_of_family | task/robust | 16 | 2/4 | 2 | 0 | 4 |
| bypass | out_of_family | task/abstain | 16 | 0/4 | 0 | 0 | 4 |
| bypass | out_of_family | task/fit | 16 | 4/4 | 0 | 4 | 4 |
| bypass | out_of_family | task/identity | 16 | 4/4 | 2 | 2 | 4 |
| bypass | out_of_family | task/one_best | 16 | 4/4 | 0 | 4 | 4 |
| bypass | out_of_family | task/oracle | 16 | 4/4 | 4 | 0 | 4 |
| bypass | out_of_family | task/robust | 16 | 4/4 | 0 | 4 | 4 |
| delay | out_of_family | task/abstain | 16 | 0/4 | 0 | 0 | 4 |
| delay | out_of_family | task/fit | 16 | 4/4 | 2 | 2 | 4 |
| delay | out_of_family | task/identity | 16 | 4/4 | 2 | 2 | 4 |
| delay | out_of_family | task/one_best | 16 | 0/4 | 0 | 0 | 4 |
| delay | out_of_family | task/oracle | 16 | 4/4 | 4 | 0 | 4 |
| delay | out_of_family | task/robust | 16 | 0/4 | 0 | 0 | 4 |
| drift | out_of_family | task/abstain | 16 | 0/4 | 0 | 0 | 4 |
| drift | out_of_family | task/fit | 16 | 4/4 | 4 | 0 | 4 |
| drift | out_of_family | task/identity | 16 | 4/4 | 2 | 2 | 4 |
| drift | out_of_family | task/one_best | 16 | 4/4 | 4 | 0 | 4 |
| drift | out_of_family | task/oracle | 16 | 4/4 | 4 | 0 | 4 |
| drift | out_of_family | task/robust | 16 | 4/4 | 4 | 0 | 4 |
| extra_state | out_of_family | task/abstain | 16 | 0/4 | 0 | 0 | 0 |
| extra_state | out_of_family | task/fit | 16 | 4/4 | 0 | 4 | 0 |
| extra_state | out_of_family | task/identity | 16 | 4/4 | 0 | 4 | 0 |
| extra_state | out_of_family | task/one_best | 16 | 4/4 | 0 | 4 | 0 |
| extra_state | out_of_family | task/oracle | 16 | 0/4 | 0 | 0 | 0 |
| extra_state | out_of_family | task/robust | 16 | 0/4 | 0 | 0 | 0 |
| incompatible | out_of_family | task/abstain | 16 | 0/4 | 0 | 0 | 4 |
| incompatible | out_of_family | task/fit | 16 | 4/4 | 2 | 2 | 4 |
| incompatible | out_of_family | task/identity | 16 | 4/4 | 2 | 2 | 4 |
| incompatible | out_of_family | task/one_best | 16 | 0/4 | 0 | 0 | 4 |
| incompatible | out_of_family | task/oracle | 16 | 4/4 | 4 | 0 | 4 |
| incompatible | out_of_family | task/robust | 16 | 0/4 | 0 | 0 | 4 |
| malformed | interface_error | task/abstain | 16 | 0/4 | 0 | 0 | 0 |
| malformed | interface_error | task/fit | 16 | 0/4 | 0 | 0 | 0 |
| malformed | interface_error | task/identity | 16 | 0/4 | 0 | 0 | 0 |
| malformed | interface_error | task/one_best | 16 | 0/4 | 0 | 0 | 0 |
| malformed | interface_error | task/oracle | 16 | 0/4 | 0 | 0 | 0 |
| malformed | interface_error | task/robust | 16 | 0/4 | 0 | 0 | 0 |
| repeat | out_of_family | task/abstain | 16 | 0/4 | 0 | 0 | 4 |
| repeat | out_of_family | task/fit | 16 | 4/4 | 2 | 2 | 4 |
| repeat | out_of_family | task/identity | 16 | 4/4 | 2 | 2 | 4 |
| repeat | out_of_family | task/one_best | 16 | 4/4 | 2 | 2 | 4 |
| repeat | out_of_family | task/oracle | 16 | 4/4 | 4 | 0 | 4 |
| repeat | out_of_family | task/robust | 16 | 4/4 | 2 | 2 | 4 |
| semantic_corruption | out_of_family | task/abstain | 16 | 0/4 | 0 | 0 | 4 |
| semantic_corruption | out_of_family | task/fit | 16 | 4/4 | 0 | 4 | 4 |
| semantic_corruption | out_of_family | task/identity | 16 | 4/4 | 2 | 2 | 4 |
| semantic_corruption | out_of_family | task/one_best | 16 | 4/4 | 0 | 4 | 4 |
| semantic_corruption | out_of_family | task/oracle | 16 | 4/4 | 4 | 0 | 4 |
| semantic_corruption | out_of_family | task/robust | 16 | 4/4 | 0 | 4 | 4 |

### Forced-fit residuals

| Family | Implementation | Seed | Residual (raw + anchor) | Tied maps | Contract satisfied |
|---|---|---:|---:|---:|---|
| alias | procedural | 17 | 0 (0 + 0) | 2 | True |
| alias | procedural | 23 | 1 (1 + 0) | 3 | False |
| alias | table | 17 | 0 (0 + 0) | 2 | True |
| alias | table | 23 | 1 (1 + 0) | 3 | False |
| bypass | procedural | 17 | 0 (0 + 0) | 2 | False |
| bypass | procedural | 23 | 0 (0 + 0) | 1 | False |
| bypass | table | 17 | 0 (0 + 0) | 2 | False |
| bypass | table | 23 | 0 (0 + 0) | 1 | False |
| delay | procedural | 17 | 1 (1 + 0) | 72 | True |
| delay | procedural | 23 | 1 (1 + 0) | 72 | False |
| delay | table | 17 | 1 (1 + 0) | 72 | True |
| delay | table | 23 | 1 (1 + 0) | 72 | False |
| drift | procedural | 17 | 0 (0 + 0) | 2 | True |
| drift | procedural | 23 | 0 (0 + 0) | 1 | True |
| drift | table | 17 | 0 (0 + 0) | 2 | True |
| drift | table | 23 | 0 (0 + 0) | 1 | True |
| extra_state | procedural | 17 | 0 (0 + 0) | 2 | False |
| extra_state | procedural | 23 | 0 (0 + 0) | 2 | False |
| extra_state | table | 17 | 0 (0 + 0) | 2 | False |
| extra_state | table | 23 | 0 (0 + 0) | 2 | False |
| incompatible | procedural | 17 | 2 (2 + 0) | 38 | True |
| incompatible | procedural | 23 | 1 (1 + 0) | 72 | False |
| incompatible | table | 17 | 2 (2 + 0) | 38 | True |
| incompatible | table | 23 | 1 (1 + 0) | 72 | False |
| malformed | procedural | 17 | 0 (0 + 0) | 144 | None |
| malformed | procedural | 23 | 0 (0 + 0) | 144 | None |
| malformed | table | 17 | 0 (0 + 0) | 144 | None |
| malformed | table | 23 | 0 (0 + 0) | 144 | None |
| repeat | procedural | 17 | 0 (0 + 0) | 2 | True |
| repeat | procedural | 23 | 0 (0 + 0) | 2 | False |
| repeat | table | 17 | 0 (0 + 0) | 2 | True |
| repeat | table | 23 | 0 (0 + 0) | 2 | False |
| semantic_corruption | procedural | 17 | 0 (0 + 0) | 2 | False |
| semantic_corruption | procedural | 23 | 0 (0 + 0) | 1 | False |
| semantic_corruption | table | 17 | 0 (0 + 0) | 2 | False |
| semantic_corruption | table | 23 | 0 (0 + 0) | 1 | False |

