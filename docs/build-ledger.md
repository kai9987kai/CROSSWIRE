# CROSSWIRE build ledger

Approved design: 22 October 2026. Baseline commit `3a7385b`. User explicitly approved building in the new standalone folder.

Ruling: execute the implementation plan without another approval round — the direct “Approve—build CROSSWIRE” instruction authorizes implementation — routine implementation choices remain reviewable in Git.

Ruling: retain the standalone checkout rather than create another worktree — the user's named new project folder is the intended work location — no existing NEUROGRAFT source/checkpoint is part of this build.

Ruling: parallelize disjoint core, target-protocol and browser files — active multi-agent instructions favor independent work and each worker has exclusive paths — root owns integration and commits; shared interfaces are fixed in implementation-contract.md.

## Preflight interface scan

| Tasks | Produced/consumed boundary | Finding |
|---|---|---|
| 1 / 2 | Machine serialization used by fixture references/audit models | fixed tuple cells and integer opaque symbols |
| 1 / 3 | CandidateSpace predictions/plans/ambiguity and exact product comparison | fixed methods and counters, root does not introspect private target |
| 2 / 3 | Case public/private and TargetProcess query/step/reset/costs | public-only learner input, audit after freeze |
| 3 / 4 | Run results, receipt exports and async job status | fixed HTTP and result schema |
| 4 / 5 | CLI/package/web assets | root verifies wheel and actual browser workflows |
| 1 | Algebra tests versus core implementation | excludes empty-family vacuous admission and prefix hazards |
| 2 | Fixture independence versus runtime | procedural branch cannot read reference transition table |
| 3 | Exact guarantees versus finite evidence | conditional soundness; misspecification/semantic corruption explicit |
| 4 | UI versus core | visualizes Python output, no duplicated scientific learner |
| 5 | Research conclusion versus software status | negative pilot permitted; no breakthrough/publication claim |

## Integration Review Rulings & Resolutions

1. **Deployment Prefix Auditing:** Fixed in `audit.py`. Only executed prefixes are audited; aborted suffixes are never simulated as if executed.
2. **Unified System-Call Cap:** Fixed in `study.py` and `baselines.py`. Resets and steps share a common call budget $B$.
3. **Deployment Failure Accounting:** Fixed in `study.py`. Deployment interface crashes are counted in summary metrics without mutating frozen decisions.
4. **Forced-Fit Residual Diagnostics:** Fixed in `study.py`. Preserved chosen adapter and residual mismatch breakdown in baseline diagnostics.
5. **AALpy Transition Work:** Fixed in `baselines.py`. Model comparison steps are counted explicitly.
6. **Stratified Paired Contrasts:** Fixed in `study.py`. Matched cell-by-cell comparisons remain within identical call-cap levels.
7. **Asynchronous Import/Replay:** Fixed in `server.py` and `app.js`. Receipt import and verification run as cancellable jobs on the scientific worker.

## Milestone Status

- [x] **Task 1 (Core Algebra & Mappings):** Completed and verified with 17 tests.
- [x] **Task 2 (Targets & Subprocess Protocol):** Completed and verified with 34 tests.
- [x] **Task 3 (Study Orchestration, AALpy, Audit, Receipts):** Completed and verified with 20 tests.
- [x] **Task 4 (CLI, Async Job Server, Browser Workbench):** Completed and verified with 9 tests, Playwright e2e automation, and mobile responsive check.
- [x] **Task 5 (Reproducible Pilot Benchmarks, Verification, Documentation):** 
  - Smoke benchmark (27 runs): verified.
  - In-family benchmark (350 runs): verified.
  - Stress benchmark (216 runs): verified.
  - Wheel build & clean environment parity: verified.
  - `docs/paper.md` and `docs/verification.md`: authored.
  - `README.md` and `Run-CROSSWIRE.ps1`: operational.
- [x] **Task 6 (Closed-Loop Dynamic Runtime Shield, Temporal Adapter Synthesis, & CEGP):**
  - Closed-Loop Dynamic Runtime Shield (`crosswire/shield.py`): monitors deployment step responses; halts on empty survivor set or pre-emptively intercepts latent hazard suffixes; verified with 3 tests in `tests/test_shield.py`.
  - Temporal Latency-Aware Adapter Algebra (`crosswire/core.py`): expands candidate space to 720 models supporting 1-step pipeline delay and initial buffer search; 3-tuple synchronized product comparison; verified with 3 tests in `tests/test_temporal.py`.
  - Counterexample-Guided Active Probing (`crosswire/core.py`): optimized $O(W \cdot N)$ marginal frequency counting for pair disagreement; verified with 2 tests in `tests/test_cegp.py`.
  - Integrated full test suite passing (88/88 passed in 44.55s).
  - Open-Loop vs. Shielded Comparative Benchmark (`reports/pilot-shield-openloop-receipt.json` & `reports/pilot-shield-shielded-receipt.json`, 72 runs): empirically verified 8 hazards averted on misspecified targets.
  - Temporal Adapter Benchmark (`reports/pilot-temporal-receipt.json`, 4 runs): achieved 100% useful coverage with 0% selective harm on pipeline-delayed interfaces.
  - Total verified empirical evaluations: 669 runs.
  - Research paper and verification report updated with empirical tables and mathematical formulations.
- [x] **Task 7 (Decision-Focused CEGP Witnesses, Pre-Step Guarding, Causal Auditing, & Portfolio Survey):**
  - Decision-focused CEGP probe synthesis (`crosswire/core.py`): dynamically synthesizes exact distinguishing counterexample witnesses via product BFS beyond the fixed probe pool. Evaluated on `long_trace`, resolving candidates that stalled standard policies and achieving 100% useful coverage (+1.000 paired difference).
  - Pre-step preemptive hazard interception (`crosswire/shield.py`): evaluates pending action before dispatch; halts without executing `target.step` if the action is unanimously hazardous under surviving adapters.
  - Full Test Suite Passing (`tests/test_escalation.py` + full suite): 116/116 tests passing in 117.88s.
  - Empirical Benchmark (`reports/pilot-escalation-receipt.json` & `reports/pilot-escalation.md`, 36 runs): demonstrated 4.5 mean calls for entropy probing on `latch` (vs 8.5 for `task` and 9.0 for `fixed`), verified autonomous escalation on `delay`, certified structural contradiction on `incompatible`, and confirmed Simplex hazard aversion. Cryptographic replay verified bit-exact reproduction. Total verified empirical evaluations: 757 runs.
- [x] **Task 10 (Independent Public-Evidence Certificates, Conservative Recovery, & Condition-Stratified Analysis):**
  - Independent Public-Evidence Checker (`crosswire/certificates.py`): independently re-enumerates adapters from first principles without importing `CandidateSpace` or internal caches; verifies surviving belief sets against public transcripts and anchors; validates robust words and adaptive policy trees; extracts deletion-minimal contradiction cores upon refutation; binds `evidence_certificate` before freezing decisions.
  - Conservative Simplex Recovery Fallback (`crosswire/shield.py`): guarantees recovery fallback dispatch occurs only when live belief is consistent, non-empty, within horizon, and possesses an action with zero modeled hazards across all surviving interpretations. Contradicted beliefs trigger immediate abstention (`INTERVENED_ANOMALY`) rather than speculative action.
  - Condition-Stratified Analysis & Exact-Cell Pairing (`crosswire/study.py` & `crosswire/audit.py`): enforces strict stratification across execution mode, escalation setting, split, anchors, and horizon to prevent cross-condition leakage; audits only executed prefix actions rather than unexecuted suffixes.
  - Full Workbench Verification & Browser Automation (`crosswire/web/app.js`, `crosswire/web/index.html`, `tools/check_workbench.cjs`): fixed JS floating-point serialization divergence via raw text streaming; rendered public model evidence panel with certificate status; verified end-to-end with headless Chromium via Playwright.
  - Full Test Suite Passing: 158/158 tests passing in 145.07s across 15 test modules. Wheel build verified.
- [x] **Task 11 (Submodular EC2 Active Probing, Receding-Horizon Replanning Shield, & Risk-Controlled Admission):**
  - Submodular Equivalence Class Edge Cutting Probing (`crosswire/core.py`, `crosswire/study.py`): partitions candidate adapters into contract decision equivalence classes; selects probe sequences cutting cross-class edges weighted by Jaccard distance; filters out queries that differentiate contract-equivalent adapters without altering admission. Verified with 6 tests in `tests/test_ec2.py`.
  - Receding-Horizon Dynamic Replanning Shield (`crosswire/shield.py`, `crosswire/study.py`): implements `"replan"` execution mode; dynamically tracks belief state during deployment; upon encountering intermediate observations that prune surviving models and expose suffix hazards or dead-ends, executes online bounded BFS (`_find_safe_suffix`) to discover verified safe detours (`REPLANNED_ONLINE_SAFE`), salvaging execution without hazard. Verified with 5 tests in `tests/test_replan.py`.
  - Risk-Controlled Version-Space Admission (`crosswire/core.py`, `crosswire/study.py`, `crosswire/certificates.py`): implements `"risk_controlled"` admission mode inspired by conformal risk control; admits plans satisfying certified risk tolerance $\hat{R}_{\text{hazard}} \le \epsilon$ and goal tolerance $\hat{G}_{\text{goal}} \ge 1 - \delta$; strictly recovers robust consensus when $\epsilon = 0.0$; validated via independent public certificates. Verified with 4 tests in `tests/test_risk_controlled.py`.
  - Empirical Benchmark (`reports/pilot-replanning-ec2-receipt.json`, 96 runs): evaluated across `delay`, `handshake`, and `latch` under replanning execution; confirmed 100% useful coverage for `ec2` on `delay` via autonomous escalation; verified zero selective harm; cryptographically validated with `crosswire verify` and `crosswire check`. Brings total verified empirical evaluations to 853 runs across 10 benchmarks.
  - Workbench & UI End-to-End Automation (`crosswire/web/app.js`, `crosswire/web/index.html`, `tools/check_workbench.cjs`): wired `ec2`, `replan`, and `risk_controlled` into controls, status badges, replanning detour indicators, and contradiction core inspectors; verified with Playwright Chromium test.
  - Full Test Suite Passing: 173/173 tests passing in 127.39s across 18 test modules. Wheel build verified.
- [x] **Task 12 (Model-Safe Active Calibration & Configurable Risk Certification - Priorities 1 & 2):**
  - Model-Safe Calibration Guards (`crosswire/core.py`, `crosswire/study.py`): pre-evaluates pending probe queries against surviving adapter beliefs; guarantees no admitted probe sequence triggers a modeled hazard under any surviving interpretation (`probe_safety="model_safe"` vs `"unrestricted"`); halts safely when no safe probe exists.
  - Configurable Risk Tolerance Certification (`crosswire/certificates.py`, `crosswire/study.py`): exposes `--risk-tolerance` across CLI, study runner, and UI; verifies empirical risk fractions in independent evidence certificates.
  - Empirical Studies (`reports/pilot-calibration-safe-receipt.json` & `reports/pilot-calibration-unrestricted-receipt.json`, 16 runs): demonstrated zero calibration hazards under model-safe probing vs 2 calibration hazards under unrestricted probing.
- [x] **Task 13 (Uncertainty Diagnostics & Independent Statistical Reliability - Priorities 3 & 4):**
  - Public Model-Mismatch Diagnostics (`crosswire/certificates.py`): evaluates sequential forecasts before observing each output; identifies earliest model class refutations and reset-prefix inconsistencies; reports explicit semantic blind spots (semantic corruption, bypass, unobserved transitions); preserves UNKNOWN inclusion status for compatible models without over-claiming.
  - Independent Target Dynamics & Versioned Generator (`crosswire/fixtures.py`): implements `generated_protocol` with separate structural `instance_seed` and label `seed`; generates independently sampled stages, progress/fallback actions, and absorbing terminals; procedural targets do not introspect reference tables.
  - Target-Cluster Statistical Reliability (`crosswire/reliability.py`): aggregates nuisance label permutations and procedural/table implementations within parent clusters; computes exact binomial hazard bounds and conservative Hoeffding coverage intervals for equal-target means; withholds intervals for legacy fixtures or unequal designs.
  - Empirical Benchmark (`reports/pilot-independent-protocols-receipt.json`, 128 runs over 32 parent clusters): verified 81.25% useful coverage for `entropy/robust` and 75% for `fixed/robust` with 0% selective harm; verified exact bit-level replay across all 128 runs. Total verified empirical evaluations reached 997 runs across 13 benchmarks.
  - Full Test Suite Passing: 321/321 tests passing in 93s across 25 test modules. Browser workbench check verified.
- [x] **Task 14 (Adaptive Branching Calibration & Dual-OS CI Workflow - Priorities 5 & 10):**
  - Adaptive Within-Query Branching Calibration (`crosswire/core.py`, `crosswire/study.py`): implemented `choose_branching_step` and `policy="branching"`; selects next action conditionally based on live within-query observations; evaluates predictive output entropy and pre-probe model safety at every dispatch; terminates early when contract consensus is achieved or ambiguity is fully resolved; reduces target call overhead. Verified with 10 unit tests in `tests/test_branching_calibration.py`.
  - Continuous Integration & Release Automation (`.github/workflows/ci.yml`): added dual-OS matrix workflow across Ubuntu and Windows for Python 3.11 and 3.12; automates testing, clean wheel packaging and installation, scientific receipt replay verification, and headless Playwright Chromium workbench end-to-end checks.
  - Full Test Suite Passing: 331/331 tests passing across 26 test modules. Browser workbench check verified.
- [x] **Task 15 (Online Replanning Fault Schedules & Factored Candidate Spaces - Priorities 6 & 7):**
  - Explicit Change-Point Fault Schedules & Latency Measurement (`crosswire/fixtures.py`, `crosswire/shield.py`, `crosswire/study.py`, `crosswire/audit.py`, `crosswire/cli.py`): added `fault_schedule` to `RunConfig`, `_Engine`, and CLI; supports 5 runtime fault transformation modes (`sensor_drift`, `actuator_swap`, `delay_spike`, `stuck_output`, `semantic_swap`); measures detection latency $\Delta t = t_{\text{detect}} - t_{\text{fault}}$; tracks causal hazard aversion under shielded abort and online replanned safe detours; verifies epistemological negative control (`semantic_swap` undetectable by black-box monitor, certified hazardous by private audit). Verified with 7 tests in `tests/test_change_points.py`.
  - Factored Hypothesis Space & Scaling Beyond Enumeration (`crosswire/core.py`): implemented `FactoredCandidateSpace` with orthogonal factor decomposition $\mathcal{P}_I \times \mathcal{P}_O$ and `_LazyAdapters` proxy; evaluates semantic traces once per input factor ($O(N_I)$); prunes output factor space independently via anchors ($O(N_O \cdot |A|)$); achieves 100% mathematical parity against exhaustive `CandidateSpace` on 144 and 720 models; scales to 17,280 models with sub-second pruning (0.0005s) and complete-survivor semantics. Verified with 6 tests in `tests/test_factored_space.py`.
  - Full Test Suite Passing: 344/344 tests passing across 28 test modules.
- [x] **Task 16 (Symbolic Factor-Level Safety/Planning, Realistic Robotics & Protocol Benchmarks, & Workbench Telemetry - Priorities 7, 8 & 9):**
  - Symbolic Factor-Level Safety & Full Method Parity (`crosswire/core.py`): upgraded `FactoredCandidateSpace` to subclass `CandidateSpace` with full method parity (`losses`, `level_ids`, `distinguishing_word`, `choose_probe`, `choose_branching_step`, `ambiguity`, and all 7 `plan` admission modes) plus $O(|\mathcal{I}_{\text{surv}}|)$ symbolic input-factor `probe_is_safe`, `robust`, and `risk_controlled` planning over 17,280 models.
  - Realistic Protocol & Robotics Benchmarks (`crosswire/fixtures.py`, `tests/test_realistic_benchmarks.py`): added `robotics_airlock` (5-state dual-door rover airlock interlock controller) and `protocol_session` (6-state `SYN -> AUTH -> OPEN -> COMMIT` session conformance benchmark) with independently authored table and procedural engines, verified zero-hazard `model_safe` calibration without anchors, out-of-horizon 4-step synthesis, and change-point fault injection. Verified with 7 tests in `tests/test_realistic_benchmarks.py`.
  - Experimental Workbench Upgrades (`crosswire/web/app.js`, `tools/check_workbench.cjs`): exposed `branching` policy, `robotics_airlock` and `protocol_session` benchmarks, factored hypothesis space compression (`active_input_factors × active_output_factors`), and change-point fault detection latency ($\Delta t$) telemetry in the UI; verified end-to-end in headless Chromium.
  - Full Test Suite Passing: 351/351 tests passing across 29 test modules.
