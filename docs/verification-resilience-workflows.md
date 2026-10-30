# Resilience workflow verification — 2026-10-30

The upgrade completes controlled fault experiments across runs, studies, browser configuration, condition-stratified analysis and saved reports. It also repairs demonstrated finite certification and private audit errors. All evidence here is local and synthetic.

## Implemented behavior

- Optional sensor drift, actuator swap, injected delay, stuck output and semantic swap settings include a zero-based onset, explicit calibration/deployment/both phase, and validated stuck symbol. Unknown fields and ineffective duplicate schedule defaults are rejected.
- Studies accept `fault_schedules`, including `null` nominal controls. Shared condition identity prevents different types, phases, onset steps or stuck symbols from pooling or matching. Saved summaries, reliability records, reports and workbench tables retain those settings.
- Faults compose with existing sensor/semantic mechanisms. Independent injected-delay memory is reset and included in the private finite target export. Equivalence checking uses deployment-phase dynamics and a saturated onset counter. Onsets beyond 512 withhold an exact exported model rather than allocating an unbounded state graph; actual trajectory auditing still executes the schedule.
- Calibration hazard reconstruction uses calibration phase. Calibration-only schedules do not masquerade as detected deployment change points.
- Policy information metrics distinguish complete observation paths, soft-return synthesis obeys the remaining horizon, and contract evaluation supports larger nonnegative output alphabets.
- Reports check saved envelope and scientific digests, including historical source identities. This is integrity checking, not target replay or authentication. Import and replay still require the exact source revision.
- CI now checks the wheel in a clean temporary environment outside the checkout, with isolated Python, actual deployment and replay. It compares installed Python source identity and every web asset against the checkout.

## Validation

The final pre-publication full suite passed: **539 tests in 300.10 seconds**, including the direct-script CLI regressions. The report-rendering check also passed all 23 report tests. Expected failures were reproduced for the corrected scientific behaviors.

- Real Chromium workbench check passed: native input validation, nominal defaults, fault configuration, actual faulted run and paired study, export, import/replay, row inspection, model diagnostics and 390-pixel mobile layout. Desktop and mobile screenshots were inspected.
- Fresh eight-run study: `configs/resilience-workflows.json` -> `reports/resilience-workflows-receipt.json`. Independent public checking passed all eight runs. CLI exact replay matched scientific hash `a4d9a0fa2aec1b776bc04f64535d8252c6761c4586230ca1ce131111e4a72e1f`.
- All 14 saved study receipts passed source-independent digest validation and report rendering. The original 13 receipt files remain unchanged; those require their original source revision for replay.
- Wheel built successfully. Its clean outside-checkout installation matched Python source hash `f0c070bc77cebfbd711ec6be9282ed20779d1e6aa91769619905d345f4ee20a1` and all three web assets. A real routing/adaptive/shielded smoke used zero acquisition calls and five deployment calls, then replayed exactly. Empty/multiple-wheel inputs and stale-source wheels were rejected.
- The standalone report command was exercised from outside the checkout under isolated Python, for valid historical evidence and corrupted evidence.
- Wheel and source distribution builds passed. Archive inspection confirmed the web assets, shared conditions module, new configuration/receipt, verification document and distribution checker are included where required. `git diff --check` passed.

## Fresh smoke-study outcomes and scope

Both table and procedural engines were nuisance repeats of one latch parent, with label seed 42 and unrestricted calibration at budget 16. This is a workflow regression demonstration, not an independently sampled reliability study.

| Deployment condition | Runs | Goal completions | Monitor interventions | Audited deployment hazards |
|---|---:|---:|---:|---|
| Nominal | 2 | 2 | 0 | 0 |
| Sensor drift at step 2 | 2 | 0 | 2 | No hazard in observed prefix; incomplete outcome remains unknown |
| Stuck output at step 2 | 2 | 0 | 2 | No hazard in observed prefix; incomplete outcome remains unknown |
| Semantic swap at step 1 | 2 | 0 | 0 | 2 |

Unrestricted calibration incurred one hazardous probe per run and is reported separately from deployment. Semantic swaps remained invisible in raw outputs and hazardous in the private audit. No deployment-safety or semantic-grounding claim follows from these results.

The factored solver and soft-return synthesizer remain direct library capabilities. Current CLI/run/study acquisition uses `CandidateSpace`. This report records local verification; publication and hosted Windows/Linux, Python 3.11/3.12 CI results are tracked separately in Git and GitHub Actions.
