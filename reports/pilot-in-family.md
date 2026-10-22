## Pilot Study: In-Family Interoperability Benchmark

- Runs: 350; source hash `12ccc80deeacb472…`; protocol hash `9977cf45469275ff…`; scientific hash `64c084a09fa36956…`.
- Parent clusters: 7 (label permutations and implementations are not independent samples).

### Method × call budget (pooled over families)

| Method | Budget | Requests | Admitted | Useful coverage | Selective harm | Hazard | Interface errors | Mean calls |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| aalpy/robust | 0 | 14 | 0 | 0% | n/a | 0 | 0 | 0.0 |
| aalpy/robust | 4 | 14 | 0 | 0% | n/a | 0 | 0 | 4.0 |
| aalpy/robust | 8 | 14 | 0 | 0% | n/a | 0 | 0 | 8.0 |
| aalpy/robust | 16 | 14 | 0 | 0% | n/a | 0 | 0 | 16.0 |
| aalpy/robust | 32 | 14 | 0 | 0% | n/a | 0 | 0 | 32.0 |
| disagreement/robust | 0 | 14 | 2 | 14% | 0% | 0 | 0 | 0.0 |
| disagreement/robust | 4 | 14 | 3 | 21% | 0% | 0 | 0 | 3.4 |
| disagreement/robust | 8 | 14 | 6 | 43% | 0% | 0 | 0 | 5.2 |
| disagreement/robust | 16 | 14 | 10 | 71% | 0% | 0 | 0 | 7.4 |
| disagreement/robust | 32 | 14 | 10 | 71% | 0% | 0 | 0 | 7.4 |
| fixed/robust | 0 | 14 | 2 | 14% | 0% | 0 | 0 | 0.0 |
| fixed/robust | 4 | 14 | 3 | 21% | 0% | 0 | 0 | 3.4 |
| fixed/robust | 8 | 14 | 4 | 29% | 0% | 0 | 0 | 5.0 |
| fixed/robust | 16 | 14 | 9 | 64% | 0% | 0 | 0 | 9.7 |
| fixed/robust | 32 | 14 | 10 | 71% | 0% | 0 | 0 | 14.2 |
| random/robust | 0 | 14 | 2 | 14% | 0% | 0 | 0 | 0.0 |
| random/robust | 4 | 14 | 8 | 57% | 0% | 0 | 0 | 3.4 |
| random/robust | 8 | 14 | 8 | 57% | 0% | 0 | 0 | 4.7 |
| random/robust | 16 | 14 | 9 | 64% | 0% | 0 | 0 | 7.9 |
| random/robust | 32 | 14 | 10 | 71% | 0% | 0 | 0 | 13.0 |
| task/robust | 0 | 14 | 2 | 14% | 0% | 0 | 0 | 0.0 |
| task/robust | 4 | 14 | 3 | 21% | 0% | 0 | 0 | 3.4 |
| task/robust | 8 | 14 | 6 | 43% | 0% | 0 | 0 | 5.3 |
| task/robust | 16 | 14 | 10 | 71% | 0% | 0 | 0 | 7.4 |
| task/robust | 32 | 14 | 10 | 71% | 0% | 0 | 0 | 7.4 |

### Per family

| Family | Scope | Method | Budget | Admitted/requests | Successful | Harmful | Oracle-feasible |
|---|---|---|---:|---:|---:|---:|---:|
| handshake | in_family | aalpy/robust | 0 | 0/2 | 0 | 0 | 2 |
| handshake | in_family | aalpy/robust | 4 | 0/2 | 0 | 0 | 2 |
| handshake | in_family | aalpy/robust | 8 | 0/2 | 0 | 0 | 2 |
| handshake | in_family | aalpy/robust | 16 | 0/2 | 0 | 0 | 2 |
| handshake | in_family | aalpy/robust | 32 | 0/2 | 0 | 0 | 2 |
| handshake | in_family | disagreement/robust | 0 | 0/2 | 0 | 0 | 2 |
| handshake | in_family | disagreement/robust | 4 | 0/2 | 0 | 0 | 2 |
| handshake | in_family | disagreement/robust | 8 | 0/2 | 0 | 0 | 2 |
| handshake | in_family | disagreement/robust | 16 | 2/2 | 2 | 0 | 2 |
| handshake | in_family | disagreement/robust | 32 | 2/2 | 2 | 0 | 2 |
| handshake | in_family | fixed/robust | 0 | 0/2 | 0 | 0 | 2 |
| handshake | in_family | fixed/robust | 4 | 0/2 | 0 | 0 | 2 |
| handshake | in_family | fixed/robust | 8 | 0/2 | 0 | 0 | 2 |
| handshake | in_family | fixed/robust | 16 | 1/2 | 1 | 0 | 2 |
| handshake | in_family | fixed/robust | 32 | 2/2 | 2 | 0 | 2 |
| handshake | in_family | random/robust | 0 | 0/2 | 0 | 0 | 2 |
| handshake | in_family | random/robust | 4 | 2/2 | 2 | 0 | 2 |
| handshake | in_family | random/robust | 8 | 2/2 | 2 | 0 | 2 |
| handshake | in_family | random/robust | 16 | 2/2 | 2 | 0 | 2 |
| handshake | in_family | random/robust | 32 | 2/2 | 2 | 0 | 2 |
| handshake | in_family | task/robust | 0 | 0/2 | 0 | 0 | 2 |
| handshake | in_family | task/robust | 4 | 0/2 | 0 | 0 | 2 |
| handshake | in_family | task/robust | 8 | 1/2 | 1 | 0 | 2 |
| handshake | in_family | task/robust | 16 | 2/2 | 2 | 0 | 2 |
| handshake | in_family | task/robust | 32 | 2/2 | 2 | 0 | 2 |
| interlock | in_family | aalpy/robust | 0 | 0/2 | 0 | 0 | 2 |
| interlock | in_family | aalpy/robust | 4 | 0/2 | 0 | 0 | 2 |
| interlock | in_family | aalpy/robust | 8 | 0/2 | 0 | 0 | 2 |
| interlock | in_family | aalpy/robust | 16 | 0/2 | 0 | 0 | 2 |
| interlock | in_family | aalpy/robust | 32 | 0/2 | 0 | 0 | 2 |
| interlock | in_family | disagreement/robust | 0 | 0/2 | 0 | 0 | 2 |
| interlock | in_family | disagreement/robust | 4 | 1/2 | 1 | 0 | 2 |
| interlock | in_family | disagreement/robust | 8 | 2/2 | 2 | 0 | 2 |
| interlock | in_family | disagreement/robust | 16 | 2/2 | 2 | 0 | 2 |
| interlock | in_family | disagreement/robust | 32 | 2/2 | 2 | 0 | 2 |
| interlock | in_family | fixed/robust | 0 | 0/2 | 0 | 0 | 2 |
| interlock | in_family | fixed/robust | 4 | 1/2 | 1 | 0 | 2 |
| interlock | in_family | fixed/robust | 8 | 2/2 | 2 | 0 | 2 |
| interlock | in_family | fixed/robust | 16 | 2/2 | 2 | 0 | 2 |
| interlock | in_family | fixed/robust | 32 | 2/2 | 2 | 0 | 2 |
| interlock | in_family | random/robust | 0 | 0/2 | 0 | 0 | 2 |
| interlock | in_family | random/robust | 4 | 2/2 | 2 | 0 | 2 |
| interlock | in_family | random/robust | 8 | 2/2 | 2 | 0 | 2 |
| interlock | in_family | random/robust | 16 | 2/2 | 2 | 0 | 2 |
| interlock | in_family | random/robust | 32 | 2/2 | 2 | 0 | 2 |
| interlock | in_family | task/robust | 0 | 0/2 | 0 | 0 | 2 |
| interlock | in_family | task/robust | 4 | 1/2 | 1 | 0 | 2 |
| interlock | in_family | task/robust | 8 | 2/2 | 2 | 0 | 2 |
| interlock | in_family | task/robust | 16 | 2/2 | 2 | 0 | 2 |
| interlock | in_family | task/robust | 32 | 2/2 | 2 | 0 | 2 |
| latch | in_family | aalpy/robust | 0 | 0/2 | 0 | 0 | 2 |
| latch | in_family | aalpy/robust | 4 | 0/2 | 0 | 0 | 2 |
| latch | in_family | aalpy/robust | 8 | 0/2 | 0 | 0 | 2 |
| latch | in_family | aalpy/robust | 16 | 0/2 | 0 | 0 | 2 |
| latch | in_family | aalpy/robust | 32 | 0/2 | 0 | 0 | 2 |
| latch | in_family | disagreement/robust | 0 | 0/2 | 0 | 0 | 2 |
| latch | in_family | disagreement/robust | 4 | 0/2 | 0 | 0 | 2 |
| latch | in_family | disagreement/robust | 8 | 1/2 | 1 | 0 | 2 |
| latch | in_family | disagreement/robust | 16 | 2/2 | 2 | 0 | 2 |
| latch | in_family | disagreement/robust | 32 | 2/2 | 2 | 0 | 2 |
| latch | in_family | fixed/robust | 0 | 0/2 | 0 | 0 | 2 |
| latch | in_family | fixed/robust | 4 | 0/2 | 0 | 0 | 2 |
| latch | in_family | fixed/robust | 8 | 0/2 | 0 | 0 | 2 |
| latch | in_family | fixed/robust | 16 | 2/2 | 2 | 0 | 2 |
| latch | in_family | fixed/robust | 32 | 2/2 | 2 | 0 | 2 |
| latch | in_family | random/robust | 0 | 0/2 | 0 | 0 | 2 |
| latch | in_family | random/robust | 4 | 1/2 | 1 | 0 | 2 |
| latch | in_family | random/robust | 8 | 1/2 | 1 | 0 | 2 |
| latch | in_family | random/robust | 16 | 2/2 | 2 | 0 | 2 |
| latch | in_family | random/robust | 32 | 2/2 | 2 | 0 | 2 |
| latch | in_family | task/robust | 0 | 0/2 | 0 | 0 | 2 |
| latch | in_family | task/robust | 4 | 0/2 | 0 | 0 | 2 |
| latch | in_family | task/robust | 8 | 1/2 | 1 | 0 | 2 |
| latch | in_family | task/robust | 16 | 2/2 | 2 | 0 | 2 |
| latch | in_family | task/robust | 32 | 2/2 | 2 | 0 | 2 |
| long_trace | in_family | aalpy/robust | 0 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | aalpy/robust | 4 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | aalpy/robust | 8 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | aalpy/robust | 16 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | aalpy/robust | 32 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | disagreement/robust | 0 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | disagreement/robust | 4 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | disagreement/robust | 8 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | disagreement/robust | 16 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | disagreement/robust | 32 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | fixed/robust | 0 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | fixed/robust | 4 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | fixed/robust | 8 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | fixed/robust | 16 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | fixed/robust | 32 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | random/robust | 0 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | random/robust | 4 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | random/robust | 8 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | random/robust | 16 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | random/robust | 32 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | task/robust | 0 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | task/robust | 4 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | task/robust | 8 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | task/robust | 16 | 0/2 | 0 | 0 | 2 |
| long_trace | in_family | task/robust | 32 | 0/2 | 0 | 0 | 2 |
| neutral | in_family | aalpy/robust | 0 | 0/2 | 0 | 0 | 2 |
| neutral | in_family | aalpy/robust | 4 | 0/2 | 0 | 0 | 2 |
| neutral | in_family | aalpy/robust | 8 | 0/2 | 0 | 0 | 2 |
| neutral | in_family | aalpy/robust | 16 | 0/2 | 0 | 0 | 2 |
| neutral | in_family | aalpy/robust | 32 | 0/2 | 0 | 0 | 2 |
| neutral | in_family | disagreement/robust | 0 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | disagreement/robust | 4 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | disagreement/robust | 8 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | disagreement/robust | 16 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | disagreement/robust | 32 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | fixed/robust | 0 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | fixed/robust | 4 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | fixed/robust | 8 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | fixed/robust | 16 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | fixed/robust | 32 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | random/robust | 0 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | random/robust | 4 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | random/robust | 8 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | random/robust | 16 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | random/robust | 32 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | task/robust | 0 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | task/robust | 4 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | task/robust | 8 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | task/robust | 16 | 2/2 | 2 | 0 | 2 |
| neutral | in_family | task/robust | 32 | 2/2 | 2 | 0 | 2 |
| rotary | in_family | aalpy/robust | 0 | 0/2 | 0 | 0 | 2 |
| rotary | in_family | aalpy/robust | 4 | 0/2 | 0 | 0 | 2 |
| rotary | in_family | aalpy/robust | 8 | 0/2 | 0 | 0 | 2 |
| rotary | in_family | aalpy/robust | 16 | 0/2 | 0 | 0 | 2 |
| rotary | in_family | aalpy/robust | 32 | 0/2 | 0 | 0 | 2 |
| rotary | in_family | disagreement/robust | 0 | 0/2 | 0 | 0 | 2 |
| rotary | in_family | disagreement/robust | 4 | 0/2 | 0 | 0 | 2 |
| rotary | in_family | disagreement/robust | 8 | 1/2 | 1 | 0 | 2 |
| rotary | in_family | disagreement/robust | 16 | 2/2 | 2 | 0 | 2 |
| rotary | in_family | disagreement/robust | 32 | 2/2 | 2 | 0 | 2 |
| rotary | in_family | fixed/robust | 0 | 0/2 | 0 | 0 | 2 |
| rotary | in_family | fixed/robust | 4 | 0/2 | 0 | 0 | 2 |
| rotary | in_family | fixed/robust | 8 | 0/2 | 0 | 0 | 2 |
| rotary | in_family | fixed/robust | 16 | 2/2 | 2 | 0 | 2 |
| rotary | in_family | fixed/robust | 32 | 2/2 | 2 | 0 | 2 |
| rotary | in_family | random/robust | 0 | 0/2 | 0 | 0 | 2 |
| rotary | in_family | random/robust | 4 | 1/2 | 1 | 0 | 2 |
| rotary | in_family | random/robust | 8 | 1/2 | 1 | 0 | 2 |
| rotary | in_family | random/robust | 16 | 1/2 | 1 | 0 | 2 |
| rotary | in_family | random/robust | 32 | 2/2 | 2 | 0 | 2 |
| rotary | in_family | task/robust | 0 | 0/2 | 0 | 0 | 2 |
| rotary | in_family | task/robust | 4 | 0/2 | 0 | 0 | 2 |
| rotary | in_family | task/robust | 8 | 0/2 | 0 | 0 | 2 |
| rotary | in_family | task/robust | 16 | 2/2 | 2 | 0 | 2 |
| rotary | in_family | task/robust | 32 | 2/2 | 2 | 0 | 2 |
| symmetric | in_family | aalpy/robust | 0 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | aalpy/robust | 4 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | aalpy/robust | 8 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | aalpy/robust | 16 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | aalpy/robust | 32 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | disagreement/robust | 0 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | disagreement/robust | 4 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | disagreement/robust | 8 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | disagreement/robust | 16 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | disagreement/robust | 32 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | fixed/robust | 0 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | fixed/robust | 4 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | fixed/robust | 8 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | fixed/robust | 16 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | fixed/robust | 32 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | random/robust | 0 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | random/robust | 4 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | random/robust | 8 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | random/robust | 16 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | random/robust | 32 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | task/robust | 0 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | task/robust | 4 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | task/robust | 8 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | task/robust | 16 | 0/2 | 0 | 0 | 2 |
| symmetric | in_family | task/robust | 32 | 0/2 | 0 | 0 | 2 |

### Paired contrasts (useful coverage, within call cap)

| Contrast | Budget | Parent clusters | Matched cells | Mean Δ | Descriptive 95% interval |
|---|---:|---:|---:|---:|---|
| task - aalpy | 0 | 7 | 14 | +0.143 | [+0.000, +0.429] |
| task - disagreement | 0 | 7 | 14 | +0.000 | [+0.000, +0.000] |
| task - fixed | 0 | 7 | 14 | +0.000 | [+0.000, +0.000] |
| task - random | 0 | 7 | 14 | +0.000 | [+0.000, +0.000] |
| task - aalpy | 4 | 7 | 14 | +0.214 | [+0.000, +0.500] |
| task - disagreement | 4 | 7 | 14 | +0.000 | [+0.000, +0.000] |
| task - fixed | 4 | 7 | 14 | +0.000 | [+0.000, +0.000] |
| task - random | 4 | 7 | 14 | -0.357 | [-0.643, -0.143] |
| task - aalpy | 8 | 7 | 14 | +0.429 | [+0.143, +0.714] |
| task - disagreement | 8 | 7 | 14 | +0.000 | [-0.214, +0.214] |
| task - fixed | 8 | 7 | 14 | +0.143 | [+0.000, +0.286] |
| task - random | 8 | 7 | 14 | -0.143 | [-0.286, +0.000] |
| task - aalpy | 16 | 7 | 14 | +0.714 | [+0.429, +1.000] |
| task - disagreement | 16 | 7 | 14 | +0.000 | [+0.000, +0.000] |
| task - fixed | 16 | 7 | 14 | +0.071 | [+0.000, +0.214] |
| task - random | 16 | 7 | 14 | +0.071 | [+0.000, +0.214] |
| task - aalpy | 32 | 7 | 14 | +0.714 | [+0.429, +1.000] |
| task - disagreement | 32 | 7 | 14 | +0.000 | [+0.000, +0.000] |
| task - fixed | 32 | 7 | 14 | +0.000 | [+0.000, +0.000] |
| task - random | 32 | 7 | 14 | +0.000 | [+0.000, +0.000] |

_Exploratory parent-cluster bootstrap over few fixture clusters; not a confirmatory test._

