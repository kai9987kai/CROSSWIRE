# CROSSWIRE priority roadmap

The user's order is the implementation order. This first roadmap phase builds on the existing safe-calibration and tolerance work, then implements public model diagnostics and independent-instance reliability. Later milestones have explicit completion criteria; they are not claimed complete by scaffolding or a synthetic pilot.

| Priority | Milestone | Current phase and completion criterion |
|---|---|---|
| 1 | Safe calibration and active probing | Existing seven-policy pre-query guard; retain regression tests for long witnesses, interrupted attempts, no-safe-action abstention and temporal escalation. Guarantees remain model conditional. |
| 2 | Risk configuration and certification | Existing CLI/API/UI tolerance and independent fraction checks; retain malformed-input and strict-boundary tests. Candidate fractions are not calibrated real-world risk. |
| 3 | Uncertainty and model mismatch | Implement sequential forecasts before observing each output, first refutation witnesses, deterministic-reset conflicts, enabled-class diagnostics, and explicit semantic blind spots. Compatibility must leave inclusion UNKNOWN. |
| 4 | Statistical reliability | Implement versioned generated protocol dynamics, a separate structural instance seed, nuisance-aware parent grouping and conservative finite-sample intervals. Run a reproducible independent-instance pilot with zero-event upper bounds. |
| 5 | Adaptive branching calibration | Completed: interactive within-query action selection (`policy="branching"`); evaluates conditional predictive entropy and model safety under surviving belief at every action dispatch; halts early upon contract readiness; verified with 10 unit tests in `tests/test_branching_calibration.py`. |
| 6 | Online replanning and recovery | Existing finite replanning/recovery remains model conditional. Next: explicit change-point fault schedules, detection latency and recovery success/cost studies, with semantic-only failures as negative controls. |
| 7 | Scale beyond enumeration | Next: lazy symbolic permutation constraints or factored beliefs, checked against exhaustive small-instance baselines. Report time, memory and bounded-search abstention; retain complete-survivor semantics. |
| 8 | Realistic benchmarks | Generated protocol instances are synthetic. Next: external executable protocol conformance harness and robotics simulator adapters with fault injection, recorded versions and independent task-ground-truth audits. Real hardware requires a separate safety boundary. |
| 9 | Dashboard | This phase exposes model inclusion, forecast evidence, structural target seeds and reliability denominators. Later add branching calibration inspection and larger-belief summaries as those mechanisms land. |
| 10 | CI and reproducible releases | Completed: Dual-OS GitHub Actions workflow (`.github/workflows/ci.yml`) on Ubuntu and Windows across Python 3.11 and 3.12, testing automated suite, clean wheel build and install, scientific receipt replay, and headless Playwright Chromium workbench checks. |

## Evidence policy

Keep implementation, local validation, independent target sampling, CI execution and publication distinct. Preserve historical receipt bytes and their source revisions. Never count label seeds or duplicate implementations as independent dynamics. Zero observed hazards must not produce a zero-width safety claim.
