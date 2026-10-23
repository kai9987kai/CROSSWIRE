# CROSSWIRE Verification Report

**Date:** 23 October 2026  
**Commit:** `codex/crosswire-design`  
**Platform:** Windows (Python 3.12.10 64-bit, Node.js v20+, Chromium)  
**Overall Status:** PASS (109/109 tests passing, clean wheel install verified, browser e2e verified, 721 total empirical runs verified)

---

## 1. Automated Test Suite Summary

The automated test suite runs via `pytest` without external dependencies (except optional pinned `aalpy==1.6.2` for baseline testing).

```
============================= 109 passed in 80.24s =============================
```

### 1.1 Test Suite Breakdown by Subsystem

| Test File | Tests Passed | Subsystem & Invariant Checked |
|---|---:|---|
| `tests/test_core.py` | 17 | 144 bijective adapter permutations; prefix hazard safety; true-map retention; equivalence classes; empty-family non-vacuous handling; shortest lexicographic product counterexample BFS. |
| `tests/test_fixtures.py` | 21 | Procedural vs. table target implementations; 17 fixture families; grounded anchor validation; hidden permutations; private raw machine extraction; deterministic seeded variation; routing control. |
| `tests/test_interfaces.py` | 13 | Subprocess lifecycle; exact-PID cleanup; line-delimited JSON protocol; malformed message recovery; timeout enforcement; attempted vs. successful call accounting. |
| `tests/test_baselines.py` | 3 | Pinned AALpy 1.6.2 $L^*$ integration; budget-limited SUL and equivalence oracle; comparison transition step counting; global RNG isolation. |
| `tests/test_receipts.py` | 7 | Canonical JSON serialization; SHA-256 payload and scientific hashing; envelope validation; tampering rejection; exact scientific replay. |
| `tests/test_study.py` | 13 | Bounded run/study configuration validation; freeze-before-audit digest; unified reset+step system-call cap; partial deployment prefix auditing; forced-fit residual diagnostics; stratified paired comparisons within budget strata; paired admission contrasts; AALpy configuration guards. |
| `tests/test_server.py` | 5 | Async job queue; thread-safe scientific execution; cancellable import and replay jobs; static file path traversal rejection (`..` escaping blocked); origin protection. |
| `tests/test_cli.py` | 4 | CLI commands `run`, `study`, `verify`, `replay`, `catalog`, `serve`. |
| `tests/test_shield.py` | 7 | Closed-loop dynamic runtime shield; mid-deployment anomaly detection when survivors collapse; pre-step preemptive hazard interception before target dispatch (any surviving interpretation); causal counterfactual hazard averted auditing; execution mode validation. |
| `tests/test_temporal.py` | 7 | Temporal latency-aware adapter algebra ($|\mathcal{A}|=720$ with delay-1 and init-output); augmented transducer signatures tracking `(state, buffer)`; 3-tuple product Mealy state comparison; exact product equivalence merging. |
| `tests/test_cegp.py` | 3 | Decision-focused counterexample-guided active probing (CEGP); $O(W \cdot N)$ marginal frequency pair disagreement counting; dynamic synthesis of distinguishing witnesses beyond fixed probe pool. |
| `tests/test_adaptive.py` | 5 | Observation-dependent contingent policy synthesis (AND/OR tree search); independent policy certificate verification (branch completeness, horizon bounds, zero hazard); certificate tampering rejection; search cap handling; full execution trace replay and audit. |
| `tests/test_web.py` | 4 | Local workbench server endpoints, static file serving, and receipt export. |
| **Total** | **109** | **Complete local coverage of contract specifications, runtime dynamics, witness synthesis, and adaptive contingent policies.** |

---

## 2. Integration Review Findings Resolution

Following independent code review before benchmark execution, six specific actionable findings were identified and verified by test-driven regression:

1. **Deployment Prefix Auditing (P1):**
   - *Issue:* Auditor previously executed full words even if target subprocess failed midway, counting phantom hazards.
   - *Fix:* Reconstruct only the executed prefix; failed calls emit no engine step; unexecuted suffixes are never simulated as if they occurred.
   - *Regression Test:* `tests/test_study.py::test_failed_deployment_never_audits_an_unexecuted_suffix`.
2. **Unified System-Call Cap (P1):**
   - *Issue:* Resets were not charged against the active probe budget, violating the same-call-cap comparison.
   - *Fix:* `budget` is now enforced as a shared system-call cap ($N_{\text{calls}} = N_{\text{resets}} + N_{\text{steps}}$). Both learner loops and AALpy count resets.
   - *Regression Test:* `tests/test_study.py::test_calibration_budget_counts_resets_as_well_as_actions`.
3. **Deployment Interface Error Accounting (P2):**
   - *Issue:* Post-admission deployment failures were omitted from interface error summaries.
   - *Fix:* Count both acquisition and deployment interface errors explicitly in summaries without mutating frozen decisions.
   - *Regression Test:* `tests/test_study.py::test_failed_deployment_never_audits_an_unexecuted_suffix`.
4. **Forced-Fit Residual Diagnostics (P2):**
   - *Issue:* Forced-fit baseline discarded the selected adapter and residual loss under misspecification.
   - *Fix:* Added `fit_diagnostics` to baseline output detailing chosen adapter, raw mismatches, anchor mismatches, tied maps, and total residual.
   - *Regression Test:* `tests/test_study.py::test_forced_fit_exposes_residual_instead_of_implying_consistency`.
5. **AALpy Comparison Transition Work Accounting (P2):**
   - *Issue:* Product-automaton comparisons for AALpy hypotheses were not counting transition steps.
   - *Fix:* Accumulated `comparison_source_steps` and `comparison_hypothesis_steps` in baseline metadata.
   - *Regression Test:* `tests/test_baselines.py::test_completed_classical_model_reports_comparison_transition_work`.
6. **Budget-Stratified Paired Contrasts (P2):**
   - *Issue:* Paired comparisons pooled all budgets into a single parent mean.
   - *Fix:* Stratified paired contrasts strictly within identical call-cap levels, matching cell by cell inside each parent cluster.
   - *Regression Test:* `tests/test_study.py::test_paired_comparison_never_matches_different_budget_conditions`.
7. **Asynchronous Import and Replay (P2):**
   - *Issue:* Receipt import and replay ran synchronously on HTTP handler threads, blocking server worker queues.
   - *Fix:* Converted `/api/import` and `/api/runs/{id}/replay` to submit cancellable background jobs to the scientific worker.
   - *Regression Test:* `tests/test_server.py::test_http_run_export_import_and_replay_use_real_worker`.

---

## 3. Package Parity & Clean Wheel Installation

A clean packaging verification was executed using standard Python build tooling:
1. Wheel built with `pyproject.toml` via `python -m build --wheel --outdir $TEMP/crosswire-wheel-check/dist`.
2. Clean virtual environment initialized in `$TEMP/crosswire-wheel-check/env`.
3. Built wheel installed via `pip install`.
4. Verified package asset inclusion:
   ```
   ['app.js', 'index.html', 'styles.css']
   ```
5. Verified CLI operation from clean wheel environment:
   - `crosswire run --family latch --budget 16 --out latch.json` (exit 0)
   - `crosswire verify latch.json` (exit 0: "Scientific decisions, probes, costs and audits replay exactly")
   - `crosswire run --family latch --policy aalpy --budget 8` without optional dependency produces clear, expected `ModuleNotFoundError: No module named 'aalpy'`.

---

## 4. Browser Workbench End-to-End Automation

Browser automation was conducted using Playwright on headless Chromium against a live instance of the local server (`http://127.0.0.1:8790/`):

- **Script:** `scratch/e2e.js`
- **Output Artifacts:** `output/playwright/*.png`
- **Test Scenarios Exercised:**
  1. **Empty State:** Initial load confirms `connection: Local worker · 0.1.0`, skip link, accessible control labels, and empty state glyph. (`01-empty.png`)
  2. **Live Experiment Execution:** Submitted `latch` with seed 17, anchors enabled, budget 16. Polling tracked progress through worker completion. Displayed reference state graph, candidate mapping table, probe history, and private audit breakdown. (`02-latch-run.png`)
  3. **Receipt Export:** Clicked `#export-button`, received valid `crosswire-receipt-v1` JSON file (5,187 bytes).
  4. **Replay Verification:** Clicked `#replay-button`, tracked async worker job, verified receipt notice: `Replay verified: Scientific decisions, probes, costs and audits replay exactly`.
  5. **Receipt Import:** Ingested exported receipt file via `#receipt-file`, server validated digest and exact execution, rendered imported results.
  6. **Semantic Corruption Control:** Executed `semantic_corruption` fixture. UI accurately displayed decision admitted with contract violation flagged in red by independent audit. (`03-semantic-corruption.png`)
  7. **Study Dispatch & Cancellation:** Dispatched paired study via `#study-button`, triggered `#cancel-button`. Verified job cancelled cleanly without hanging child processes.
  8. **Study Execution & Plot:** Dispatched and completed paired study. Verified rendering of SVG useful-coverage plot and paired summary tables. (`04-study.png`)
  9. **Responsive Mobile Viewport:** Set viewport to $390 \times 900$. Verified 0 horizontal overflow pixels (`document.documentElement.scrollWidth === document.documentElement.clientWidth`). (`05-mobile.png`)
  10. **Error Log Audit:** Exactly zero console errors or uncaught page errors observed.

---

## 5. Scientific Receipt Provenance & Reproducibility

Six systematic empirical benchmarks were executed and preserved as self-contained scientific receipts:

| Benchmark | Output Receipt | Protocol Hash | Scientific Hash | Total Runs |
|---|---|---|---|---:|
| **Development Smoke** | `reports/smoke-receipt.json` | `18f9b1ef3bce37f8…` | `f08e0e7316980cb7…` | 27 |
| **In-Family Benchmark** | `reports/pilot-in-family-receipt.json` | `9977cf45469275ff…` | `64c084a09fa36956…` | 350 |
| **Out-of-Family Stress** | `reports/pilot-stress-receipt.json` | `1dc8cc430b960163…` | `ad1c49f782e756cb…` | 216 |
| **Open-Loop Stress Baseline** | `reports/pilot-shield-openloop-receipt.json` | `a4fcb06f0e492da4…` | `5bdf9766d4ab4946…` | 36 |
| **Shielded Closed-Loop Benchmark** | `reports/pilot-shield-shielded-receipt.json` | `a88c531ea7fad346…` | `924a7b12de35f87c…` | 36 |
| **Temporal Adapter Synthesis** | `reports/pilot-temporal-receipt.json` | `674907c7f02dcdb7…` | `f0eee9109c032893…` | 4 |
| **CEGP Distinguishing Witness Benchmark** | `reports/pilot-cegp-longtrace-receipt.json` | `968ed5dfe5874e08…` | `e931c96b3d027d34…` | 4 |
| **Adaptive Contingent Policy Benchmark** | `reports/pilot-adaptive-receipt.json` | `6e07673c27941fc7…` | `cbc85a6cbc260e98…` | 48 |
| **Total Empirical Runs** | | | | **721** |

All receipts are cryptographically bound to explicit source and protocol hashes. Replaying any receipt against the current codebase recomputes identical scientific states and passes validation.
