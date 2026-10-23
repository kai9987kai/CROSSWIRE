# Resilient Model Escalation, Entropy Probing & Simplex Recovery Plan

**Goal:** Implement Shannon entropy active learning, autonomous hypothesis class escalation, and Simplex recovery runtime shielding.
**Architecture:** Standard Python 3.12 library, strict subprocess isolation, pre-freeze hashing, post-freeze private audit.
**Spec:** `../specs/2026-10-23-resilient-escalation.md`

## Tasks

- [ ] **1. Information-Theoretic Active Probing (`entropy`):**
  - Add `entropy` to `POLICIES` in `crosswire/core.py`.
  - Implement Shannon entropy computation over predictive observation distributions in `choose_probe`.
  - Add unit tests in `tests/test_cegp.py` or new `tests/test_escalation.py` verifying entropy calculations and deterministic tie-breaking.
- [ ] **2. Autonomous Model-Class Escalation:**
  - Add `escalate: bool = False` to `RunConfig` in `crosswire/study.py`.
  - Support automatic transition $\mathcal{H}_0 \to \mathcal{H}_1$ in `_acquire` when $\mathcal{V}_{\mathcal{H}_0} = \emptyset$.
  - Re-evaluate historical transcripts against $\mathcal{H}_1$.
  - Record escalation metadata (`escalations`, `escalation_level`, `structural_complexity`) in decision and metrics.
  - Implement `StructuralContradictionCertificate` when both $\mathcal{H}_0$ and $\mathcal{H}_1$ are refuted.
  - Test on `delay` fixture (escalates from static to temporal and succeeds) and `alias` (proves structural contradiction).
- [ ] **3. Simplex Safe Fallback & Recovery Shielding (`recovery`):**
  - Add `"recovery"` to `EXECUTION_MODES` in `crosswire/study.py` and `crosswire/shield.py`.
  - Implement recovery action search and safe dispatch in `RuntimeShield.step`.
  - Audit recovery actions in `crosswire/audit.py` to ensure recovery steps are counted and checked against hazards.
  - Test on `alias` and `delay` to verify clean recovery and `RECOVERED_SAFE_FALLBACK` status.
- [ ] **4. Workbench UI & CLI Integration:**
  - Expose `entropy` in policy options and `recovery` in execution mode options.
  - Add `escalate` checkbox in `crosswire/web/index.html` and `crosswire/web/app.js`.
  - Render escalation badges and recovery status cards in run inspection.
- [ ] **5. Empirical Benchmark & Verification:**
  - Create `configs/pilot-escalation.json` benchmarking static vs escalated vs recovery runs.
  - Execute study to produce `reports/pilot-escalation-receipt.json` and `reports/pilot-escalation.md`.
  - Verify receipt bit-exact replay.
  - Run full test suite (`pytest -q`) ensuring all existing and new tests pass.
- [ ] **6. Documentation & Ledger Update:**
  - Update `docs/paper.md`, `docs/verification.md`, `README.md`, and `docs/build-ledger.md`.
