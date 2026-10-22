# CROSSWIRE

**A proposed CPU-local laboratory for behavioral interoperability under ambiguous interfaces.**

Research question: when can finite observations justify connecting independently implemented systems with unknown action and observation meanings, and when must the connector preserve ambiguity or decline the connection?

The candidate mechanism keeps every interface interpretation consistent with observed behavior. It permits a bounded task only if all remaining interpretations permit it; otherwise it probes or abstains. Its value must be measured in useful coverage and evidence cost, with explicit tests of harmful connections when its assumptions fail.

## Current status

The research review and first-build design are prepared for review. No application, implementation tests, CROSSWIRE experiments or release have been created yet. The 26 linked repositories were inspected live at pinned commits; their historical experiments were not rerun. This is a new project in `C:\Users\kai99\Desktop\CROSSWIRE`, separate from NEUROGRAFT.

- [First-build design](docs/superpowers/specs/2026-10-22-crosswire-design.md): mechanism, exact assumptions, baselines, interface, evaluation and falsification.
- [All 26 repositories](research/portfolio-index.md): complete coverage and pointers to detailed source reviews.
- [Recent research and foundational prior art](research/recent-research.md): primary sources, publication dates and what they change in the design.
- [Model/search portfolio review](research/portfolio-models.md).
- [Synthetic-laboratory portfolio review](research/portfolio-labs.md).
- [Systems and interoperability portfolio review](research/portfolio-systems.md).

## First build proposed

A finite-state CPU core, independently implemented target modules, ambiguity-preserving adapters, actual competing baselines, an exact private auditor, raw experiment receipts, CLI study/replay and a local browser inspector. Begin with deterministic stationary interfaces. Treat delay, drift and missing semantics as explicit stress conditions before extending the supported model.

The portfolio already covers memory transfer, neural grafts, causal assays, shared program libraries and evidence ledgers. CROSSWIRE's selected object is the justification for a task-specific connection through an unknown interface. Adapter synthesis, active learning and abstention have substantial prior art; no global novelty or breakthrough is claimed. A reproducible negative result is a valid research outcome.
