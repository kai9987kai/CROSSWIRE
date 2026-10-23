# Safe-calibration verification — 23 October 2026

Verified locally on Windows with Python 3.12. No release, push, or deployment is implied.

## Implementation

- Optional model-safe filtering across all seven finite probe policies, including long counterexample witnesses.
- Temporal-envelope guarding before automated class escalation.
- Independent pre-probe safety checks, including interrupted full query words.
- Configured candidate tolerance through CLI/API/UI, strict validation and bound checking, verified reported fractions, and undefined rates for unselected plans.
- Condition-preserving study comparisons and Markdown reports; browser run inspection retains parent receipts.
- Corrected adaptive deployment options, research attribution and guarantee language.

## Automated evidence

`python -m pytest -q --tb=short`: **321 passed in 93.24 seconds** across 25 test modules. This includes 53 safe-probe cases, 28 calibration/certificate integration cases, 12 sequential model diagnostic cases, 10 independent target generator cases, 14 target-cluster reliability cases, and 11 report tests. New boundary tests reproduced both certificate loopholes before their repairs. Independent review identified the implicit epsilon allowance and fictitious abstention rates; both now have passing regression tests.

`node tools/check_workbench.cjs`: passed. Browser checks cover configuration validation, adaptive compatibility, exact study submission, paired output, individual run inspection, parent export, replay/import cancellation, undefined abstention rates, and desktop/mobile overflow. Screenshots in `output/playwright/` were visually inspected, including the 390×900 study inspector viewport.

Python wheel and source archive builds passed. `MANIFEST.in` includes source tools, protocols, documentation and receipts so the source archive retains the report test's dependency. The wheel includes all Python runtime modules and browser assets. Source identity is checked across the checkout and installed wheel.

## Scientific evidence

Two eight-run calibration protocols were generated and each receipt was exactly replayed. Both bind Python source:

`d4e09989ef4899df6cea086aaf315adfb302730b570b3f5d95e573800f9a68d6`

| Protocol | Scientific hash | Result |
|---|---|---|
| Safe | `b86af950532de18711721d2b7303c233c2545c2eff25c87c61367a222bfaffea` | 4 useful completions; 0 hazardous calibration probes; 0 deployment hazards |
| Unrestricted | `3cc08ec4a691fb93e458101c4d31de6eefac03d8da6b9fb6f9f1e200c00fb083` | 6 useful completions; 3 hazardous calibration probes; 2 deployment hazards |

See [research notes](../research/2026-10-23-safe-calibration.md) for the per-family tradeoff, protocols, receipts and primary sources. In-family cases and semantic negative controls remain separate in detailed summaries. Label seeds do not supply independent semantic replications.

## Scope

Safety checking is conditional on enabled finite model inclusion, stationarity, deterministic resets and truthful anchors. Bounded probe exhaustion is not an impossibility proof. Candidate fractions are uniformly weighted model counts, not calibrated probabilities of target harm. Historical receipts require their recorded source revision; their original bytes were preserved.
