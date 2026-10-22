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
- **Strict Process Boundary:** Opaque targets run in isolated subprocesses communicating over line-delimited JSON. Every reset and step attempt is metered against a shared system-call cap.
- **Freeze-Before-Audit Protocol:** Scientific decisions, survivor counts, and probe histories freeze into cryptographic digests before private semantic evaluation.
- **Classical Learning Baseline:** Pinned integration with AALpy 1.6.2 ($L^*$ algorithm) under identical target interaction budgets.
- **Cryptographic Scientific Receipts:** Every run and study generates self-contained JSON receipts with source hash bindings and exact determinism checking.
- **Local Browser Workbench:** Dark-mode responsive UI featuring live state graph inspection, candidate mapping matrices, probe timelines, receipt export/import, and SVG study coverage charts.

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
# Run a single experiment
crosswire run --family latch --budget 16 --anchors --out reports/latch.json

# Verify and replay a scientific receipt
crosswire verify reports/latch.json

# Execute a paired empirical study
crosswire study --config configs/pilot-in-family.json --out reports/my-study.json

# Inspect available fixture families
crosswire catalog
```

---

## Empirical Benchmark Findings

In a 566-run systematic evaluation across 16 synthetic fixture environments:

1. **Zero Selective Harm (In-Family):** Across 350 runs on in-family mechanisms, robust consensus admission achieved **0% selective harm** and **0 hazards**. Whenever a connection was admitted, it was 100% successful.
2. **Task-Relevant Probing Efficiency:** Contract-relevant active probing achieved **71.4% useful coverage** in an average of only 7.4 calls (at budget 16), significantly outperforming fixed sequential probing (9.7 calls).
3. **Classical System Identification Bottleneck:** Under small call caps ($B \le 32$), classical automata learning (AALpy $L^*$) requires 100–250 queries for full state identification and thus abstains entirely (0% coverage). CROSSWIRE's task-directed ambiguity reduction solves the task with an order-of-magnitude fewer interactions.
4. **Falsification & Honest Negative Controls:** Under semantic corruption (where sensor outputs match raw predictions but underlying physical events are swapped), black-box consensus admitted connections that failed private auditing (100% harm). This rigorously demonstrates that ungrounded behavioral observation cannot substitute for semantic anchors.
5. **Forced-Fit Catastrophe:** Forced-fit point estimation (`fit`) admitted 33.3% of misspecified stress cases but incurred **62.5% selective harm**, proving the necessity of ambiguity preservation over single-point optimization.

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
