# Portfolio review: model, search and neural-system repositories

Review date: 22 October 2026. Reviewer inspected each repository through the connected GitHub plugin, resolved its default branch to a commit, read the README and selected implementation/configuration/results files at that commit. This is source inspection, not independent reproduction or exhaustive auditing. No source repository, weights, dataset or running process was changed.

## Pinned inventory

| Repository | Observed identity | Default branch | Commit |
| --- | --- | --- | --- |
| [NexusSearch](https://github.com/kai9987kai/NexusSearch) | NexusSearch 0.2 | `main` | `538edcba595889090946a51ce03f72ac9fb72202` |
| [prometheus-alpha](https://github.com/kai9987kai/prometheus-alpha) | Prometheus-alpha 0.7.0 | `claude/epic-tesla-l7brlx` | `417009e5548453338761732152b7b8ec30ffa79a` |
| [morpheus](https://github.com/kai9987kai/morpheus) | Morpheus 0.3.0 | `claude/zealous-euler-y2xqul` | `5db6f98d605b80245ed9ff5e2cc9d42151830a14` |
| [Supermix-Expanse-v2](https://github.com/kai9987kai/Supermix-Expanse-v2) | Supermix Expanse v2 repository (v4/mixture continuation line) | `main` | `33e38a279c86bccdb1e5680f15f193d61a3f71cb` |
| [Supermix-expanse](https://github.com/kai9987kai/Supermix-expanse) | Supermix Expanse (v1-v3 line) | `main` | `3fd091e9cc3387b2c17da5ce7514831d77e2af44` |
| [supermix-archimedes](https://github.com/kai9987kai/supermix-archimedes) | Supermix Archimedes (supermix-archimedes-v1) | `main` | `1952cf1c92cb506fff60f9ee0c055c2365988e5e` |
| [Supermix](https://github.com/kai9987kai/Supermix) | Supermix monorepo (README through v90; mixed generations) | `main` | `6ea1c2cc41e3705b4b899b764a001cec180d155d` |
| [QuantumBot](https://github.com/kai9987kai/QuantumBot) | QuantumBot 3.0 | `main` | `42e4fd637da2df1da5241da484ebc2c625050e72` |
| [Supermix-Poseidon](https://github.com/kai9987kai/Supermix-Poseidon) | Supermix Poseidon 3.8.0 | `main` | `72d42218ae92cee5c9668a090f9d31d8d9961681` |

## Per-repository evidence

### 1. NexusSearch 0.2

**Implemented mechanism:** Implemented snapshot search over local JSON: exact int64 numeric filters, scanned BM25/text operations, exhaustive cosine vectors and deterministic reciprocal-rank fusion. The core source computes document-wide BM25 statistics and explicitly accumulates every eligible vector score. Standalone graph ANN, postings and quantization modules are separate experiments, not the active query engine.

**Evidence inspected:** README explicitly distinguishes active and experimental paths; nx_search.c contains the BM25 reference scanner, cosine loop and result-path execution counters. [Pinned README](https://github.com/kai9987kai/NexusSearch/blob/538edcba595889090946a51ce03f72ac9fb72202/README.md), [core source](https://github.com/kai9987kai/NexusSearch/blob/538edcba595889090946a51ce03f72ac9fb72202/src/engine/nx_search.c).

**Strongest reusable lesson:** An exact reference engine and observable execution path make attractive approximations falsifiable; a module's existence does not establish its use.

**Limits and aspiration boundary:** No embeddings included; snapshot lexical/vector paths scan; local HTTP interface has no authentication/TLS. ANN advantage, durability and other compiler/platform behavior require separate evidence. This review did not build it or reproduce benchmarks.

**Overlap to avoid:** Another local search/index wrapper or claiming ANN from unused source files.

**Missing question worth testing:** Can two retrieval modules with matching schemas but incompatible score/order semantics be composed without silently changing the meaning of downstream thresholds?

### 2. Prometheus-alpha 0.7.0

**Implemented mechanism:** A 1-D neural cellular automaton has head-gated cues, broadcast shock, local learned updates and fixed voltage diffusion. Rule parameters remain frozen during a life; learned associations live in cell state. The v7 trainer makes matched turnover/noise/control siblings, with held-out stress measurements.

**Evidence inspected:** The tissue step multiplies cue inputs by the living-head gate and the response averages the response channel only over head tissue. README and results/v7.json distinguish causal stress training from the earlier post-hoc robustness correlation. [Pinned README](https://github.com/kai9987kai/prometheus-alpha/blob/417009e5548453338761732152b7b8ec30ffa79a/README.md), [core source](https://github.com/kai9987kai/prometheus-alpha/blob/417009e5548453338761732152b7b8ec30ffa79a/src/prometheus/tissue.py), [additional implementation](https://github.com/kai9987kai/prometheus-alpha/blob/417009e5548453338761732152b7b8ec30ffa79a/src/prometheus/train_v7.py).

**Strongest reusable lesson:** Decodable state is not necessarily used state. Private codes can transfer the opposite meaning; matched causal implants and held-out behavioral tests reveal this where a representation probe alone cannot.

**Limits and aspiration boundary:** Synthetic selected rules, tiny constructed bodies and explicit training objectives. Repository findings are not animal-memory or consciousness evidence. v7 receipts record a historical run/source identity; this review inspected them without rerunning training or confirmatory experiments.

**Overlap to avoid:** Regeneration memory, hidden-state implants, memory compilers, lineage stress robustness or a new synthetic worm lab.

**Missing question worth testing:** When an independently trained receiver admits several equally compatible interpretations of a donor's state, can it preserve that ambiguity until a discriminating behavioral probe exists?

### 3. Morpheus 0.3.0

**Implemented mechanism:** A regenerating 2-D NCA combines voltage diffusion, learned per-cell forward prediction and intervention controls. Source implements naive benchmark reuse, fresh-sample LORD++ gating, and sequential e-process/e-LOND adoption with a separate auditor and frozen anchor. The compiler optimizes phased voltage maps through regeneration on training tissues.

**Evidence inspected:** run_loop has independent proposal/fresh-suite/auditor streams and records believed versus actual gain; compiler.py implements tail-focused multi-start programs. The committed eaudit result contains per-seed adoption/outcome data. [Pinned README](https://github.com/kai9987kai/morpheus/blob/5db6f98d605b80245ed9ff5e2cc9d42151830a14/README.md), [core source](https://github.com/kai9987kai/morpheus/blob/5db6f98d605b80245ed9ff5e2cc9d42151830a14/src/morpheus/rsi.py), [additional implementation](https://github.com/kai9987kai/morpheus/blob/5db6f98d605b80245ed9ff5e2cc9d42151830a14/src/morpheus/compiler.py).

**Strongest reusable lesson:** Keep selection evidence separate from a never-consulted auditor, and test whether the intended mechanism survives after a transient intervention ends.

**Limits and aspiration boundary:** Small number of evolved rules, artificial anatomy and priors; no biological validation. README says the compiled head is largely not retained after re-amputation. Statistical labels concern the implemented synthetic protocol and are not universal self-improvement guarantees.

**Overlap to avoid:** Another online-FDR self-edit gate, independent auditor ledger, own-versus-yoked prediction error assay or anatomical intervention compiler.

**Missing question worth testing:** Can an experiment planner recognize that its available interventions cannot distinguish two competing rule interpretations, even when both improve the measured endpoint?

### 4. Supermix Expanse v2 repository (v4/mixture continuation line)

**Implemented mechanism:** Extends the Expanse graft architecture with a configurable CNS laboratory, causal per-position FlyCore writes, input-evoked readouts, deterministic source-mixture sampling/resume, donor-preserving continuation and a frozen semantic-generation diagnostic. The repository contains distinct historical v1-v4 experiments and later controls.

**Evidence inspected:** The graft hook dispatches component writes; causal fly code never pools future positions. SourceSampler binds local RNG and packed-row order. MIXTURE_STUDY.md records two completed 80-update arms: balanced dev loss improved 0.319%, but parent/natural/balanced each scored 4/72 strict final answers and neither candidate was promoted. [Pinned README](https://github.com/kai9987kai/Supermix-Expanse-v2/blob/33e38a279c86bccdb1e5680f15f193d61a3f71cb/README.md), [core source](https://github.com/kai9987kai/Supermix-Expanse-v2/blob/33e38a279c86bccdb1e5680f15f193d61a3f71cb/expanse/src/expanse_core.py), [additional implementation](https://github.com/kai9987kai/Supermix-Expanse-v2/blob/33e38a279c86bccdb1e5680f15f193d61a3f71cb/expanse/src/source_sampler.py).

**Strongest reusable lesson:** Loss improvements and extra architecture can leave generated behavior unchanged. Remove constant-bias shortcuts and compare matched mechanisms before attributing a gain to biological wiring or donor knowledge.

**Limits and aspiration boundary:** Short one-seed continuation, 320 row exposures per arm; strict formatting also affects the 4/72 score. Real wiring did not beat degree-preserving shuffles in the recorded protocol. An older supported CNS verdict is now inconclusive under stricter cohort hashes. Composite model/data restrictions differ from code licensing.

**Overlap to avoid:** Another source-mixture/semantic-diagnostic toolkit, connectome adapter or model-graft collection.

**Missing question worth testing:** Can a module interface be admitted by behavioral counterexamples when functional fit alone is high but semantic permutations remain unresolved?

### 5. Supermix Expanse (v1-v3 line)

**Implemented mechanism:** A custom PyTorch language trunk integrates donor MoE experts, frozen Omni encoders, a simulated FlyCore and a full type-level male CNS sparse recurrent branch. Source implements causal per-token FlyCore evaluation, component gates, donor slot wake schedules, cached generation and model-specific checkpoint loading.

**Evidence inspected:** README records a 132.6M combined model, weak held-out donor mapping fits, v2 consolidation ablation and v3 tokenizer/data comparisons. The inspected core contains the actual graft dispatch and per-position sensing, not a generic weight average. [Pinned README](https://github.com/kai9987kai/Supermix-expanse/blob/3fd091e9cc3387b2c17da5ce7514831d77e2af44/README.md), [core source](https://github.com/kai9987kai/Supermix-expanse/blob/3fd091e9cc3387b2c17da5ce7514831d77e2af44/expanse/src/expanse_core.py).

**Strongest reusable lesson:** A preserved branch or transplanted neuron group is not demonstrated capability transfer. v2's gain mostly survived disabling its new blocks, exposing extra training as the explanation.

**Limits and aspiration boundary:** v3 generation table reports 0% code-pass/PubMedQA in its small held-out sets; 128-token single-turn context. Biomedical performance regressed. The graft/teacher line has inherited model/data license restrictions. No current weight download, remote model-hash verification or evaluation execution was performed here.

**Overlap to avoid:** A larger merger with more named subsystems, connectome claims without shuffled controls or loss-only transfer claims.

**Missing question worth testing:** Which adapter invariances are necessary for a donor to preserve its behavior in a receiver, and when can no adapter in the chosen family do so?

### 6. Supermix Archimedes (supermix-archimedes-v1)

**Implemented mechanism:** Fits ridge maps on shared token embeddings to lift 256-d v87 experts into a 320-d v93 trunk; installs dormant experts; ports 22-role FlyCore, adds heuristic CNS nodes and retains independent Omni classification/image branches through gates. The source contains the actual linear solves, expert transformations and trunk hooks.

**Evidence inspected:** LiftMaps.fit solves regularized least squares and records fit R2. FlyCore.sense actually mean-pools hidden positions despite its stale last-position docstring; Expanse later identifies and fixes the resulting causal issue. README records build logit difference 0.3197, a 47.6M architecture and a 44/48 small checkable probe. [Pinned README](https://github.com/kai9987kai/supermix-archimedes/blob/1952cf1c92cb506fff60f9ee0c055c2365988e5e/README.md), [core source](https://github.com/kai9987kai/supermix-archimedes/blob/1952cf1c92cb506fff60f9ee0c055c2365988e5e/archimedes/src/archimedes_core.py).

**Strongest reusable lesson:** Point-estimate alignment needs causal and held-out behavioral checks. Inspect code rather than relying on comments, architecture diagrams or successful loading.

**Limits and aspiration boundary:** Small house-style probe is not broad generalization; image decoder is natively 64x64 and classifier labels lack semantic names. Graft abstractions are not a faithful fly brain. README's no-license paragraph is stale: the pinned tree contains an MIT LICENSE; upstream checkpoint terms still need separate checking.

**Overlap to avoid:** Shared-token ridge lifting, dormant expert schedules or a multi-branch integration demo as the central novelty.

**Missing question worth testing:** Can multiple plausible cross-system maps remain live until a targeted behavioral test rules them out, instead of selecting the lowest regression-error map?

### 7. Supermix monorepo (README through v90; mixed generations)

**Implemented mechanism:** Large mixed source/package/training workspace. Inspected implementations include bounded deterministic answer verification, evidence-class answer admission/abstention, receipts that bind a request/output/nonce, and canonical causal-scenario tooling. Many model generations, native text models, desktop apps and training/promotion controls coexist.

**Evidence inspected:** verifiable_reasoning.py uses parsing/Decimal/Fraction/strict JSON and oracle-checked logical metadata rather than executing candidate text. nexus_epistemics.py keeps internal scores separate from calibrated correctness. nexus_causal_dag.py handles preset equations; its backdoor helper only finds direct common parents. [Pinned README](https://github.com/kai9987kai/Supermix/blob/6ea1c2cc41e3705b4b899b764a001cec180d155d/README.md), [core source](https://github.com/kai9987kai/Supermix/blob/6ea1c2cc41e3705b4b899b764a001cec180d155d/source/verifiable_reasoning.py), [additional implementation](https://github.com/kai9987kai/Supermix/blob/6ea1c2cc41e3705b4b899b764a001cec180d155d/source/nexus_epistemics.py).

**Strongest reusable lesson:** Route exact closed-world authority through an appropriate verifier and make the limits machine-readable. Keep native-model evidence distinct from retrieved/solved output and packaged-runtime behavior.

**Limits and aspiration boundary:** Selected-file review only; 131k-character README contains both careful experimental boundaries and broad architecture claims. The inspected causal helper is not general identification/do-calculus. Passing solver checks do not establish learned reasoning, and the runtime/promotion machinery cannot validate arbitrary scientific claims.

**Overlap to avoid:** Another proof/receipt ledger, exact solver wrapper, untrained latent 'thought' demo or architecture name collection.

**Missing question worth testing:** Can an interface validator reject semantically incompatible components despite passing each local verifier, and expose a minimal cross-component counterexample?

### 8. QuantumBot 3.0

**Implemented mechanism:** NumPy statevector/density-matrix simulation of small variational circuits drives evolving agents. Implements repeated input encoding, noise, configurable entanglement, parameter-shift analysis and multi-seed paired benchmarks against classical policies. SimulationConfig's shipped default is one layer, no entanglement, plus state and sign-neutral output initialization.

**Evidence inspected:** CircuitEngine runs batched quantum gates and computes tanh-transformed observables. benchmark.py uses paired seeds, bootstrap summaries and paired comparisons. README's result table has circuit 91.7 versus linear 94.3 (no demonstrated difference), and entanglement hurts this task. [Pinned README](https://github.com/kai9987kai/QuantumBot/blob/42e4fd637da2df1da5241da484ebc2c625050e72/README.md), [core source](https://github.com/kai9987kai/QuantumBot/blob/42e4fd637da2df1da5241da484ebc2c625050e72/quantumbot/quantum.py), [additional implementation](https://github.com/kai9987kai/QuantumBot/blob/42e4fd637da2df1da5241da484ebc2c625050e72/quantumbot/benchmark.py).

**Strongest reusable lesson:** The simplest competitive baseline and matched initialization/budget matter more than an impressive mechanism label; test whether communication is listened to rather than merely emitted.

**Limits and aspiration boundary:** Classical 2-6-qubit simulations with gradient-free evolution; no hardware or quantum-advantage evidence. Reported benchmarks are small and scenario-specific. This review did not execute tests, Qiskit checks or benchmark runs.

**Overlap to avoid:** Another quantum-inspired controller or swarm-communication demo.

**Missing question worth testing:** Can behavioral interface alignment outperform a parameter-matched linear map once sensor/action symmetries, timing and noise are controlled?

### 9. Supermix Poseidon 3.8.0

**Implemented mechanism:** CPU research workbench around frozen Tidal, optional explicit trained ORACLE artifacts, hierarchy memory, one-step supported planning, adaptation, exact tools and many independent synthetic studies. CognitiveAgent returns the frozen base action when planning is unsupported. ExternalAdapterBridge validates declared units/coordinate frames, sessions, tick order, physical bounds and replay arithmetic.

**Evidence inspected:** The current README labels useful learned memory and structural transfer as research objectives. learning-foundation report rejects the initial ORACLE: candidate survival 0/48 versus frozen Tidal 48/48. A corrected channel-schema assay documents progress mistakenly interpreted as exposure; after correction, the residual candidate still loses reward by 1.0711 in the 64-seed block. [Pinned README](https://github.com/kai9987kai/Supermix-Poseidon/blob/72d42218ae92cee5c9668a090f9d31d8d9961681/README.md), [core source](https://github.com/kai9987kai/Supermix-Poseidon/blob/72d42218ae92cee5c9668a090f9d31d8d9961681/poseidon/cognitive_agent.py), [additional implementation](https://github.com/kai9987kai/Supermix-Poseidon/blob/72d42218ae92cee5c9668a090f9d31d8d9961681/poseidon/external_adapter.py).

**Strongest reusable lesson:** Prediction accuracy, valid schema, replay integrity and closed-loop usefulness are different properties. This portfolio already contains a real semantic interface failure even though all numbers fit the expected vector shape.

**Limits and aspiration boundary:** TidePool and later worlds remain synthetic. Source names/status do not establish general autonomous learning, biological or physical capabilities. The external adapter trusts declared semantics and uses the canonical observation/action contract; it does not infer unknown sensor/action mappings. Some historical research prose overstates physical validation relative to synthetic checks.

**Overlap to avoid:** Another memory/controller/active-inference integration: Helm, TRIDENT, decision-value/contrastive memory, causal diffusion, schedule-shift tracking, discovery demos, typed adapters and research receipts are already present.

**Missing question worth testing:** Can a black-box module pair establish a behavioral contract while preserving unresolved sensor/action/timing symmetries, and refuse transfer when no supported alignment exists?

## CROSSWIRE overlap assessment

A behavioral interoperability laboratory is a stronger distinct direction than adding another memory, controller, connectome graft or audit ledger. The narrow question is whether ambiguity-preserving adapters, selected with targeted behavioral counterexamples, can compose independently implemented modules when channel/action mappings, temporal alignment or invariances are unknown.

This is adjacent to architecture stitching and functional alignment; it should not claim that adapters, black-box system identification, counterexample-guided synthesis, protocol conformance or symmetry-aware learning are new. Portfolio distinctness is not a global novelty proof.

Evidence motivating this question:

- Archimedes chooses a ridge-map point estimate from shared token embeddings; it has no set-valued alignment or targeted experiment-selection mechanism in the inspected implementation. [LiftMaps source](https://github.com/kai9987kai/supermix-archimedes/blob/1952cf1c92cb506fff60f9ee0c055c2365988e5e/archimedes/src/archimedes_core.py).
- Prometheus shows that independently trained state codes can invert learned meaning and that decodability does not establish causal use. [Current results narrative](https://github.com/kai9987kai/prometheus-alpha/blob/417009e5548453338761732152b7b8ec30ffa79a/README.md).
- Poseidon's declared typed adapter checks protocol shape, units, timing and kinematics. Its tick path passes the received canonical observation to the agent; declarations are not an inferred semantic alignment. [Adapter implementation](https://github.com/kai9987kai/Supermix-Poseidon/blob/72d42218ae92cee5c9668a090f9d31d8d9961681/poseidon/external_adapter.py).
- Poseidon's corrected schema-control assay is a direct failure case: a valid numeric channel was given the wrong semantic interpretation. The residual adapter was not rescued by fixing that interpretation. [Corrected assay](https://github.com/kai9987kai/Supermix-Poseidon/blob/72d42218ae92cee5c9668a090f9d31d8d9961681/docs/research/nexus-omega-adapter-schema-control-assay-2026-10-13.md).
- Supermix's exact admission/verification already addresses answer authority and canonical scenarios; a new project should measure cross-component behavioral compatibility, not rebrand those receipts. [Epistemic admission](https://github.com/kai9987kai/Supermix/blob/6ea1c2cc41e3705b4b899b764a001cec180d155d/source/nexus_epistemics.py), [canonical causal helper](https://github.com/kai9987kai/Supermix/blob/6ea1c2cc41e3705b4b899b764a001cec180d155d/source/nexus_causal_dag.py).

Required distinctions for a credible first instrument:

1. Identifiable mappings, several observationally equivalent mappings, several mappings that are decision-equivalent for a chosen task, and impossible alignments are separate ground-truth cases.
2. An adapter may be admitted only for a named task/horizon/perturbation family. Agreement on a probe bank is empirical compatibility, not proof of universal semantics.
3. Independent module implementations must avoid leaking the hidden transform through names, metadata, seeds, candidate order, common code paths or evaluation construction.
4. A set of plausible maps must remain a set until evidence separates it. Use agreement across that set to permit a bounded downstream decision; otherwise probe or abstain.
5. Compare identity/no adapter, oracle mapping, random mapping, a point-estimate linear/ridge map, behavioral/functional stitching and a budget-matched random-probe strategy. Count all fitting, candidate search, probes and execution.
6. Hold out mechanisms, not just seeds. Include noninvertible sensors, aliases, adversarially symmetric tasks, inconsistent actuators, multiple delays, delay drift and unit/coordinate mismatches that cannot be repaired by a permutation.
7. Report harmful-transfer frequency, selective coverage, alignment ambiguity, adaptation query cost, recovery lag, regret and computation. A certificate must name its finite contract and list counterexamples or untested conditions.

An alternate identifiability laboratory that chooses experiments to distinguish competing world mechanisms is also plausible, but overlaps more with Causeway/Poseidon causal-active-inference work. CROSSWIRE's independently implemented modules and composition contract give it the clearer boundary.

## Additional pinned sources inspected

Reuse policy for a new project: implement the experimental instrument independently from public concepts and paper descriptions. Do not copy these repositories' source, weights, datasets, assets, generated corpora or biological graph data. Cite their concrete lessons and failures. Any later import must have its exact artifact license and provenance reviewed separately; a root code license does not automatically cover bundled weights or data. No upstream implementation was executed, imported or copied during this review.

Evidence strength for every row: **source inspected**. Repository benchmark values above are **committed author-reported results**, inspected for context; none was independently rerun by this reviewer. Tests, remote model publication, real-world transfer and broader scientific validity were not verified.

- [prometheus-alpha: results/v7.json](https://github.com/kai9987kai/prometheus-alpha/blob/417009e5548453338761732152b7b8ec30ffa79a/results/v7.json)
- [morpheus: results/eaudit_early.json](https://github.com/kai9987kai/morpheus/blob/5db6f98d605b80245ed9ff5e2cc9d42151830a14/results/eaudit_early.json)
- [Supermix-Expanse-v2: expanse/MIXTURE_STUDY.md](https://github.com/kai9987kai/Supermix-Expanse-v2/blob/33e38a279c86bccdb1e5680f15f193d61a3f71cb/expanse/MIXTURE_STUDY.md)
- [Supermix-Expanse-v2: expanse/src/source_sampler.py](https://github.com/kai9987kai/Supermix-Expanse-v2/blob/33e38a279c86bccdb1e5680f15f193d61a3f71cb/expanse/src/source_sampler.py)
- [supermix-archimedes: LICENSE](https://github.com/kai9987kai/supermix-archimedes/blob/1952cf1c92cb506fff60f9ee0c055c2365988e5e/LICENSE)
- [Supermix: source/nexus_causal_dag.py](https://github.com/kai9987kai/Supermix/blob/6ea1c2cc41e3705b4b899b764a001cec180d155d/source/nexus_causal_dag.py)
- [QuantumBot: quantumbot/simulation.py](https://github.com/kai9987kai/QuantumBot/blob/42e4fd637da2df1da5241da484ebc2c625050e72/quantumbot/simulation.py)
- [Supermix-Poseidon: docs/research/learning-foundation-2026-10-12.md](https://github.com/kai9987kai/Supermix-Poseidon/blob/72d42218ae92cee5c9668a090f9d31d8d9961681/docs/research/learning-foundation-2026-10-12.md)
- [Supermix-Poseidon: docs/research/README.md](https://github.com/kai9987kai/Supermix-Poseidon/blob/72d42218ae92cee5c9668a090f9d31d8d9961681/docs/research/README.md)
- [Supermix-Poseidon: docs/research/nexus-omega-adapter-control-assay-2026-10-13.md](https://github.com/kai9987kai/Supermix-Poseidon/blob/72d42218ae92cee5c9668a090f9d31d8d9961681/docs/research/nexus-omega-adapter-control-assay-2026-10-13.md)
- [Supermix-Poseidon: docs/research/nexus-omega-adapter-schema-control-assay-2026-10-13.md](https://github.com/kai9987kai/Supermix-Poseidon/blob/72d42218ae92cee5c9668a090f9d31d8d9961681/docs/research/nexus-omega-adapter-schema-control-assay-2026-10-13.md)
- [Supermix-Poseidon: docs/research/interactive-3d-external-adapter-stage7-2026-10-13.md](https://github.com/kai9987kai/Supermix-Poseidon/blob/72d42218ae92cee5c9668a090f9d31d8d9961681/docs/research/interactive-3d-external-adapter-stage7-2026-10-13.md)
- [Supermix-Poseidon: poseidon/nexus_omega/residual_adapter.py](https://github.com/kai9987kai/Supermix-Poseidon/blob/72d42218ae92cee5c9668a090f9d31d8d9961681/poseidon/nexus_omega/residual_adapter.py)
