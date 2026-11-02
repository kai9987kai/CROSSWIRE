# Budgeted Experiments Implementation Plan

> **For agentic workers:** Implement focused disjoint tasks, then independently review the integrated result. Use test-first regressions and preserve the declared scientific scope.

**Goal:** Add independently checked bounded experiment planning and an actually usable factored runtime backend.

**Architecture:** A public-only experiment synthesizer emits a proposed query tree. A separate checker re-enumerates models and validates it. One backend factory routes existing solver workflows; shared conditions keep experimental designs separate.

**Tech stack:** Python 3.11+, standard library, pytest, vanilla JavaScript and existing Playwright tooling.

**Spec:** `docs/superpowers/specs/2026-11-01-budgeted-experiments-design.md`.

## Global constraints

- No new runtime dependency, private learner information or changed target call accounting.
- Keep existing flat backend default, finite runtime alphabet limits and strict source-bound replay.
- Search caps mean incomplete search, not negative proofs.
- Preserve historical receipts; publish new evidence under new names.
- Uniform candidate readiness is a finite planning objective, not a calibrated real-world probability.

## Review focus

- Hypothetical branch safety uses that branch's belief and all enabled temporal models.
- Missing/extra response branches, unsupported ready leaves and reset costs are independently checked.
- Adapter IDs stay canonical and reject bool aliases before cache lookup.
- Backend conditions never silently pool; backend telemetry is actual, not inferred from labels.
- A saturated search or non-informative bank produces an honest incomplete/unresolved result.

### Task 1: Factored solver and construction

Files: `crosswire/core.py`, new `crosswire/backends.py`, dedicated backend utility tests.

- [x] Reproduce quadratic task allocation, duplicate prediction accounting and bool adapter-ID cache bug.
- [x] Implement exact contract-class task scoring; check against a pairwise Fraction oracle.
- [x] Fix caching, strict IDs and implement backend factory/telemetry.
- [x] Add bounded/cancellable factored robust product search and utility parity/limit tests.

### Task 2: Independent experiment-tree checking

Files: new `crosswire/experiment_checks.py`, dedicated certificate tests.

- [x] Re-enumerate static/temporal models and filter complete observed prefixes independently.
- [x] Validate tree shape, safety, response partitions, ready leaves, depth and total reset/action costs.
- [x] Return independently derived metrics and a content binding; exercise adversarial tampering and empty/refuted beliefs.

### Task 3: Public experiment synthesis and runtime

Files: new `crosswire/experiments.py`, `study.py`, `baselines.py`, `certificates.py`, `conditions.py`, integration tests.

- [x] Implement depth-two bounded tree search and deterministic fallback, recording exact expansion scope.
- [x] Thread backend selection through every construction and study grid; export only survivor IDs.
- [x] Dispatch root queries only after independent checking; recheck recorded trees from pre-probe evidence.
- [x] Verify policy/backends/guarded escalation/fault controls, source freeze and replay.

### Task 4: User workflows

Files: CLI, server catalog, web controls/labels/planning display, report conditions and browser tests.

- [x] Expose backend and lookahead with clear finite-model objective and search-limit labels.
- [x] Propagate the exact settings to runs/studies and all analysis displays.
- [x] Verify actual factored lookahead run/study/export/replay and nominal defaults.

### Task 5: Research evidence, review and delivery

- [x] Save dated research synthesis distinguishing source results from this adaptation.
- [x] Run a bounded exploratory policy/backend comparison; preserve negative results.
- [x] Freeze Python source, run full tests, browser checks, public checker, exact replay and installed-wheel verification.
- [x] Resolve independent review findings and document actual validation, performance scope and remaining limits.
