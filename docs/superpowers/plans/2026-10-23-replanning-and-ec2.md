# Plan: Receding-Horizon Dynamic Replanning, EC2 Active Probing, and Risk-Controlled Version-Space Admission

## Phase 1: EC2 Active Probing Policy (Test-Driven Development)
1. Author `tests/test_ec2.py`:
   - Test EC2 class partitioning and distance weighting.
   - Test that EC2 cuts cross-class edges and assigns zero score to intra-class divisions.
   - Test probe selection when full consensus already exists (empty/null handling).
   - Test that EC2 achieves goal admission in fewer queries than uniform random on ambiguous fixtures (`latch`, `rotary`).
2. Implement EC2 in `crosswire/core.py`:
   - Add `ec2` branch in `choose_probe`.
   - Update `crosswire/study.py` `POLICIES` to include `"ec2"`.
3. Verify all EC2 tests pass.

## Phase 2: Receding-Horizon Dynamic Replanning Shield
1. Author `tests/test_replan.py`:
   - Test that `replan` mode detects upcoming plan hazard or dead-end under updated survivors.
   - Test that `replan` discovers and adopts a verified safe alternative suffix if one exists within remaining horizon.
   - Test that execution successfully completes the goal along the replanned path (`REPLANNED_ONLINE_SAFE`).
   - Test that if no safe replan exists, `replan` mode falls back to conservative recovery or safe halt without executing hazards.
   - Test that private audit correctly verifies executed prefix and awards goal success when the replanned path reaches the goal.
2. Implement `replan` in `crosswire/shield.py`:
   - Add `replan` to valid modes in `RuntimeShield`.
   - Implement `_find_safe_suffix(self, prefix, remaining_horizon)`.
   - In `step()`, attempt online replanning before halting or falling back.
   - Track `replanned`, `replan_count`, `replan_events` in deployment record.
   - Register `"replan"` in `crosswire/study.py` `EXECUTION_MODES`.
3. Verify all replan tests pass.

## Phase 3: Risk-Controlled Version-Space Admission
1. Author `tests/test_risk_controlled.py`:
   - Test empirical version-space hazard and goal calculation across candidate words.
   - Test that `risk_controlled` with $\epsilon = 0.0$ matches `robust` consensus.
   - Test that `risk_controlled` with positive $\epsilon$ allows admission when a dominant majority of models agree.
   - Test certificate validation in `crosswire/certificates.py` under `risk_controlled`.
2. Implement `risk_controlled` in `crosswire/core.py` and `crosswire/certificates.py`:
   - Add `risk_controlled` in `CandidateSpace.plan` and `crosswire/study.py` `ADMISSIONS`.
   - Attach risk metrics to decision dictionary.
3. Verify all risk-controlled tests pass.

## Phase 4: Workbench UI & Browser Regression
1. Update `crosswire/web/app.js` and `crosswire/web/index.html`:
   - Add label mappings for `ec2`, `replan`, `risk_controlled`.
   - Add replanning indicators and badge in the deployment view.
   - Add interactive Minimal Contradiction Core rendering when model contradictions occur.
2. Update `tools/check_workbench.cjs` to test `ec2` and `replan` modes in Playwright.
3. Run `node tools/check_workbench.cjs` and verify clean pass.

## Phase 5: Empirical Benchmarking & Verification
1. Run a comparative empirical study comparing EC2 vs Task vs Entropy vs Disagreement, and Replan vs Shielded vs Open-Loop.
2. Save receipt and update documentation in `docs/paper.md`, `docs/verification.md`, `README.md`, and `docs/build-ledger.md`.
3. Run full pytest suite (all 158+ tests passing).
4. Build clean wheel.
5. Clean git commit.
