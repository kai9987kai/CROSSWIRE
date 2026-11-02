# Research synthesis: bounded experiments and solver structure

Primary sources were checked on 1 November 2026. This is a targeted engineering review, not an exhaustive survey or a global novelty assessment.

| Primary source and verified date | Transferable point | CROSSWIRE decision |
|---|---|---|
| Fortz et al., [A Research Agenda for Active Automata Learning](https://tneele.com/static/papers/sttt2026_al_agenda.pdf), accepted 3 February 2026 | Separates practical learning access, assumptions, counterexample search and conformance guarantees; highlights structured testing and benchmarking gaps. | Optimize explicitly bounded task readiness. Do not call a finite query bank an equivalence oracle. Keep independent checking and empirical target outcomes separate. |
| Vaandrager & Melse, [New Fault Domains for Conformance Testing of Finite State Machines](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CONCUR.2025.34), published 18 August 2025 | Completeness depends on a declared fault domain; the paper develops access/reachability assumptions and apartness-based sufficient conditions. | Certificates cover the enumerated adapter family and all branches of the supplied tree. Safety-filtered/truncated query banks do not inherit the paper's conformance completeness theorem. |
| Kruger, Junges & Rot, [Small Test Suites for Active Automata Learning](https://link.springer.com/chapter/10.1007/978-3-031-57249-4_6), first online 5 April 2024 | Uses structural assumptions and combines test-generation suites with a bandit. Reported improvements were limited for small/medium models. | Retain strong greedy baselines and measure the local adaptation. A small synthetic pilot can yield no advantage; no speedup or coverage improvement is presumed. |
| Kruger, Junges & Rot, [Error-Awareness Accelerates Active Automata Learning](https://link.springer.com/chapter/10.1007/978-3-032-26204-2_27), first online 18 May 2026 | Exploits known observable, persistent error behavior and varying trusted reference knowledge to accelerate learning. | Deferred: CROSSWIRE's raw symbols lack intrinsically trusted error meanings. Repeated output IDs cannot justify pruning semantic hazards or inventing observations. |

## Implemented adaptation

`lookahead` searches reset-separated query trees of depth at most two from the existing length-1..3 bank. Every root model follows exactly one complete predicted-response branch. A ready leaf supplies a common hazard-free goal-reaching deployment word. Ranking first maximizes the number of root candidates reaching ready leaves, then prefers smaller unresolved beliefs, smaller terminal belief squares and fewer worst-case calls. These are uniform finite-model counts, not learned or calibrated target probabilities.

Each query costs one reset plus all actions. Ready beliefs terminate immediately, matching the acquisition stopping rule. A deterministic 2,048-state expansion cap bounds planning; exhausted searches retain a completed proposal or use a checked one-query fallback. Only the root query is executed, then the engine replans using actual observations. A hypothetical tree is never counted as measured evidence, and its readiness fraction is a proposal property rather than a guarantee about future replanning behavior.

The independent experiment checker separately reconstructs permutations, latency buffers, observations and branch beliefs. It validates complete response coverage, semantic guards, readiness witnesses and call bounds. The final public-evidence checker reconstructs every proposed tree from evidence preceding that query and checks the stored certificate. It does not establish optimizer optimality, target inclusion, reset reliability or private audit authenticity.

The selectable factored backend reuses the same canonical adapter IDs. Robust planning searches the product of active input-factor states and returns SEARCH_LIMIT on bounded-search exhaustion. Default task probing now aggregates exact rational Jaccard separation over contract classes, avoiding allocation of every candidate pair. Exact ties may differ from historical floating-summation artifacts; historical receipts remain bound to their original source.

## Evaluation and limits

The frozen exploratory protocol compares entropy, greedy branching and lookahead at call caps 4 and 8, across two generated structural seed requests and both backends (24 runs). Structural identities and collisions determine actual parent counts; labels and implementations are nuisance repetitions. The separate 12-run control protocol includes nominal latch, latency and semantic corruption. The controls deliberately permit unrestricted calibration and may incur calibration hazards.

Report task outcomes, calibration/deployment hazards, acquisition calls, proposed-tree readiness, search-limit frequency, source work and wall time separately. Compare flat/factored behavioral projections, not whole scientific hashes: configuration, backend storage and computational counters intentionally differ. Public checking/private audit still enumerate the finite class; factor counts and cached-adapter counts do not prove end-to-end memory or speed gains. Larger-alphabet library tests do not establish larger-alphabet runtime support.

### Observed exploratory results — 2 November 2026

The [24-run generated-target pilot](../reports/budgeted-planning-pilot.md) found **no useful-coverage advantage** for lookahead over entropy or branching. The two structural requests produced two distinct parents. Both backend strata have the following results; backend repetitions do not increase the independent-parent denominator.

| Acquisition cap | Policy | Successful parents | Mean acquisition calls | Hazardous calibration probes | Deployment hazards |
|---|---|---|---|---|---|
| 4 | entropy | 0/2 | 3.0 | 0 | 0 |
| 4 | branching | 0/2 | 3.0 | 0 | 0 |
| 4 | lookahead | 0/2 | 3.5 | 0 | 0 |
| 8 | entropy | 1/2 | 7.0 | 0 | 0 |
| 8 | branching | 1/2 | 7.0 | 0 | 0 |
| 8 | lookahead | 1/2 | 6.0 | 0 | 0 |

Thus lookahead used one fewer mean acquisition call at cap eight and half a call more at cap four. These are descriptive results from two parents, not evidence of a general efficiency gain. The pointwise 95% hazard intervals remain wide even with zero observed events; the generated reports retain those bounds.

The [12-run temporal/unrestricted controls](../reports/budgeted-planning-controls.md) preserved successful deployment on latch and delay for both methods/backends, while **all four semantic-corruption runs were admitted and hazardous**. For each backend, entropy incurred two hazardous calibration probes on latch and two on delay; lookahead incurred one on latch and zero on delay. Semantic-corruption calibration had no recorded hazards, followed by hazardous deployment. This negative control demonstrates that matching raw behavior and a valid public certificate do not establish correct private semantics.

The [eight-run small-budget latch smoke study](../reports/budgeted-experiments.md) reached the goal with lookahead at cap four, where entropy abstained; both abstained at cap two. Each cap-four lookahead run incurred one hazardous calibration probe because this smoke protocol deliberately used unrestricted probing. Its coverage result cannot be presented as safe calibration evidence.

Protocols, complete receipts and the final source/checking record are linked from [the verification report](../docs/verification-budgeted-experiments.md). Timing and storage measurements in individual receipts are observations from this machine; no controlled end-to-end performance benchmark was conducted.

This is a bounded observation-tree planning adaptation alongside an integration/scaling improvement. ADS, version spaces, robust planning, product-state search, Jaccard objectives and factored representations are established techniques. No new theorem, best-in-class performance, general interoperability or real-world safety follows from implementing them together.
