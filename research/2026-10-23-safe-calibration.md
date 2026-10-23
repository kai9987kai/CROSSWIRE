# Model-safe calibration — 23 October 2026

## Question and mechanism

Can the lab retain useful interoperability while refusing calibration queries that could trigger hazards under any surviving finite model? Deployment shielding leaves learning-time hazards outside its guarantee.

The new `model_safe` setting constrains all seven finite probe policies. An independent checker reconstructs each pre-probe belief and checks the entire dispatched word, including interrupted suffixes. Escalation guards the full enabled temporal envelope from the first query. If no eligible safe probe exists, acquisition stops without consuming target calls. The bounded search does not establish impossibility of all safe experiments.

## Matched local pilot

Two eight-run protocols differ only in `probe_safety`. Both use entropy probing, procedural targets, seeds 17 and 42, eight calibration calls, horizon four, evaluation split, shielded deployment, no anchors, and robust admission. Each receipt was exactly replayed after generation.

| Family | Runs per mode | Useful completions: unrestricted / safe | Hazardous calibration probes: unrestricted / safe | Mean calibration calls: unrestricted / safe | Deployment hazards: unrestricted / safe |
|---|---:|---:|---:|---:|---:|
| latch | 2 | 2 / 0 | 2 / 0 | 6 / 0 | 0 / 0 |
| routing | 2 | 2 / 2 | 0 / 0 | 5 / 5 | 0 / 0 |
| neutral | 2 | 2 / 2 | 0 / 0 | 0 / 0 | 0 / 0 |
| semantic_corruption (negative control) | 2 | 0 / 0 | 1 / 0 | 6 / 0 | 2 / 0 |

This is a tradeoff. Safe calibration retains both routing completions and refuses latch calibration because every first raw action could be hazardous. Neutral cases need no calibration. Abstaining on semantic corruption does not establish semantic grounding. Seeds are label variations, not independent semantic replications; these counts are not a confidence bound.

Receipts: [safe](../reports/pilot-calibration-safe-receipt.json), [unrestricted](../reports/pilot-calibration-unrestricted-receipt.json). Tables: [safe](../reports/pilot-calibration-safe.md), [unrestricted](../reports/pilot-calibration-unrestricted.md).

Python source SHA-256: `d4e09989ef4899df6cea086aaf315adfb302730b570b3f5d95e573800f9a68d6`.

## Evidence and usability

`risk_tolerance` now reaches the engine through CLI, API and browser. Values must be finite numbers in [0,1); positive values require `risk_controlled`. The independent certificate binds tolerance to configuration, checks reported fractions and applies no extra epsilon allowance. Unselected plans have undefined rates. These fractions use uniform weighting over candidates, not a calibrated target-risk distribution.

Study analyses and Markdown reports preserve safety, tolerance and all existing conditions. Arbitrary policy pairs can be compared within the same admission rule and matched cells; controls remain separate. The browser displays stopping reasons, safety scope, comparison conditions and individual runs while exporting/replaying the complete parent study.

## Primary sources and limits

[Alshiekh et al. (2018), Safe Reinforcement Learning via Shielding](https://ojs.aaai.org/index.php/AAAI/article/view/11797) motivates model-based constraints during learning and execution. CROSSWIRE's filter assumes model inclusion, stationarity, deterministic resets and truthful anchors; no new general shielding theorem is claimed.

[Golovin, Krause and Ray (2010)](https://papers.nips.cc/paper_files/paper/2010/hash/1e6e0a04d20f50967c64dac2d639a577-Abstract.html) introduced EC2. CROSSWIRE's Jaccard-weighted contract objective is EC2-inspired; no adaptive-submodularity or approximation theorem has been established for this implementation.

[Angelopoulos et al., Conformal Risk Control, author implementation](https://github.com/aangelopoulos/conformal-risk) calibrates observed losses to control expected test loss. Enumerating CROSSWIRE's candidate models supplies neither that sampling setup nor its guarantee. README and paper claims have been corrected.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -m crosswire study --config configs/pilot-calibration-safe.json --out reports/reproduced-safe.json
.\.venv\Scripts\python.exe -m crosswire verify reports/reproduced-safe.json
.\.venv\Scripts\python.exe -m crosswire check reports/reproduced-safe.json
.\.venv\Scripts\python.exe tools/report.py reports/reproduced-safe.json --out reports/reproduced-safe.md
```

Historical receipts require their original source revision. Hashes bind content; they do not authenticate measurements or establish truth.
