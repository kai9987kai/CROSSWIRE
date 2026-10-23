# CROSSWIRE: Behavioral Interoperability Under Ambiguous Black-Box Interfaces

A CPU-local research laboratory and experimental benchmark for learning and verifying interface adapters between independently developed systems under unknown action and observation mappings.

---

## Overview

When independently developed controllers, agents, or tools communicate without a shared semantic schema, how can they safely connect?

**CROSSWIRE** formalizes this interface synthesis problem using finite-state Mealy transducers. Rather than choosing a single "best-fit" mapping, CROSSWIRE preserves the entire set of candidate adapters consistent with observed behavior. A task deployment plan is admitted if and only if it satisfies a public safety contract under **all** surviving interpretations; otherwise, it actively probes or abstains.

```
                    ┌────────────────────────┐
                    │ Public Reference Model │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │ Candidate Adapter Space│  (144 Bijection Pairs)
                    │  V(D) Surviving Maps   │
                    └───────────┬────────────┘
                                │ (Consensus Plan / Active Probe)
                    ┌───────────▼────────────┐
                    │    Process Boundary    │  (Subprocess JSON Protocol)
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │    Opaque Target       │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │ Independent Audit      │  (Post-Freeze Ground Truth)
                    └────────────────────────┘
```

---

## Key Capabilities & Architecture

- **Consensus Admission vs. Point Estimation:** Eliminates selective harm by verifying safety across all candidate mappings.
- **Autonomous Model-Class Escalation (SRM):** Implements Structural Risk Minimization across nested hypothesis spaces $\mathcal{H}_0 \subset \mathcal{H}_1$. Starts at parsimonious static bijections (144 models) and autonomously escalates to temporal latency-aware models (720 models) upon refutation, emitting unforgeable structural contradiction certificates if all nested classes fail.
- **Information-Theoretic Active Probing (Shannon Entropy):** Probing policy that maximizes output predictive entropy $H(O \mid w)$ per query cost, identifying valid adapters in up to 50% fewer target interactions.
- **Simplex Safe Fallback Recovery Shielding:** Dynamically monitors execution step-by-step; upon detecting observation anomaly or impending hazard, dispatches a verified minimum-hazard recovery action to restore the system to a safe baseline state (`RECOVERED_SAFE_FALLBACK`).
- **Adaptive Contracts (Observation-Dependent Policies):** Extends interface synthesis from linear words to contingent AND/OR policy trees certified by an independent tree checker (Proof-Carrying Code). Chooses each action based on the observed response, achieving 100% useful coverage on routing interlocks without prior calibration.
- **Closed-Loop Dynamic Runtime Shielding:** Actively monitors intermediate target responses step-by-step; detects behavioral anomalies/drift and preemptively averts latent hazards before irreversible actions are committed.
- **Temporal / Latency-Aware Adapter Algebra:** Expands the adapter candidate space to 720 models supporting stateful pipeline delays ($d \in \{0, 1\}$) and initial buffer search, enabling verified connections to asynchronous interfaces.
- **Counterexample-Guided Active Probing (CEGP):** Optimized $O(W \cdot N)$ active exploration selecting probes that maximize pairwise disagreement across candidate models.
- **Strict Process Boundary:** Opaque targets run in isolated subprocesses communicating over line-delimited JSON. Every reset and step attempt is metered against a shared system-call cap.
- **Freeze-Before-Audit Protocol:** Scientific decisions, survivor counts, and probe histories freeze into cryptographic digests before private semantic evaluation.
- **Classical Learning Baseline:** Pinned integration with AALpy 1.6.2 ($L^*$ algorithm) under identical target interaction budgets.
- **Cryptographic Scientific Receipts:** Every run and study generates self-contained JSON receipts with source hash bindings and exact determinism checking.
- **Local Browser Workbench:** Dark-mode responsive UI featuring live state graph inspection, candidate mapping matrices, probe timelines, dynamic shield badges, receipt export/import, and SVG study coverage charts.

---

## Quickstart

### Installation

Requires Python 3.12+.

```bash
# Clone or navigate to the directory
cd C:\Users\kai99\Desktop\CROSSWIRE

# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install in editable mode with baseline dependencies
pip install -e ".[baselines,dev]"
```

### Running the Interactive Browser Workbench

Start the local server and open the browser:

```bash
crosswire serve --port 8781 --open
```

Or run the convenient PowerShell launcher:

```powershell
.\Run-CROSSWIRE.ps1
```

### Command-Line Interface

```bash
# Run a single experiment with shielded deployment and temporal synthesis
crosswire run --family delay --temporal --execution_mode shielded --budget 16 --out reports/delay.json

# Run counterexample-guided active probing (CEGP)
crosswire run --family latch --policy counterexample --budget 16 --out reports/cegp.json

# Verify and replay a scientific receipt
crosswire verify reports/delay.json

# Execute a paired empirical study
crosswire study --config configs/pilot-shield-shielded.json --out reports/shielded-study.json

# Inspect available fixture families
crosswire catalog
```

---

## Empirical Benchmark Findings

In a 757-run systematic evaluation across 17 synthetic fixture environments:

1. **Autonomous Escalation & Shannon Entropy Efficiency:** In a 36-run benchmark (`reports/pilot-escalation-receipt.json`), Shannon entropy active probing resolved valid adapters in **4.5 mean calls** on `latch` compared to 8.5 for `task` and 9.0 for `fixed` (nearly 50% query savings). On pipeline-delayed targets (`delay`), fixed probing stalled and failed (0% coverage), while autonomous escalation promoted the hypothesis space to $\mathcal{H}_1$ and achieved successful connection. On unconnectable targets (`incompatible`), the engine certified structural contradiction across all candidate classes.
2. **Simplex Safe Recovery:** In the presence of runtime anomalies during deployment, Simplex recovery shielding intercepted the divergence, safely dispatched a verified minimum-hazard fallback action, and averted impending hazards with zero safety violations.
3. **Adaptive Contracts vs. Open-Loop Stalling:** On the designed `routing` interlock control, fixed non-branching sequences suffered 0% admission at budget zero because commit actions depend on the unknown input map. Adaptive policy synthesis certified an observation-dependent policy tree that achieved **100% useful coverage at budget zero without requiring any prior target interactions**, delivering a **+0.500 mean useful coverage advantage** on in-family fixtures (`[+0.000, +1.000]`).
4. **Zero Selective Harm (In-Family):** Across in-family mechanisms, robust consensus admission achieved **0% selective harm** and **0 hazards**. Whenever a connection was admitted, it was 100% successful.
3. **Task-Relevant Probing Efficiency:** Contract-relevant active probing achieved **71.4% useful coverage** in an average of only 7.4 calls (at budget 16), significantly outperforming fixed sequential probing (9.7 calls).
4. **Dynamic Anomaly Interception & Causal Hazard Deflection:** In stressful out-of-family environments, the **Closed-Loop Dynamic Runtime Shield** intercepted unexpected behavioral divergences across 8 deployment runs. Causal counterfactual auditing verified that where unshielded plans ran into catastrophic absorbing hazards (`alias` and `delay`), the shield preemptively deflected both hazards with zero harm.
5. **Temporal Adapter Synthesis:** On asynchronous interfaces with pipeline latency (`delay`), static bijections suffered 0% admission due to transition contradictions. Enabling temporal adapter synthesis expanded the search space to 720 models and achieved **100% useful coverage with 0% selective harm**.
6. **Decision-Focused CEGP Distinguishing Witnesses:** On deep mechanisms (`long_trace`) where fixed-horizon length-3 probes left candidate adapters indistinguishable (forcing 0% admission), Counterexample-Guided Active Probing (CEGP) dynamically synthesized the 4-step distinguishing witness `[0, 0, 0, 0]`, achieving **100% useful coverage** (+1.000 mean paired difference).
7. **Classical System Identification Bottleneck:** Under small call caps ($B \le 32$), classical automata learning (AALpy $L^*$) requires 100–250 queries for full state identification and thus abstains entirely (0% coverage). CROSSWIRE's task-directed ambiguity reduction solves the task with an order-of-magnitude fewer interactions.
8. **Falsification & Honest Negative Controls:** Under semantic corruption (where sensor outputs match raw predictions but underlying physical events are swapped), black-box consensus admitted connections that failed private auditing (100% harm). This rigorously demonstrates that ungrounded behavioral observation cannot substitute for semantic anchors.
9. **Forced-Fit Catastrophe:** Forced-fit point estimation (`fit`) admitted 33.3% of misspecified stress cases but incurred **62.5% selective harm**, proving the necessity of ambiguity preservation over single-point optimization.

---

## Documentation & Research

- [Standalone Research Paper](docs/paper.md): Comprehensive theoretical formulation, experimental methodology, empirical tables, and epistemological bounds.
- [Verification Report](docs/verification.md): Full test suite results, packaging verification, Playwright browser test logs, and receipt hashes.
- [Pre-Implementation Design Specification](docs/superpowers/specs/2026-10-22-crosswire-design.md): The approved design specification.
- [Portfolio Research & Prior Art Reviews](research/portfolio-index.md): Source code reviews and commit hashes of all 26 related repositories.
- [Recent Research Context](research/recent-research.md): Representation stitching, active automata learning, and interface theory context.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
