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
  - Causal counterfactual auditing (`crosswire/audit.py`): simulates unshielded trajectory on private target to verify whether the unshielded run would have encountered a hazard, preventing phantom safety attribution and ensuring scientifically honest reporting.
  - Cross-portfolio survey of 95 additional `kai9987kai` repositories (`research/portfolio-index.md`): extracted lessons from `Bot-research-lab`, `Habitat-Genome-Compiler`, `BIOLAB`, `Hybrid-Intel-Studio`, `Italtensor`, and `1313-Game`.
  - Full test suite passing (91/91 passed in 45.08s). Total verified empirical evaluations: 673 runs.
