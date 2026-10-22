# CROSSWIRE build ledger

Approved design: 22 October 2026. Baseline commit `3a7385b`. User explicitly approved building in the new standalone folder.

Ruling: execute the implementation plan without another approval round — the direct “Approve—build CROSSWIRE” instruction authorizes implementation — routine implementation choices remain reviewable in Git.

Ruling: retain the standalone checkout rather than create another worktree — the user's named new project folder is the intended work location — no existing NEUROGRAFT source/checkpoint is part of this build.

Ruling: parallelize disjoint core, target-protocol and browser files — active multi-agent instructions favor independent work and each worker has exclusive paths — root owns integration and commits; shared interfaces are fixed in implementation-contract.md.

## Preflight interface scan

| Tasks | Produced/consumed boundary | Finding |
|---|---|---|
| 1 / 2 | Machine serialization used by fixture references/audit models | fixed tuple cells and integer opaque symbols |
| 1 / 3 | CandidateSpace predictions/plans/ambiguity and exact product comparison | fixed methods and counters, root does not introspect private target |
| 2 / 3 | Case public/private and TargetProcess query/step/reset/costs | public-only learner input, audit after freeze |
| 3 / 4 | Run results, receipt exports and async job status | fixed HTTP and result schema |
| 4 / 5 | CLI/package/web assets | root verifies wheel and actual browser workflows |
| 1 | Algebra tests versus core implementation | excludes empty-family vacuous admission and prefix hazards |
| 2 | Fixture independence versus runtime | procedural branch cannot read reference transition table |
| 3 | Exact guarantees versus finite evidence | conditional soundness; misspecification/semantic corruption explicit |
| 4 | UI versus core | visualizes Python output, no duplicated scientific learner |
| 5 | Research conclusion versus software status | negative pilot permitted; no breakthrough/publication claim |

## Progress

- Planning and shared API: prepared.
- Implementation, task reviews, pilot, package and browser checks: pending.
