# Safe Calibration Implementation Plan

> **For agentic workers:** Implement independent core, integration, and UI tasks in this session; review the integrated change before completion.

**Goal:** Guard calibration queries under the enabled finite model and make the resulting evidence configurable and inspectable.

**Architecture:** Constrain existing probe selection, preserve separate calibration/deployment accounting, independently check sequential calibration beliefs, and thread new conditions through the existing run/study/receipt interfaces.

**Tech Stack:** Python 3.12+, standard-library runtime, pytest, native JavaScript, Playwright.

**Spec:** `docs/superpowers/specs/2026-10-23-safe-calibration.md`

## Global constraints

- Default unrestricted behavior and the existing source-bound receipt protocol remain available.
- No new runtime dependency. No private audit state enters acquisition or public certificates.
- All scientific claims remain conditional finite synthetic claims.

## Review focus

- Safe selection must filter generated long counterexamples as well as fixed probes.
- Escalation must guard the full enabled model envelope before the first query.
- NaN, infinity, booleans, strings and forged rates must fail certificate validation.
- Scientific comparisons must separate safety/tolerance conditions and handle arbitrary selected policies.
- UI inspection must preserve the original completed receipt for export and replay.

## Tasks

1. Core probe constraints and tolerance validation (core agent)
   - [x] Add failing tests for safe selection across all policies and invalid tolerance.
   - [x] Implement `CandidateSpace.choose_probe(..., safe_only=False)`.
   - [x] Run focused core tests.
2. Config, acquisition, certificate, CLI and study integration (root)
   - [x] Add failing integration and adversarial certificate tests.
   - [x] Add validated `probe_safety` and `risk_tolerance` configuration fields; expose CLI/catalog.
   - [x] Use temporal safety envelope for safe escalation, freeze stopping diagnostics, and independently verify calibration.
   - [x] Extend condition strata and policy contrasts; run focused tests.
3. Workbench controls and study inspection (UI agent)
   - [x] Add safety/tolerance controls, informative evidence, condition labels and run drill-down.
   - [x] Correct adaptive deployment options and extend browser regression checks.
4. Evidence and verification (root plus fresh reviewer)
   - [x] Review combined change; fix demonstrated issues.
   - [x] Run full pytest, browser check, package build and matched study/replay.
   - [x] Update README, research notes and current verification record with bounded claims.
