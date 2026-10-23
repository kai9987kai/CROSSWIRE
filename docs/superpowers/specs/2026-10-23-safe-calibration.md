# Model-safe calibration and inspectable evidence

## Intent

Extend the existing CPU-local Python laboratory so safety evidence covers calibration actions as well as admitted deployments. Keep the existing unrestricted experiment available as a matched control. The user authorized a whole-project improvement; these implementation choices are the agent's proposals within that scope.

## Approach and alternatives

Adding another acquisition heuristic would leave calibration hazards unaddressed. Guarding only deployment is already implemented. Choose a model-safe constraint around every existing finite probe policy, plus an independent sequential evidence check, configurable candidate-fraction admission, and usable study inspection.

## Required behavior

- `probe_safety` is `unrestricted` (default) or `model_safe`. Before a safe-mode query, all actions in its full word must avoid the contract hazard under every currently evidence-compatible adapter. Lack of such a probe causes conservative stopping without target calls.
- Safety is conditional on the finite model, deterministic resets, stationarity, and truthful anchors. It is not proof about unknown semantics. Private negative controls remain necessary.
- With automated escalation enabled, safe acquisition uses the complete enabled temporal envelope from the first query. Refuting the initial static acquisition class must not retrospectively invalidate safety checks.
- AALpy safe calibration is rejected explicitly because its internal query generator is not guarded.
- Independent certificates recompute pre-probe survivors and check every dispatched probe word, including the unexecuted suffix of an interrupted attempt, without CandidateSpace caches. A decision binds a public calibration stopping reason; do not describe bounded probe exhaustion as impossibility.
- `risk_tolerance` is a finite numeric value in [0,1), excludes booleans, defaults to zero, and positive values require `risk_controlled` admission. Rates are exact fractions over uniformly weighted surviving models, not calibrated target hazard probabilities. Certificates bind tolerance to configuration and compare all reported rates against independently recomputed rates.
- Studies keep safety mode and tolerance in their condition strata; pair every available method within identical scientific conditions and admission rule. Maintain existing task-relative contrast signs.
- Workbench adds the two controls, explanatory safety evidence, readable study conditions and individual run inspection. Adaptive deployment cannot offer the unsupported replanning mode.
- Existing receipts retain their source identities; do not overwrite historical evidence after code changes.

## Validation

Test all probe policies, no-safe-probe abstention, truthful anchors, temporal escalation envelope, malformed certificate tolerances, tampered rates, interrupted probes, study separation and policy contrasts. Run the full suite, browser flow at desktop/mobile sizes, package build, and a small matched calibration-safety study with exact receipt replay. Report finite synthetic findings only.
