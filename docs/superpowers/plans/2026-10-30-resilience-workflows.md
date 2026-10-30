# Resilience Workflows Implementation Plan

> **For agentic workers:** Use focused subagents for disjoint tasks and review the integrated diff. Steps use checkbox syntax for tracking.

**Goal:** Make controlled runtime-fault studies usable and preserve trustworthy certification and evidence through every interface.

**Architecture:** Retain the current Python scientific runtime and local JavaScript inspector. Centralize experimental condition identity; integrate fault settings through the existing run/study boundary. Correct the independent private audit rather than altering acquisition to use private fault knowledge.

**Tech Stack:** Python 3.11+, pytest, vanilla JavaScript/CSS, existing Playwright checks.

**Spec:** `docs/superpowers/specs/2026-10-30-resilience-workflows-design.md`.

## Global constraints

- Dependency-free runtime; Python 3.11+; no new remote services.
- Preserve historical receipt bytes and strict source-bound replay/import.
- All safety and equivalence claims remain conditional on declared finite models.
- Keep fault schedules out of public learner state and admission decisions.

## Review focus

- Implicit/default fault settings must not create duplicate effective conditions.
- Nominal and faulted rows must not match or pool in any analysis surface.
- Calibration-only faults must not be simulated as deployment faults during auditing.
- Same-action/different-observation policy leaves must retain distinct beliefs.
- Historical report digest checks must not falsely imply replay against current source.

### Task 1: Correct finite certification utilities

Files: `crosswire/adaptive.py`, `crosswire/shield.py`, `crosswire/core.py`, focused tests.

- [x] Reproduce same-action observation leaves, soft-return horizon overrun and emitted fifth output failures.
- [x] Correct leaf identity, strict return bounds and contract symbol validation.
- [x] Run focused adaptive, shield, core and factored tests.

### Task 2: Preserve report integrity

Files: `crosswire/receipts.py`, `tools/report.py`, `tests/test_receipts.py`, `tests/test_report.py`.

- [x] Add failing tests for corrupted envelopes and legitimate historical source identities.
- [x] Expose source-independent envelope integrity validation; retain strict existing replay checks.
- [x] Make report rendering verify complete receipts and label the verification scope.
- [x] Verify report and receipt regressions.

### Task 3: Complete controlled fault studies and audit

Files: `crosswire/conditions.py`, `study.py`, `reliability.py`, `fixtures.py`, `audit.py`, report condition plumbing, tests.

- [x] Add regression tests for invalid schedules, duplicate defaults and fault-stratum isolation.
- [x] Add `fault_schedules` study dimension and canonical condition identity.
- [x] Export actual deployment models with capped onset counters and correctly audit calibration phases.
- [x] Verify actual faulted study export, public checking and exact replay.

### Task 4: Complete workbench fault configuration

Files: `crosswire/web/index.html`, `app.js`, `styles.css`, `tools/check_workbench.cjs`.

- [x] Add accessible optional fault controls and truthful zero-based phase help.
- [x] Propagate settings into runs, study previews and paired study requests.
- [x] Render schedule conditions clearly and test controls, actual fault runs and preserved nominal defaults.

### Task 5: Verify and document the release

Files: README, roadmap, paper corrections, new verification report, configs/receipts, CI package checks.

- [x] Run full pytest on frozen Python source and integrated browser checks.
- [x] Generate new named current-source smoke receipts and replay them; preserve historical files.
- [x] Build wheel/sdist and check installed imports/assets/source identity from outside the checkout.
- [x] Review integrated changes and record exact local validation and remaining limits.
