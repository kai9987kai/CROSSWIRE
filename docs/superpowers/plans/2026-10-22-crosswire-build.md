# CROSSWIRE Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task by task. Steps use checkbox syntax for tracking.

**Goal:** Build and verify the approved CPU-local behavioral interoperability laboratory, including real baselines, reproducible raw studies and a browser inspector.

**Architecture:** A Python finite-model core operates only on public reference/contracts and raw target traces. A subprocess owns target implementation and private semantics; a separate audit runs only after decisions freeze. The CLI and loopback web server share the same study and receipt implementation.

**Tech stack:** Python 3.12, standard-library runtime, AALpy 1.6.2 optional pinned baseline, pytest, browser-native HTML/CSS/JavaScript. No model downloads or GPU.

**Spec:** `docs/superpowers/specs/2026-10-22-crosswire-design.md` (approved 22 October 2026).

## Global constraints

- Work only in `C:\Users\kai99\Desktop\CROSSWIRE`, the new independent project.
- Three inputs, four outputs, 144 bijective adapters; initial probe words have lengths 1-3, deployment words 1-H with default H=4.
- Each deployment word starts from reset and executes completely without early stopping; candidate mappings remain fixed across steps.
- Public reference and task are available to the learner; target states/maps/private semantic events are unavailable during acquisition/admission.
- Preserve empty-family handling and semantic ambiguity; no universal safety, novelty or biological claim.
- All source, target, probe, baseline and audit costs are distinguished and actual failed calls are counted.
- Statistical resampling uses underlying semantic parent instance clusters, not permutations/contracts/implementations as independent samples.
- No upstream source/weights/data/assets copied. No external publication is part of this build.

## Review focus

- Malformed/slow target response: bounded failure, charged attempted calls, no blocked UI or stranded child.
- No surviving maps: do not admit by vacuous all-candidate agreement.
- Semantically corrupted but raw-equivalent target: expose the limitation; audit actual semantics, never inverse-map emitted symbols into truth.
- Cancel/import/replay: incomplete results cannot be imported as completed evidence, and cancel cannot kill unrelated processes.
- Repeated contracts/implementations: preserve a common parent ID in summary/resampling; never inflate independent sample counts.

## Ownership and interfaces

The exact shared API and HTTP payload decisions are in `docs/implementation-contract.md`. Each implementer owns only its assigned files and tests. Root integrates and commits. Parallel workers may implement disjoint tasks after reading that contract; no worker changes another worker's files. This is a deliberate adaptation to the active multi-agent instructions and a new repository with no pre-existing product code.

### Task 1: finite model, mappings, probes and admission

Files: `crosswire/core.py`, `tests/test_core.py`.

- [ ] Write failing tests for 144 maps, prefix hazard, true-map retention, unique versus task-equivalent ambiguity, non-vacuous empty family and exact product counterexamples.
- [ ] Observe failure with `python -m pytest tests/test_core.py -q`.
- [ ] Implement the core contract with validated finite immutable tuples, memoized predictions, work counters, task-agnostic and contract-relevant probe scores, robust/one-best/unique/fit/identity/abstain admission.
- [ ] Verify targeted tests, then run the available full suite. Report deterministic behavior and cost-accounting checks.
- [ ] Independent review of core semantics and tests before final integration.

### Task 2: target fixtures and bounded subprocess protocol

Files: `crosswire/fixtures.py`, `crosswire/target_worker.py`, `crosswire/interfaces.py`, `tests/test_fixtures.py`, `tests/test_interfaces.py`.

- [ ] Write failing tests for separately implemented table/procedural traces, hidden action/output maps, symmetric semantic ambiguity, neutral-map ambiguity, semantic corruption, aliasing, long separating traces, malformed protocol and timeout cleanup.
- [ ] Observe failures before implementation.
- [ ] Implement `Case`, public/private separation, case catalog, target engines, private evaluation and finite audit-model exports. Procedural engines must not interpret a shared transition table at runtime.
- [ ] Implement exact-PID subprocess lifecycle with line-delimited JSON, init/reset/step, response validation, bounded timeout, counted failures and context-manager cleanup.
- [ ] Verify targeted and available full tests, including child exit. Source snapshot and private target identity cannot affect learner-facing observations except through the documented interface.
- [ ] Independent review of privacy data flow, boundary handling and semantic ground truth.

### Task 3: study orchestration, AALpy baseline, audit and receipts

Files: `crosswire/study.py`, `crosswire/baselines.py`, `crosswire/audit.py`, `crosswire/receipts.py`, `tests/test_study.py`, `tests/test_receipts.py`, `tests/test_baselines.py`.

- [ ] Write failing tests for zero-budget admission, common transcript comparisons, deterministic replay, true-map containment, actual semantic harm, exact no-map-in-class, empty-result risk, tampering and parent-cluster summaries.
- [ ] Observe failures; implement acquisition with exclusive call accounting and freeze scientific decision before private audit.
- [ ] Implement AALpy 1.6.2 raw Mealy learning using budget-limited SUL/oracle access, with no uncharged model finish. Complete models undergo adapter equivalence search and the same task admission; incomplete learning abstains.
- [ ] Implement receipt canonical hashes, deterministic scientific projection, import validation and exact scientific replay. Runtime measurements remain outside deterministic identity.
- [ ] Implement method-by-family summaries, parent-cluster paired bootstrap, utility at recorded abstention costs and exploratory pilot runner; incomplete/cancelled runs cannot be passed as complete.
- [ ] Verify targeted/full tests and compare core private auditor with direct enumerated tiny fixtures. Record any scope rulings.

### Task 4: CLI, async job server and browser inspector

Files: root owns `crosswire/__main__.py`, `crosswire/cli.py`, `crosswire/server.py`, `tests/test_cli.py`, `tests/test_server.py`; web worker owns `crosswire/web/index.html`, `crosswire/web/styles.css`, `crosswire/web/app.js`.

- [ ] Write failing API/CLI tests for run/export/import/replay, bounded input, async status, cancel, loopback static serving and errors.
- [ ] Implement shared CLI commands `run`, `study`, `verify`, `replay`, `serve`; one queued worker in server and stable HTTP contract.
- [ ] Implement responsive browser workbench from the shared contract: task settings, module diagrams, candidate maps, probe/counterexample timeline, decision/outcome separation, study plots, cancel/import/export/replay.
- [ ] Verify CLI/API tests; browser automation must exercise real run, cancel, export/import and replay. Inspect actual screenshots and repair errors/overflow/empty states.

### Task 5: reproducible pilot, documentation and package parity

Files: `configs/pilot.json`, `configs/smoke.json`, `README.md`, `docs/paper.md`, `docs/verification.md`, `Run-CROSSWIRE.ps1`, `pyproject.toml`, `LICENSE`, `reports/`.

- [ ] Run development smoke to establish run cost and sample variability. Freeze an explicit exploratory pilot config/source hash before executing the pilot.
- [ ] Run paired methods on the same semantic parent instances; preserve raw rows and receipts, source/config hashes, actual baselines, failure counts, conditional and total coverage/harm, and cluster intervals.
- [ ] Write operational docs and standalone paper reporting measured results honestly, including negative outcomes and supported versus out-of-family assumptions.
- [ ] Build wheel, install in a clean temporary environment, execute the same CLI fixture/receipt replay and confirm web assets are included.
- [ ] Run full tests, artifact/link checks and fresh whole-project review; fix actionable findings, rerun checks justified by fixes, commit the completed local build, launch and verify responsive browser workbench.

## Execution decisions

The user's explicit answer was “Approve—build CROSSWIRE.” That authorizes executing this plan; no additional permission loop is introduced. The new standalone folder is already the isolated project requested by the user, so implementation stays there rather than creating a second checkout in another location. Research-review commits form the clean baseline.
