# Autonomous Model-Class Escalation, Information-Theoretic Probing, and Simplex Recovery Shielding

## Intent and Mathematical Formulation

This specification extends CROSSWIRE along three complementary formal dimensions:
1. **Information-Theoretic Active Learning (`entropy`):** Probing by maximizing Shannon observation entropy over the surviving candidate version space.
2. **Automated Structural Model-Class Escalation (`escalate`):** Autonomous Structural Risk Minimization (SRM) that begins in the minimal static hypothesis class $\mathcal{H}_0$ ($|\mathcal{A}|=144$) and automatically escalates to temporal latency space $\mathcal{H}_1$ ($|\mathcal{A}|=720$) upon empirical refutation, with a formal Structural Contradiction Diagnosis Certificate if all declared classes fail.
3. **Simplex Safe Fallback & Recovery Shielding (`recovery`):** Extends runtime shielding beyond passive halting to active fail-safe recovery, executing certified non-hazardous recovery actions when an interface anomaly is detected.

---

## 1. Information-Theoretic Probing (`entropy`)

### 1.1 Formal Definition
Given calibration evidence $D$ with surviving candidate adapter set $\mathcal{V} \subseteq \mathcal{A}$:
For any candidate probe sequence $w \in \Sigma_I^{\le K}$:
Each candidate adapter $\alpha \in \mathcal{V}$ predicts an output sequence:
$$\hat{o}_\alpha = \text{predict}(\alpha, w) \in \Sigma_O^{|w|}$$
The empirical predictive distribution over observable sequences is:
$$p(o \mid w, \mathcal{V}) = \frac{1}{|\mathcal{V}|} \sum_{\alpha \in \mathcal{V}} \mathbb{I}[\text{predict}(\alpha, w) = o]$$
The Shannon observation entropy is:
$$H(O \mid w, \mathcal{V}) = -\sum_{o \in \text{supp}(p)} p(o \mid w, \mathcal{V}) \log_2 p(o \mid w, \mathcal{V})$$
The optimal entropy probe is:
$$w^* = \arg\max_{w \in \mathcal{W}_{\text{candidate}}} H(O \mid w, \mathcal{V})$$
Ties are broken deterministically by $(H, -|w|, w)$.

### 1.2 Guarantees
- If all surviving candidates agree on $w$, $H(O \mid w, \mathcal{V}) = 0$; the probe is guaranteed uninformative and will not be selected.
- Maximum entropy $H(O \mid w, \mathcal{V}) = \log_2 |\Sigma_O|^{|w|}$ indicates an equiprobable partitioning of the version space across all possible observations, halving uncertainty in the minimum expected number of queries.

---

## 2. Automated Structural Model-Class Escalation

### 2.1 Nested Hypothesis Hierarchy
Define a hierarchy of increasingly expressive interface hypothesis classes:
$$\mathcal{H}_0 \subset \mathcal{H}_1$$
where:
- $\mathcal{H}_0$: Static bijective permutations $|\Sigma_I|! \times |\Sigma_O|! = 144$, latency $d=0$. Structural complexity $C(\mathcal{H}_0) = 0$.
- $\mathcal{H}_1$: Temporal latency-aware permutations with one-step output delay buffer $d \in \{0, 1\}$ and initial buffer conditions $|\mathcal{A}|=720$. Structural complexity $C(\mathcal{H}_1) = 1$.

### 2.2 Escalation Protocol
1. Initialize CandidateSpace at $\mathcal{H}_0$.
2. At every query step $t$, filter survivors $\mathcal{V}_0(D_t) = \{\alpha \in \mathcal{H}_0 : \text{loss}(\alpha, D_t) = 0\}$.
3. If $\mathcal{V}_0(D_t) \neq \emptyset$: Proceed with probing or plan admission inside $\mathcal{H}_0$.
4. If $\mathcal{V}_0(D_t) = \emptyset$ (empirical refutation of static interfaces):
   - Trigger automated escalation to $\mathcal{H}_1$.
   - Re-evaluate all historical evidence $D_t$ against $\mathcal{H}_1$:
     $$\mathcal{V}_1(D_t) = \{\alpha \in \mathcal{H}_1 : \text{loss}(\alpha, D_t) = 0\}$$
   - If $\mathcal{V}_1(D_t) \neq \emptyset$: Resume active probing and admission in $\mathcal{H}_1$, recording `escalation_level = 1`.
   - If $\mathcal{V}_1(D_t) = \emptyset$: Emit `FAMILY_CONTRADICTED` with a `StructuralContradictionCertificate` proving that no model in $\mathcal{H}_0 \cup \mathcal{H}_1$ is consistent with the observed trace.

---

## 3. Simplex Safe Fallback & Recovery Shielding (`recovery`)

### 3.1 Motivation
In safety-critical runtime enforcement (Simplex Architecture; Sha 2001, Bloem et al. 2015), when a primary controller's assumptions are refuted by runtime observations, passive termination can leave the physical plant in a vulnerable, intermediate, or non-quiescent state.

### 3.2 Recovery Protocol
When the shield detects an observation anomaly (output refuting all surviving candidates) or pre-step model risk:
1. Set `shield_status = "INTERVENED_ANOMALY"`.
2. Instead of immediate unguided termination, the shield enters **Fail-Safe Recovery**:
   - Searches for an action $a_{\text{rec}} \in \Sigma_I$ that is certified hazard-free under all reference transitions and emits a recognized quiescent or reset response.
   - Dispatches $a_{\text{rec}}$ to the target process.
   - If $a_{\text{rec}}$ executes without hazard, marks `recovery_succeeded = True` and updates status to `RECOVERED_SAFE_FALLBACK`.
   - If no recovery action is certified safe or the recovery step encounters a fault, halts cleanly with `recovery_succeeded = False`.

---

## 4. Verification and Replay Constraints

1. Zero external network/cloud dependencies; CPU-local deterministic execution.
2. Cryptographic binding: receipts must bind `escalate`, `recovery`, and `entropy` configurations.
3. Replaying any study or run must reproduce all scientific metrics, escalation transitions, and audits bitwise.
4. Backward compatibility: all existing 109 tests must continue to pass without regression.
