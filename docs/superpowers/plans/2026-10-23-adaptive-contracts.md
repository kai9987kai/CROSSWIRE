# Adaptive Contracts Implementation Plan

**Goal:** Verify and execute observation-dependent finite policies with measured fixed-plan controls.
**Architecture:** Public-only bounded AND/OR search, independent tree checking,
monitored execution, then private post-freeze audit. Existing static APIs remain.
**Tech Stack:** Python 3.12+, standard library, existing vanilla browser UI.
**Spec:** ../specs/2026-10-23-adaptive-contracts.md

## Global constraints

CPU-local; no external target calls, model downloads or new runtime dependencies.
Horizon 1–6. Deterministic search, hard node cap, explicit unresolved outcomes.
No private fixture fields in synthesis or certificate verification.

## Review focus

Missing or extraneous branches fail verification; empty beliefs cannot certify.
Temporal raw outputs and current semantic hazards use different time indices.
Unexpected responses halt before the next action; failed steps retain observed prefix.
Incomplete adaptive policies have no single fixed counterfactual suffix.
Paired analyses must retain execution mode and temporal class in their strata.

## Tasks

- [ ] Add regression tests, then fix temporal signatures and any-survivor shield guards.
- [ ] Test and implement adaptive.synthesize_policy(space, ids, node_limit=20000, cancel=None),
  verify_policy(space, ids, policy), and execute_policy(target, policy, space, ids, cancel=None).
  Test all branches, corrupted trees, no survivors, search caps, delay and pre-dispatch checks.
- [ ] Add routing table and independent procedural implementation; compare complete bounded traces.
- [ ] Integrate admission, acquisition stopping, freeze, execution, private audit and replay.
  Test fixed/adaptive routing contrast, fault path accounting and unsupported combinations.
- [ ] Render policy/certificate/path, temporal mappings and separate risk/cost domains in UI.
- [ ] Freeze a small paired pilot and controls after source changes stop; save receipt/report,
  replay it, run full pytest, build wheel and inspect browser at desktop/mobile sizes.
- [ ] Update README, paper, verification and research lineage with bounded measured claims.
