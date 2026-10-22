# Research basis for CROSSWIRE

Reviewed 22 October 2026. These are selected primary sources, not an exhaustive literature search or a ranking of the world's best methods. Publication dates and arXiv revisions were checked live. The design below is an inference from this literature and the separate repository review; none of these sources establishes that CROSSWIRE works.

## Recent work that changes the design

| Primary source | What it contributes | Consequence for this project |
|---|---|---|
| Smith, Mannering & Marcu, [Functional Alignment Can Mislead: Examining Model Stitching](https://proceedings.mlr.press/v267/smith25a.html), ICML 2025 | Successful stitching can coexist with very different represented information, including different predictive cues. | Measure behavior under interventions and held-out changes. Calibration fit alone cannot establish semantic agreement. |
| Athanasiadis, Karmush & Felsberg, [Grounding Functional Similarity by Invariance-Aware Model Stitching](https://arxiv.org/abs/2505.20142v2), revised 1 June 2026 | Studies forward and backward compatibility and the invariances obscured by ordinary stitching. | Include mismatched invariances and aliasing; distinguish a useful one-way connection from semantic equivalence. This paper is direct adjacent work, not a method CROSSWIRE has reproduced. |
| Sanyal et al., [KLAS](https://proceedings.iclr.cc/paper_files/paper/2026/hash/e9f0ce998bede73f8068985f3deeab9a-Abstract-Conference.html), ICLR 2026 | Selects neural stitches using representation similarity to improve accuracy versus compute trade-offs. | Ordinary stitching is a serious existing approach. A later neural phase needs an implemented competitive alignment baseline and measured compute, rather than a comparison only with random mappings. |
| Benintendi et al., [Grounded Joint-Attention Other-Play for Zero-Shot Coordination](https://arxiv.org/abs/2610.06025v1), submitted 5 October 2026 | MATE adds an environment-grounded joint attention signal for independently trained partners. | Grounding information is an experimental resource. Compare absent anchors with explicitly supplied anchors and charge their acquisition. CROSSWIRE is not a reproduction of MATE or its MARL results. |
| Kim, [Drawing with Strangers](https://arxiv.org/abs/2606.10582v1), submitted 9 June 2026 | Studies communication between independent populations and the role of perceptual grounding. | Within-population success is different from interoperability with unfamiliar implementations. Hold out module construction and partners, not merely random seeds. Preprint findings require independent evaluation. |
| Fortz et al., [A research agenda for active automata learning](https://sfortz.github.io/publication/2026-al-agenda/2026-al-agenda.pdf), accepted 3 February 2026 | Surveys active model learning and open challenges, including practical interfaces and the gap between conformance testing and guarantees. | State reset, determinism, state bounds, query access and equivalence assumptions explicitly. A finite probe bank is not an equivalence oracle. |
| Chen et al., [PolyVer](https://arxiv.org/abs/2503.03207v3), FMCAD 2025, revised 12 October 2025 | Connects contract synthesis and counterexample-guided verification across programming languages. | Contracts and counterexample refinement are established ideas. Separate observed contradictions from a proof about a declared finite model. A trace receipt is not formal verification. |

## Foundational prior art that prevents inflated novelty claims

| Primary source | Existing idea | Boundary for CROSSWIRE |
|---|---|---|
| Autili, Inverardi & Tivoli, [Automatic adaptor synthesis for protocol transformation](https://arxiv.org/abs/1412.0527v1), WCAT 2004, uploaded 2014 | Compositional glue synthesis to repair protocol mismatches. | Adapter synthesis and protocol interoperability are decades-old topics. Use the original 2004 venue date rather than mistaking the arXiv upload for the work's origin. |
| Amram et al., [Adapting Behaviors via Reactive Synthesis](https://arxiv.org/abs/2105.13837v1), 2021 | Synthesizes an adapter between target and adaptee transducers. | The core adapter problem is established. CROSSWIRE's candidate contribution is its bounded evidence/ambiguity experiment and benchmark, not the invention of adapter synthesis. |
| Steffen, Howar & Isberner, [Active Automata Learning: From DFAs to Interface Programs and Beyond](https://proceedings.mlr.press/v21/steffen12a.html), ICGI 2012 | Mealy-machine learning, alphabet abstraction and interface programs. | A finite-state model and distinguishing queries are established machinery. Include a recognized conformance-learning comparison before claiming an algorithmic advantage. |
| El-Yaniv & Wiener, [On the Foundations of Noise-free Selective Classification](https://jmlr.org/papers/v11/el-yaniv10a.html), JMLR 2010 | Formalizes the error versus coverage trade-off with a reject option. | Abstention is not new, and zero accepted connections is not success. Measure useful coverage, harm and abstention cost together. |

## Existing tools worth comparing with

[LearnLib](https://learnlib.de/) provides active/passive automata learning and several approximate equivalence/conformance strategies. [AALpy](https://github.com/DES-Lab/AALpy) provides Python implementations for deterministic, nondeterministic and stochastic models. The first build should use a pinned AALpy L-star comparison with a finite query budget, plus a clearly identified bounded conformance test. Its test oracle must receive the same system access as CROSSWIRE. Only a separately marked oracle diagnostic may receive hidden state or exact equivalence access.

Neither library was installed or executed during this review. Versions, dependency hashes and actual settings must be recorded when the implementation is built. A depth-limited test called a W-method without its state-bound assumptions would be misleading.

## Working novelty statement

CROSSWIRE proposes a small experimental instrument for studying when finite behavioral evidence supports a task-specific connection through an unknown interface. Its candidate mechanism retains multiple interface interpretations and computes behavior permitted by all of them, while distinguishing resolvable uncertainty, observationally unresolvable semantic ambiguity, and a contradicted adapter family.

The combination is distinct from the centers of the 26 reviewed repositories. This review does not establish global novelty, a new theorem, superiority to existing synthesis/learning methods, general AI interoperability, biological validity or a breakthrough. Those claims would require further literature work and results. A negative experiment would still be a useful project outcome if it identifies where the mechanism has no advantage.

## What to use and what to leave for later

Use finite transducers, selective decisions, counterexamples, exact private audits and independently implemented held-out targets first. Leave large neural training, biological networks, game injection, hardware emulation, boot changes and live external controllers for later work. They would add cost and ambiguity before the core question is answered.
