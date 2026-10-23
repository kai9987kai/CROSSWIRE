# Observation-dependent contract deployment

## Intent and design choice

Extend the CPU-local finite laboratory from a fixed admitted word to a bounded,
observation-dependent policy. The user's broad improvement request authorizes
implementation; this concrete design is the implementation choice made here.

Three approaches were considered: more probe ranking heuristics (incremental),
safe acquisition alone (valuable but does not increase expressiveness), and
robust contingent deployment (chosen because a response can justify a different
next action without fully identifying the interface). Preserve fixed plans as
the matched baseline. Do not claim general reactive synthesis or real-world safety.

## Contract

A policy is an action node with one child per possible raw output, or a stop
leaf. Every action prefix must avoid the semantic hazard for every surviving
adapter. Every leaf must satisfy the goal for every adapter consistent with its
observations, within the existing horizon (1–6). Empty beliefs never certify a
policy. Search uses deterministic iterative deepening and a hard expansion cap;
exhausting the cap is unresolved, not an impossibility proof.

An independent traversal checks the policy against the public model and exact
survivor IDs before deployment. The frozen decision binds the tree, certificate,
and evidence before private auditing. Execution always monitors responses and
stops on a missing branch or model contradiction. Temporal predictions include
the output buffer; physical hazard checks use current semantic events.

## Experiment and interface

Add an independently authored table/procedural routing fixture: three harmless
diagnostic actions precede a commit stage. The correct commit action depends on
the unknown input map. At horizon four a contingent policy can identify and use
that action; no common fixed word works without calibration. This is a designed
positive control, not independent evidence of broad superiority. Existing
semantic-corruption, alias, delay and other fixtures remain falsification cases.

Expose adaptive admission through CLI/server/workbench, render the response tree
and actual path, retain temporal candidate metadata, and make the study button
honor selected settings. Report acquisition and deployment costs/hazards
separately. Policy comparisons are paired within the same configuration and
semantic parents; label permutations are not independent mechanisms.

## Correctness repairs and limits

Fix temporal observational signatures and conservative shield preconditions.
Reject the unsupported AALpy-plus-temporal configuration instead of silently
running a static candidate class. Correct stale empirical prose. Existing
receipts remain historical and require their original source revision.
All guarantees are conditional on stationary deterministic targets, valid
reset, truthful anchors, and inclusion of the target in the candidate family.
Acquisition remains a sandbox experiment and can encounter hazards.
