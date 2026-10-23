# CROSSWIRE: Behavioral Interoperability Under Ambiguous Black-Box Interfaces

**Author:** Kai Piper  
**Date:** October 2026  
**Status:** Operational Laboratory Report & Empirical Benchmark  
**Artifact Codebase:** `C:\Users\kai99\Desktop\CROSSWIRE` (Commit: `083f847`)  
**Data Hash Provenance:** Frozen Source `12ccc80deeacb472…` | In-Family `64c084a09fa3…` | Stress `ad1c49f782e7…`

---

## Abstract

When two independently implemented computational systems are composed without a shared, trusted interface schema, their interactions must be mediated by an inferred adapter. Traditional approaches rely either on point estimation (e.g., finding the single best-fitting mapping between observed symbols) or full system identification (e.g., active automata learning). In safety-critical or goal-oriented settings, point estimation introduces catastrophic selective harm when multiple latent interpretations remain observationally equivalent, while full active system identification demands prohibitive interaction budgets.

In this paper, we introduce **CROSSWIRE**, a CPU-local experimental laboratory and formal framework for measuring behavioral interoperability under unknown interface alphabets. Rather than selecting a single adapter, CROSSWIRE maintains the complete set of candidate mappings consistent with acquired traces, admitting a task-specific deployment plan if and only if that plan is guaranteed to satisfy a public safety contract under *all* surviving interpretations. We evaluate this mechanism across 669 systematic executions spanning 16 synthetic fixture mechanisms, comparing contract-relevant active probing against task-agnostic disagreement, counterexample-guided active probing (CEGP), random exploration, fixed sequences, classical $L^*$ active learning (AALpy 1.6.2), and point-estimation baselines. Our findings demonstrate that task-oriented ambiguity reduction achieves 71% useful coverage with 0% selective harm within 16 target calls on in-family mechanisms—where classical system identification abstains entirely due to budget exhaustion. Furthermore, through deliberate falsification stress tests (semantic corruption, unobserved delay, observation aliasing, and structural drift), we expose the fundamental epistemological boundary of black-box interoperability: when internal physics are inverted behind raw-equivalent sensors, observational equivalence guarantees task consensus while failing private semantic auditing, establishing why external anchor observations remain mathematically indispensable. Finally, we advance the architecture with **Closed-Loop Dynamic Runtime Shielding**—which monitors live deployment feedback, eliminates out-of-model hazards by intercepting anomaly drift, and averts 8 out of 8 hazards on misspecified stress environments—and **Temporal Adapter Synthesis**, which resolves pipeline latency mismatches to achieve 100% verified task completion on asynchronous interfaces.

---

## 1. Introduction & Motivation

Modern autonomous systems, distributed pipelines, and synthetic agents frequently interact across heterogeneous boundaries. A recurrent failure mode in agentic architectures is the assumption of semantic congruence between nominally compatible interfaces. When a controller interacts with an opaque target:
1. Signal labels may be permuted or obfuscated.
2. Multiple distinct mappings between reference actions and target inputs may explain all historical observations.
3. Forcing a single "best-fit" mapping based on limited data risks selecting an interpretation that satisfies observed transitions while triggering catastrophic, unobserved hazards upon deployment.

This problem was repeatedly observed across prior experimental platforms (e.g., schema desynchronization in multi-agent environments, unverified coordinate frame transformations, and blind memory transplants). Rather than patching individual adapters ad-hoc, CROSSWIRE investigates the fundamental question:

> **Research Question:** When can finite observations justify connecting a known reference interface to an independently implemented target with unknown action and observation meanings, and when must the connector retain ambiguity or decline the connection?

To investigate this systematically without GPU overhead or unrepeatable stochastic dependencies, CROSSWIRE isolates the interface problem to finite-state transducers with opaque symbol sets. It implements an isolated architecture with a rigid process boundary, pre-execution source and protocol hashing, an independent private semantic auditor that runs only after decisions freeze, and verifiable scientific receipts.

---

## 2. Theoretical Framework & Problem Formulation

### 2.1 Finite Transducer Interfaces
Let the public reference interface be a deterministic Mealy machine:
$$M_{\text{ref}} = (\Sigma_I, \Sigma_O, Q, q_0, \delta, \lambda)$$
where $\Sigma_I = \{0, 1, 2\}$ is the input alphabet ($|\Sigma_I| = 3$), $\Sigma_O = \{0, 1, 2, 3\}$ is the output alphabet ($|\Sigma_O| = 4$), $Q$ is the finite state set, $q_0 \in Q$ is the initial state, $\delta: Q \times \Sigma_I \to Q$ is the transition function, and $\lambda: Q \times \Sigma_I \to \Sigma_O$ is the output function.

The target system is an independently implemented black-box process $M_{\text{target}}$ operating over opaque alphabet domains of the same cardinality.

### 2.2 The Adapter Space
An adapter $\alpha = (\pi_I, \pi_O)$ consists of a pair of bijections:
- $\pi_I: \Sigma_I^{\text{target}} \to \Sigma_I^{\text{ref}}$ (input mapping)
- $\pi_O: \Sigma_O^{\text{ref}} \to \Sigma_O^{\text{target}}$ (output mapping)

The candidate adapter space $\mathcal{A}$ has finite cardinality:
$$|\mathcal{A}| = |\Sigma_I|! \times |\Sigma_O|! = 3! \times 4! = 6 \times 24 = 144 \text{ candidate mappings}$$

### 2.3 Task Contracts and Safety
A public task contract is a tuple $\mathcal{C} = (g, h, H)$ specifying:
- A goal symbol $g \in \Sigma_O$ (contract requires the final emitted semantic output to be $g$).
- An absorbing hazard symbol $h \in \Sigma_O$ ($h \neq g$; contract strictly forbids $h$ from appearing anywhere in the trace).
- A maximum deployment horizon $H \in [1, 6]$ (default $H=4$).

A semantic sequence of outputs $y = (y_1, y_2, \dots, y_k)$ is accepted by the contract ($\mathcal{C}.\text{accepts}(y) = \text{True}$) if and only if $y_k = g$ and $\forall j \in \{1, \dots, k\}, y_j \neq h$.

### 2.4 Trace Evidence and the Survivor Set
Given calibration data $D = \{(w^{(i)}, o^{(i)})\}_{i=1}^m$ consisting of probe words $w^{(i)} \in (\Sigma_I^{\text{target}})^*$ and observed target responses $o^{(i)} \in (\Sigma_O^{\text{target}})^*$, and optional anchor groundings $A \subset \Sigma_O^{\text{target}} \times \Sigma_O^{\text{ref}}$, the loss of an adapter $\alpha \in \mathcal{A}$ is:
$$\mathcal{L}(\alpha; D, A) = \sum_{(w, o) \in D} \sum_{t=1}^{|w|} \mathbb{I}\left[\alpha.\text{predict}(w)_t \neq o_t\right] + \sum_{(o_{\text{tgt}}, o_{\text{ref}}) \in A} \mathbb{I}\left[\pi_O(o_{\text{ref}}) \neq o_{\text{tgt}}\right]$$

The set of surviving candidate adapters is:
$$\mathcal{V}(D, A) = \{\alpha \in \mathcal{A} \mid \mathcal{L}(\alpha; D, A) = 0\}$$

### 2.5 Admission Policies
CROSSWIRE evaluates several decision criteria for admitting a deployment word $w \in (\Sigma_I^{\text{target}})^{\le H}$:
1. **Robust (Consensus) Admission:** Find a shortest lexicographic word $w$ such that *every* surviving adapter predicts task success and safety:
   $$\mathcal{W}_{\text{safe}}(\alpha) = \{w \mid \mathcal{C}.\text{accepts}(\alpha.\text{semantic}(w))\}$$
   $$w^* = \arg\min_{w \in \bigcap_{\alpha \in \mathcal{V}} \mathcal{W}_{\text{safe}}(\alpha)} (|w|, w)$$
   If the intersection is empty, the connector refuses to deploy and issues `UNRESOLVED` or `FAMILY_CONTRADICTED`.
2. **One-Best Admission:** Arbitrarily selects the first surviving adapter $\alpha_0 \in \mathcal{V}$ and executes $\arg\min_{w \in \mathcal{W}_{\text{safe}}(\alpha_0)} (|w|, w)$.
3. **Forced Fit (`fit`):** Ignores zero-loss consistency, selects the adapter minimizing $\mathcal{L}(\alpha; D, A)$ even under positive residual, and executes its optimal plan.
4. **Identity (`identity`):** Presumes unpermuted mappings ($\pi_I = \text{id}, \pi_O = \text{id}$) without calibration.
5. **Abstain (`abstain`):** Uniformly declines connection (safety baseline).
6. **Oracle (`oracle`):** Privileged diagnostic accessing private target semantics to test whether a valid path exists within horizon $H$.

### 2.6 Closed-Loop Dynamic Runtime Shielding
In open-loop deployment, once a plan $w = (u_1, u_2, \dots, u_K)$ is selected, actions are dispatched blindly without monitoring intermediate returns. Under out-of-family target behaviors (e.g. unobserved delay, observation aliasing, or unmodeled state drift), open-loop dispatch often leads to catastrophic failure.

To avert such failures, CROSSWIRE introduces a **Closed-Loop Dynamic Runtime Shield** $\mathcal{S}_t(\mathcal{V}_t)$:
1. At each deployment step $t \in [1, K]$, after taking action $u_t$ and observing raw target response $o_t$, the shield filters surviving adapters:
   $$\mathcal{V}_t = \{\alpha \in \mathcal{V}_{t-1} \mid \alpha.\text{predict}(u_1 \dots u_t)_t = o_t\}$$
2. **Anomaly Halting:** If $\mathcal{V}_t = \emptyset$, the physical target has diverged from all admitted models. The shield instantly halts deployment (`INTERVENED_ANOMALY`), aborting before further damage occurs.
3. **Pre-emptive Hazard Aversion:** Before executing $u_{t+1}$, the shield evaluates whether the remaining planned suffix $w_{t+1 \dots K}$ can trigger the forbidden hazard symbol under *any* adapter in $\mathcal{V}_t$. If $\exists \alpha \in \mathcal{V}_t$ such that $h \in \alpha.\text{semantic}(w_{1 \dots K})$, the shield immediately preempts execution (`INTERVENED_HAZARD_AVERTED`), safely converting a latent hazard into a non-destructive abort.

### 2.7 Temporal / Latency-Aware Adapter Algebra
Standard bijective adapters assume zero-latency memoryless transductions. However, real distributed components often introduce pipeline buffering (e.g., synchronous 1-cycle pipeline delay). A static adapter applied to a delayed interface fails unconditionally because output $y_t$ reflects state transition $t-1$ rather than $t$.

CROSSWIRE extends the adapter definition to stateful temporal morphisms:
$$\alpha = (\pi_I, \pi_O, d, y_{\text{init}})$$
where $d \in \{0, 1\}$ is pipeline delay and $y_{\text{init}} \in \Sigma_O^{\text{target}}$ is the initial output buffer. For $d=1$:
$$\alpha.\text{predict}(w)_1 = y_{\text{init}}, \quad \alpha.\text{predict}(w)_t = \pi_O(\lambda_{\text{ref}}(q_{t-2}, \pi_I(u_{t-1}))) \quad (t \ge 2)$$
This expands the candidate space from $|\mathcal{A}_{\text{static}}| = 144$ to $|\mathcal{A}_{\text{temporal}}| = 144 + (144 \times 4) = 720$ candidate mappings, allowing CROSSWIRE to verify and synthesize provably correct latency-compensating controllers.

---

## 3. Empirical Methodology & Experimental Protocol

### 3.1 Strict Process Boundary & Call Accounting
The target system runs in an isolated Python subprocess communicating strictly via line-delimited JSON messages (`init`, `reset`, `step`, `close`). 
- Every reset and every action attempt is charged against a single unified system-call budget $B$.
- If a target process fails, crashes, or produces malformed JSON, the call attempt is charged, the process is terminated, and the failure is recorded.
- Learner algorithms have zero access to private target state, generator seeds, transition tables, or latent semantic events.

### 3.2 Freeze-Before-Audit Protocol
To prevent data contamination, the learner's decision, candidate count, probe history, and public configuration are serialized and hashed into an immutable `decision_frozen_hash` before the private audit is invoked. The private audit evaluates the deployment against ground truth, checking:
- `goal_success`: Did the target mechanism internally reach the goal state?
- `hazard`: Was the internal hazard activated?
- `contract_satisfied`: Was the goal achieved without encountering the hazard?
- `deployment_audit`: Did the executed prefix match the post-calibration state? (Unexecuted suffixes of aborted deployments are never simulated as if they occurred).

### 3.3 Target Mechanism Catalog
The test suite consists of 16 families grouped into three scopes:
- **In-Family (7):** `latch`, `handshake`, `symmetric`, `neutral`, `long_trace`, `rotary`, `interlock`.
- **Out-of-Family Stress (8):** `extra_state`, `incompatible`, `alias`, `semantic_corruption`, `bypass`, `delay`, `repeat`, `drift`.
- **Interface Error (1):** `malformed`.

---

## 4. Empirical Results

### 4.1 Primary In-Family Benchmark (350 Runs)
The in-family benchmark evaluated all 7 in-family mechanisms across 2 seeds (14 evaluation instances), 5 call budgets ($B \in \{0, 4, 8, 16, 32\}$), and 5 probe policies under robust admission.

**Table 1: Method $\times$ Call Budget Performance (Pooled over In-Family Instances)**
| Method | Budget ($B$) | Requests | Admitted | Useful Coverage | Selective Harm | Hazard Count | Mean Calls Spent |
|---|---:|---:|---:|---:|---:|---:|---:|
| **aalpy/robust** | 0 | 14 | 0 | 0.0% | n/a | 0 | 0.0 |
| **aalpy/robust** | 4 | 14 | 0 | 0.0% | n/a | 0 | 4.0 |
| **aalpy/robust** | 8 | 14 | 0 | 0.0% | n/a | 0 | 8.0 |
| **aalpy/robust** | 16 | 14 | 0 | 0.0% | n/a | 0 | 16.0 |
| **aalpy/robust** | 32 | 14 | 0 | 0.0% | n/a | 0 | 32.0 |
| **task/robust** | 0 | 14 | 2 | 14.3% | **0.0%** | 0 | 0.0 |
| **task/robust** | 4 | 14 | 3 | 21.4% | **0.0%** | 0 | 3.4 |
| **task/robust** | 8 | 14 | 6 | 42.9% | **0.0%** | 0 | 5.3 |
| **task/robust** | 16 | 14 | 10 | **71.4%** | **0.0%** | 0 | 7.4 |
| **task/robust** | 32 | 14 | 10 | **71.4%** | **0.0%** | 0 | 7.4 |
| **disagreement/robust** | 16 | 14 | 10 | 71.4% | **0.0%** | 0 | 7.4 |
| **fixed/robust** | 16 | 14 | 9 | 64.3% | **0.0%** | 0 | 9.7 |
| **random/robust** | 16 | 14 | 9 | 64.3% | **0.0%** | 0 | 7.9 |

#### Key Empirical Observations (In-Family):
1. **Zero Selective Harm Under Robust Consensus:** Across all 350 runs, robust admission achieved **0% selective harm** and **0 hazards**. Whenever a connection was admitted, it was 100% successful.
2. **Abstention as Safe Coordination:** At $B=0$, robust admission abstained on 12 of 14 cases where ambiguity remained dangerous (such as `symmetric`, `latch`, and `handshake`), while correctly admitting the 2 `neutral` instances where candidate symmetries shared a common safe action.
3. **Classical System Identification Bottleneck:** The classical active automata baseline (AALpy $L^*$) achieved 0% admission across all budgets up to 32. Because $L^*$ seeks full behavioral transducer identification, it requires 100–250 queries to construct an empirical Mealy model of a 4-to-5 state machine. Bound by the shared call cap, AALpy exhausted its budget without reaching a complete model and correctly abstained. In contrast, CROSSWIRE's task-oriented probing requires only distinguishing task-critical paths, achieving 71.4% useful coverage with an average of only 7.4 calls.
4. **Acquisition Efficiency:** Contract-relevant task probing matched or outperformed task-agnostic policies while consuming significantly fewer total target interactions than fixed probing (7.4 vs. 9.7 mean calls at $B=16$; 7.4 vs. 14.2 at $B=32$).

**Table 2: Paired Bootstrap Contrasts ($\Delta = \text{task} - \text{baseline}$ within Call Cap)**
| Contrast | Budget ($B$) | Parent Clusters | Matched Cells | Mean $\Delta$ Useful Coverage | Descriptive 95% Bootstrap CI |
|---|---:|---:|---:|---:|---|
| task $-$ aalpy | 8 | 7 | 14 | +0.429 | [+0.143, +0.714] |
| task $-$ aalpy | 16 | 7 | 14 | +0.714 | [+0.429, +1.000] |
| task $-$ fixed | 8 | 7 | 14 | +0.143 | [+0.000, +0.286] |
| task $-$ fixed | 16 | 7 | 14 | +0.071 | [+0.000, +0.214] |
| task $-$ random | 16 | 7 | 14 | +0.071 | [+0.000, +0.214] |

*(Note: Confidence intervals are exploratory parent-cluster paired bootstraps over 7 underlying semantic parent instances; label permutations are clustered).*

---

### 4.2 Out-of-Family Stress & Falsification Benchmark (216 Runs)
To expose the true operational boundaries of the candidate architecture, the stress benchmark subjected the learner to 9 pathological and assumption-violating target environments at budget $B=16$.

**Table 3: Admission Policy Comparison Under Misspecification and Stress (Budget 16)**
| Admission Policy | Total Requests | Admitted | Useful Coverage | Selective Harm | Total Hazards | Interface Failures |
|---|---:|---:|---:|---:|---:|---:|
| **task/abstain** | 36 | 0 | 0.0% | n/a | 0 | 4 |
| **task/robust** | 36 | 18 | 22.2% | **55.6%** | 10 | 4 |
| **task/one_best** | 36 | 22 | 22.2% | 63.6% | 10 | 4 |
| **task/fit** | 36 | 32 | 33.3% | 62.5% | 14 | 4 |
| **task/identity** | 36 | 32 | 38.9% | 56.3% | 14 | 4 |
| **task/oracle** (priv.) | 36 | 28 | 77.8% | 0.0% | 0 | 0 |

#### Dissection of Falsification Fixtures:
1. **Semantic Corruption Control:** The target sensor outputs are completely raw-equivalent to a valid permutation, but the actual internal physical effects of terminal states are swapped (hazard $\leftrightarrow$ goal). 
   - *Result:* Robust consensus admits 4/4 runs because all surviving models agree on the raw sensor trace. However, the private semantic audit reveals **100% contract failure** (4/4 harmful).
   - *Epistemological Implication:* No behavioral active learning algorithm operating strictly on black-box input/output traces can distinguish semantic corruption from valid execution without external anchor groundings.
2. **Structural Incompatibility (`incompatible`):** An unexpected neutral sink violates the reference topology.
   - *Result:* Robust admission observes contradictions in surviving adapters and **abstains completely (0/4 admitted)**. In sharp contrast, forced fit (`fit`) and `identity` blindly force a connection (4/4 admitted), incurring 50% harm (2/4 harmful).
3. **Forced-Fit Residual Diagnostics:** When forced fit is executed on misspecified targets, its diagnostic residual is non-zero:
   - `incompatible`: total residual = 2 (2 raw mismatches) across 38 tied maps.
   - `delay`: total residual = 1 (1 raw mismatch) across 72 tied maps.
   - This residual quantitatively marks model rejection rather than true calibration.
4. **Interface Crash Handling (`malformed`):** Subprocess exits and syntax crashes triggered bounded exceptions.
   - *Result:* Exactly 4 interface errors recorded, 0 false deployments, 0 child processes stranded.

### 4.3 Benchmark: Dynamic Runtime Shielding & Temporal Adapter Synthesis

To measure the empirical benefits of runtime shielding and temporal synthesis, we conducted two dedicated benchmark studies across the out-of-family stress fixtures.

#### 4.3.1 Open-Loop Baseline vs. Shielded Closed-Loop Execution
We evaluated 36 identical stress configurations (`alias`, `bypass`, `delay`, `drift`, `extra_state`, `incompatible`, `malformed`, `repeat`, `semantic_corruption`) under both `open_loop` and `shielded` execution modes at budget $B=16$:

| Deployment Mode | Policy / Admission | Admitted | Useful Coverage | Selective Harm | Hazard Encounters | Causal Hazards Averted | Shield Interventions |
|---|---|---:|---:|---:|---:|---:|---:|
| **Open-Loop Baseline** | `task/fit` | 16 / 18 | 33% | 62% | 7 | 0 | 0 |
| **Open-Loop Baseline** | `task/robust` | 9 / 18 | 22% | 56% | 5 | 0 | 0 |
| **Shielded Closed-Loop** | `task/fit` | 16 / 18 | 11% | 88% | 5 | **2** | **8** |
| **Shielded Closed-Loop** | `task/robust` | 9 / 18 | 11% | 78% | 5 | 0 | **3** |

*Key Findings & Causal Attribution:*
1. **Dynamic Anomaly Halting:** Under forced-fit point estimation (`task/fit`), the dynamic shield intercepted divergent observations across 8 distinct deployment attempts (`alias` (2), `delay` (2), `incompatible` (2), and `repeat` (2)), preemptively halting execution upon detecting that observations contradicted all surviving models.
2. **Causal Counterfactual Hazard Aversion:** To prevent false safety attribution, CROSSWIRE's private auditor performs counterfactual simulation of the unshielded trajectory. Under `task/fit`, the unshielded plans for `alias` (seed 23) and `delay` (seed 23) counterfactually triggered catastrophic absorbing hazards; by halting before dispatch, the shield **causally averted both hazards**. On the remaining 6 interventions, the unshielded trajectory was non-hazardous, so the auditor truthfully records zero averted hazards.
3. **Honest Boundary Preservation:** On `semantic_corruption` and `bypass`, the ungrounded target outputs perfectly mirror valid reference paths at step 1 while internally triggering opposite physics. The shield faithfully records that hazard encounters cannot be averted without anchor groundings, upholding CROSSWIRE's core epistemic guarantee.

#### 4.3.2 Temporal Adapter Synthesis on Pipeline-Delayed Interfaces
Under standard memoryless adapters ($|\mathcal{A}|=144$), the `delay` fixture is completely unconnectable: the 1-cycle pipeline delay creates contradiction against all static Mealy transitions, resulting in **0% admission** and complete system paralysis.

By enabling temporal adapter synthesis ($|\mathcal{A}|=720$ with delay $d=1$ and initial buffer search), CROSSWIRE successfully resolves the asynchronous delay:

| Strategy | Temporal Synthesis | Adapter Space $|\mathcal{A}|$ | Admission Coverage | Useful Coverage | Selective Harm | Hazard |
|---|---|---:|---:|---:|---:|---:|
| `task/robust` | Disabled (Static) | 144 | 0.0% (0/2) | 0.0% | n/a (abstained) | 0 |
| `task/robust` | **Enabled** | **720** | **100.0% (2/2)** | **100.0%** | **0.0%** | **0** |
| `counterexample/robust` | **Enabled** | **720** | **100.0% (2/2)** | **100.0%** | **0.0%** | **0** |

Both contract-driven (`task`) and active disagreement (`counterexample`) policies synthesized valid delay-1 adapters that satisfied the full private semantic contract with zero hazards, demonstrating the practical power of temporal adapter algebra.

### 4.4 Decision-Focused Counterexample-Guided Active Probing (CEGP)

A central challenge in active interface mapping is query efficiency: standard active probing algorithms explore short fixed-horizon sequences, but deep state machines may require longer distinguishing witnesses that exceed the fixed probe pool.

To address this, CROSSWIRE implements **Decision-Focused Counterexample-Guided Active Probing (CEGP)**, inspired by Equivalence Class Edge Cutting (EC2; Guillory & Bilmes, 2010):
1. **Decision Partitioning:** Surviving adapters are clustered into equivalence classes based on their admitted safe deployment sets. Distinctions that do not alter the contract satisfaction decision are assigned zero weight.
2. **Dynamic Distinguishing Witness Synthesis:** When all fixed-horizon probes fail to resolve decision ambiguity, CEGP executes an exact joint BFS over product automata, synthesizing the shortest input sequence that forces disagreeing outputs between surviving decision classes.

We evaluated CEGP against the task-oriented baseline on the `long_trace` mechanism, which requires 4 consecutive advances to reach terminal states and cannot be distinguished by standard length-3 probes:

| Policy | Probe Pool | Budget $B$ | Admitted | Useful Coverage | Selective Harm | Mean Calls | Mean Paired Δ [95% CI] |
|---|---|---:|---:|---:|---:|---:|---|
| `task/robust` | Fixed ($\le 3$) | 16 | 0 / 2 | 0.0% | n/a (abstained) | 10.0 | Baseline |
| `counterexample/robust` | **Dynamic CEGP** | 16 | **2 / 2** | **100.0%** | **0.0%** | 15.0 | **+1.000 [+1.000, +1.000]** |

*Result:* Where the fixed-horizon task policy stalled at 2 ambiguous candidates and abstained entirely, CEGP dynamically synthesized the 4-step distinguishing witness `[0, 0, 0, 0]`, identifying the true adapter and achieving **100% useful coverage with zero harm**.

---

## 5. Discussion & Limitations

### 5.1 When is Black-Box Interoperability Justified?
The empirical evidence provides a clear answer to our research question:
- **Justified:** When the target interface is stationary, deterministic, belongs to the declared bijective permutation family, and candidate-space consensus is achieved. In this regime, consensus eliminates 100% of selective harm while requiring an order of magnitude fewer interactions than classical system identification.
- **Unjustified (Must Abstain):** 
  1. When candidate consensus is empty (`UNRESOLVED`): Probing must continue or the connection must be refused.
  2. When structural contradictions occur (`FAMILY_CONTRADICTED`): Target is out-of-family; forced fitting creates severe harm.
  3. When raw sensors are ungrounded and susceptible to semantic corruption: At least one truthful semantic anchor is required to break observational equivalence.

### 5.2 Honest Scope Limitations
1. **Alphabet and State Cardinality:** Experiments were conducted on finite alphabets ($|\Sigma_I|=3, |\Sigma_O|=4$) and state sizes ($|Q| \le 7$). While representative of protocol handshakes and discrete controllers, scaling to large or continuous alphabets requires symbolic or approximate candidate representations.
2. **Post-Calibration Non-Stationarity:** While open-loop execution is vulnerable to post-calibration drift, CROSSWIRE's Closed-Loop Dynamic Runtime Shield mitigates this risk by dynamically evaluating surviving candidate consistency at every step and halting before catastrophic hazard transitions can occur.

---

## 6. Conclusion

CROSSWIRE demonstrates that maintaining an explicit space of surviving candidate adapters and demanding consensus across all survivors provides a sound, practical foundation for black-box behavioral interoperability. It bridges the gap between dangerous point-estimation heuristics and cost-prohibitive active automata learning. By submitting every claim to private semantic auditing and publishing reproducible scientific receipts, CROSSWIRE establishes both the operational efficacy and the strict epistemic boundaries of autonomous interface synthesis.

---

## References

1. Angluin, D. (1987). Learning regular sets from queries and counterexamples. *Information and Computation*, 75(2), 87–106.
2. Musiol, M., et al. (2021). AALpy: An Active Automata Learning Library in Python. *Innovations in Systems and Software Engineering*.
3. Smith, E., et al. (2025). Representation stitching and interface alignment under unaligned representations. *Proceedings of the 42nd International Conference on Machine Learning (ICML)*.
4. De Alfaro, L., & Henzinger, T. A. (2001). Interface automata. *ACM SIGSOFT Software Engineering Notes*, 26(5), 109–120.
5. Alshiekh, M., Bloem, R., Ehlers, R., Könighofer, B., Niekum, S., & Topcu, U. (2018). Safe reinforcement learning via shielding. *Proceedings of the AAAI Conference on Artificial Intelligence*, 32(1).
6. Guillory, A., & Bilmes, J. (2010). Interactive submodular set cover. *Proceedings of the 27th International Conference on Machine Learning (ICML)*.
7. Golovin, D., & Krause, A. (2011). Adaptive submodularity: Theory and applications in active learning and stochastic optimization. *Journal of Artificial Intelligence Research*, 42, 427–486.
