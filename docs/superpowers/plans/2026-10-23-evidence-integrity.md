# Evidence integrity implementation plan

1. Add failing tests and independent `crosswire.certificates.check_result(result)`. Enumerate adapters separately from `CandidateSpace`, replay public traces, verify candidate completeness and robust word/tree safety, and extract deletion-minimal contradiction cores. Attach the generated certificate before freezing the decision.
2. Correct `RuntimeShield` recovery with adversarial regression tests: no action after model collapse, no hazardous fallback, no horizon overflow, response verification, reliable cancellation/error reporting.
3. Correct audit prefixes/catalog limits, cumulative escalation counters, condition-stratified summaries and exact-cell paired comparisons. Reject ambiguous duplicate comparison cells.
4. Wire browser study controls and adaptive compatibility, expose evidence/conditions, repair receipt job lifecycle/export errors, and add CLI `check` without duplicating replay.
5. Review integrated changes, run the full suite and browser checks, create and replay fresh small research receipts, build/install a wheel, and update README, paper and verification report with measured results and limits.

Parallel ownership: root owns certificates/integration/documentation; engine agent owns shield/tests; evidence agent owns audit and analysis; workbench agent owns UI/server/CLI. No publication or unrelated changes are required.
