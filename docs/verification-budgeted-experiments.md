# Budgeted experiments verification — 2026-11-02

This increment adds public-model lookahead calibration, independent experiment-tree checking and a selectable factored runtime. The research basis and limits are recorded in [the dated synthesis](../research/2026-11-01-budgeted-experiments.md). Validation and exploratory study outcomes are filled in from completed runs below; this is local evidence, separate from hosted CI or publication.

## Implemented behavior

- `candidate_backend=flat|factored` is supported through runs, bounded study grids, CLI, HTTP catalog, workbench, safety envelopes, escalation and the optional classical baseline's candidate processing. Flat remains the default. Backend conditions stay separate in summary, reliability, paired and report tables.
- Factored predictions now cache consistently and reject invalid/bool IDs before cache lookup. Survivor export avoids iterating every lazy adapter. Actual pre-audit backend telemetry labels structural ratios as structure, not measured memory compression. Exhaustive public checking and private audit still limit end-to-end scale.
- Robust factored admission uses bounded/cancellable product-state breadth-first search over active input factors. Goal outputs are checked before visited-state pruning. Search caps yield SEARCH_LIMIT; incomplete results are not cached as impossibility proofs. Other admission modes still evaluate finite word sets exhaustively.
- Default task probing aggregates exact rational Jaccard separation over contract classes. It no longer constructs every candidate pair. `pair_checks` denotes represented pairs, not primitive histogram operations. Exact ties can differ from historical floating summation artifacts.
- Lookahead proposes depth-two, reset-separated trees from length-1..3 probes. Root and branch choices obey the acquisition call cap. Whole-tree ranking preserves alternatives until the global maximum unresolved belief is known; a reproduced 18-model counterexample verifies the coupled score. The deterministic expansion cap is 2,048 states; incomplete searches retain a complete proposal or a one-query fallback.
- A separate checker reconstructs static/temporal models, evidence, branch guards, complete response coverage, readiness words and reset/action costs. Runtime dispatches only the checked root, then replans from actual observations. The final public checker reconstructs each proposal using evidence preceding that query. Search execution/completeness metadata and actual target calls require the distinct exact-replay check; public checking does not authenticate them.
- Workbench controls expose policy/backend selection and report actual backend data, planning limits, finite-model readiness and independent tree-check metrics. Hypothetical response branches are not empirical observations or calibrated target probabilities.
- Worker initialization has its own bounded ten-second default deadline, separate from the unchanged two-second per-call default. Cold interpreter/module startup is not counted as a reset/action. A deliberately slow worker regression verifies that startup can complete while a later over-deadline reset still fails, is charged and closes only its owned child.
- Profiling the temporal control exposed redundant response validation and temporary tree construction. The final planner reuses bitset response partitions, memoizes readiness by semantically identical input wiring and materializes only the selected descriptor. Candidate multiplicities remain intact, and the independent checker still reconstructs the complete family. Static/temporal regressions and an exact 720-model objective check cover this optimization.

## Validation record

The final frozen-source full suite passed **666 tests in 245.51 seconds**. Focused regressions cover exact pairwise-score agreement, invalid cached IDs, product-state horizon/limit/cancellation behavior, adversarial tree certificates, backend strata, actual guarded acquisition, startup deadlines and UI/API defaults. Thirty additional one-off comparisons against an independent exhaustive depth-two oracle matched the planner's scores. The 720-model temporal regression also matches independently reconstructed objective values: 720 ready models, zero largest unresolved belief, terminal-square sum 1,536 and worst-case acquisition cost eight.

Independent integrated reviews found no remaining Important issue in the final planner, backend boundaries or recorded outcomes. Review findings repaired during implementation included a globally coupled branch objective and an undefined UI selection variable. Validation phases ran serially after concurrent cold-start contention exposed the need for separate initialization deadlines.

- All **44 new study rows** passed independent public-model checking and exact source-bound replay. All **22 matched backend configurations** agree on probes, decisions, survivors, deployment and audited outcomes. Prototype behavioral projections were preserved across the planner optimizations; their owning source snapshot remains in the local scratch archive.
- Actual factored static-to-temporal escalation and optional AALpy paths both passed public checking and exact replay. Their final decisions were UNRESOLVED at 15/16 and 8/8 acquisition calls respectively; this verifies workflow integration, not successful task admission.
- The clean outside-checkout installed wheel matched the checkout's Python source and all three web asset hashes. It executed a factored zero-acquisition routing/adaptive deployment in five deployment calls, plus a real two-call factored lookahead query with independently checked planning evidence; both replayed exactly.
- Real Chromium workbench verification passed native/default controls, actual factored lookahead runs and studies, export, per-run inspection, import/cancel behavior, exact replay, model diagnostics and 390-pixel responsive layouts. Final desktop/mobile screenshots were visually inspected. The harness uses the correct Playwright wait-option argument and captures failure screenshots plus server job state.
- Historical tracked receipt bytes remain unchanged. The wheel and source archive include the required modules/assets and new evidence/documentation respectively. Archive inspection and `git diff --check` passed.

Python source identity: `1004a81c28c2969b59ced6684b6178f474d3d12787a73614c2a6a0ccc7ea76f2`. The isolated package check separately binds web assets; scientific receipt source identity covers Python modules. Local logs and the aggregate validation record are under `output/budgeted-*`. This records local validation; no new hosted CI result or publication is claimed.

| Frozen study receipt | Runs | Scientific hash |
|---|---:|---|
| [budgeted-experiments](../reports/budgeted-experiments-receipt.json) | 8 | `98174018871db37abcb2fc43b9db6c16f81a541ae8bbb555c0e2320020a6bc58` |
| [budgeted-planning-pilot](../reports/budgeted-planning-pilot-receipt.json) | 24 | `5ad3444a94d76c0f470415bc07217662f917550b0ff6a91281110fc8ee41d379` |
| [budgeted-planning-controls](../reports/budgeted-planning-controls-receipt.json) | 12 | `665df2a920dd3e685abaa82309e05a334fe756e93f56db4a66aa42c86e96d0da` |

Each receipt retains its complete protocol, source, envelope and scientific identities. The generated Markdown reports deliberately label their own digest-only rendering scope; the independent checking and replay above are separate completed operations.

## Exploratory outcomes

The guarded generated-target pilot found **no useful-coverage improvement**: all three methods succeeded on zero of two parents at cap four and one of two at cap eight. Per backend, lookahead used mean acquisition calls 3.5 versus 3.0 at cap four, and 6.0 versus 7.0 at cap eight. There were no recorded calibration or deployment hazards in this 24-row pilot. Two parents leave wide intervals; backend repetitions do not enlarge that denominator.

The unrestricted latch smoke succeeded with lookahead at cap four while entropy abstained, at the cost of one hazardous calibration probe per lookahead run. In the temporal controls, latch and delay succeeded under both methods, while all four semantic-corruption runs were admitted and hazardous. Across the 44 rows there were 20 admissions, 16 successful deployments, four semantic-corruption deployment hazards and 12 hazardous calibration probes. Thirty proposals were recorded and none reported incomplete search; capped-search behavior is covered separately by regressions.

See [the dated research synthesis](../research/2026-11-01-budgeted-experiments.md#observed-exploratory-results--2-november-2026) for the method/cap table, negative controls and interpretation.

## Reproduce

Run `python -m pytest -q --tb=short`, `python -m build --wheel --sdist`, `python -I tools/check_distribution.py --wheel-dir dist` and `node tools/check_workbench.cjs` from the checkout. Optional baseline tests require the pinned `baselines` extra; browser checks require Playwright Chromium.

For each of `budgeted-experiments`, `budgeted-planning-pilot` and `budgeted-planning-controls`, run `python -m crosswire study --config configs/NAME.json --out output/NAME-receipt.json`, then `python -m crosswire check output/NAME-receipt.json` and `python -m crosswire verify output/NAME-receipt.json`. `NAME` is the selected study name. Preserve the source revision when replaying an older receipt.

## Scientific scope

The generated-target pilot was fixed before execution at two structural seeds, one nuisance label, caps 4/8, three policies and two backends. Its 24 runs cannot establish a broad statistical advantage. The separate 12-run controls include latency and raw-equivalent semantic corruption, with unrestricted calibration hazards reported separately. See saved protocols and receipt hashes for exact conditions.

Model-safe guarantees remain conditional on target inclusion, stationarity, deterministic reset and truthful semantic anchors. Observable compatibility leaves inclusion UNKNOWN. Error-aware pruning and recoverability-preserving exploration were reviewed but not implemented because they require additional trusted-error or backup-controller assumptions. Semantic corruption remains an explicit negative control.

Historical receipt bytes are preserved. New source-bound evidence uses new filenames. Larger-alphabet utility checks are not larger-alphabet runtime evidence. No new theorem, global novelty, calibrated real-world risk or deployment reliability is claimed. Hosted CI status belongs to a specific published commit and is separate from these local checks.
