# Resilience workflows and trustworthy evidence

The requested project-wide improvement will complete the existing resilience workflow across configuration, studies, analysis, workbench and release checks. This is an implementation choice under the user's broad improvement request, not a new research hypothesis.

## Approach

Three useful directions emerged from the current code: integrate the standalone factored solver, make historical evidence inspectable, or finish controlled resilience experiments. The selected increment completes resilience experiments and repairs demonstrated evidence/certification bugs. Factored runtime integration and an archival dashboard remain later work; historical reports must still validate their saved digests.

## Behavior

- Run fault schedules reject unknown keys, phases and invalid stuck sensor symbols before execution.
- Study protocols accept a bounded `fault_schedules` dimension, including `null` nominal controls. Effective duplicates are rejected. Each schedule remains a separate condition in summaries, paired comparisons, reliability estimates, reports and dashboard labels.
- The workbench configures an optional fault type, zero-based onset step, phase and stuck output. Runs and previewed paired studies send exactly those settings.
- Private equivalence uses the actual deployment-phase dynamics and a finite fault-onset counter. Calibration hazard accounting uses calibration-phase semantics.
- Policy information metrics distinguish complete raw-observation paths. Soft-return searches obey the remaining contract horizon. Contract acceptance supports nonnegative semantic symbols beyond the original four-symbol fixture alphabet.
- Reports verify envelope and scientific digests independently of the current source revision; replay/import remain source-bound. Saved receipts are preserved byte-for-byte.

## Constraints and validation

Keep the existing dependency-free runtime, Python 3.11+ floor, loopback server, finite-model assumptions, semantic-swap negative control, exact replay and freeze-before-audit boundary. No deployment reliability or new scientific advantage is claimed. Regression tests precede fixes; final validation covers the full suite, browser controls and export/replay, a fresh small fault study, isolated wheel installation and asset/source parity. Existing source-bound receipts remain historical after Python changes, and receive newly named replacements for current release checks.
