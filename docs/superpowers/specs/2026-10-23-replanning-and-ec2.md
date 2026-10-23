# Spec: Receding-Horizon Dynamic Replanning, EC2 Active Probing, and Risk-Controlled Version-Space Admission

## 1. Motivation & Background

CROSSWIRE addresses autonomous behavioral interoperability between a known reference interface and an opaque black-box target under unknown permutation mappings. While consensus admission (`robust`) and dynamic runtime shielding (`shielded`, `recovery`) successfully avert hazards, two key limitations remain in current literature and the existing codebase:

1. **Passive Halting vs. Active Replanning in Runtime Assurance:**
   When dynamic runtime shielding intercepts an unexpected observation or impending hazard in `shielded` mode, it immediately aborts. In `recovery` mode, it executes a single-step minimum-hazard fallback and stops. However, intermediate observations prune the candidate version space ($\mathcal{V}_t \subset \mathcal{V}_0$). Many candidate adapters that previously blocked alternative safe plans are now refuted. Under receding-horizon assurance (Alshiekh et al. 2018; Scarbro & Mangal 2026), an intelligent shield should perform **closed-loop online replanning**—discovering and executing a newly verified safe alternative path to the contract goal.

2. **Decision-Directed Active Probing (EC2):**
   Existing heuristic probing policies either optimize output entropy over all individual adapters (`entropy`), count unweighted pair disagreements (`disagreement`), or compute all-pairs Jaccard weights (`task`). But adapters that share the exact same set of contract-admissible plans belong to the same **Contract Equivalence Class**. Probing to separate adapters within the same contract class wastes target budget. Equivalence Class Edge Cutting (EC2; Guillory & Bilmes 2010; Golovin & Krause 2011) partitions candidates into decision classes and prioritizes probes that cut edges *between* differing decision regions, drastically reducing query overhead.

3. **Risk-Controlled Version-Space Admission:**
   Between strict consensus ($\hat{R}_{\text{hazard}} = 0$, which can lead to high abstention under slight noise or minor model deviations) and forced-fit point estimation (which incurs over 60% selective harm), there is a need for calibrated risk-controlling prediction (Bates et al. 2021; Angelopoulos et al. 2022) with explicit finite-sample hazard and goal rates over surviving hypothesis spaces.

---

## 2. Technical Architecture & Invariants

### 2.1 EC2 (Equivalence Class Edge Cutting) Probing Policy
- **Partition:** Given surviving adapters $\mathcal{V}$, partition $\mathcal{V}$ into equivalence classes $\mathcal{E}_1, \dots, \mathcal{E}_m$ where $\alpha \in \mathcal{E}_k \iff \text{safe\_words}(\alpha) = S_k$.
- **Class Distance Weight:** For $i \neq j$, $w(i, j) = \frac{|S_i \Delta S_j|}{\max(1, |S_i \cup S_j|)}$.
- **Class Output Distributions:** For each candidate probe $w$ and each class $\mathcal{E}_i$, let $T_i(p) = |\{\alpha \in \mathcal{E}_i \mid \alpha.\text{predict}(w) = p\}|$.
- **Edge Cut:** $\text{Cut}_{i,j}(w) = |\mathcal{E}_i| \cdot |\mathcal{E}_j| - \sum_p T_i(p) \cdot T_j(p)$.
- **EC2 Score:** $\text{Score}_{\text{EC2}}(w) = \frac{\sum_{i < j} w(i, j) \cdot \text{Cut}_{i,j}(w)}{1 + |w|}$.
- **Complexity:** $O(|\mathcal{P}|^2 \cdot |\Sigma_O|)$ per probe word instead of $O(|\mathcal{V}|^2)$, dramatically reducing compute while focusing on contract-distinguishing actions.

### 2.2 Receding-Horizon Dynamic Replanning Shield (`replan` Mode)
- **Mode:** `replan` added to `EXECUTION_MODES = ('open_loop', 'shielded', 'recovery', 'replan')`.
- **Pre-Step Replan:** Before action $u_{t+1}$, if $u_{t+1}$ risks a hazard under any $\alpha \in \mathcal{V}_t$, search for a safe replanned suffix $w'$ of length $L \in [1, H - t]$ such that $\forall \alpha \in \mathcal{V}_t$, $\mathcal{C}.\text{accepts}(\alpha.\text{semantic}(\text{history} + w')) == \text{True}$.
  - If found: update remaining plan to $w'$, record replan event, and continue executing $w'$.
  - If not found: fall back to conservative recovery if safe, or halt with `INTERVENED_HAZARD_AVERTED`.
- **Post-Step Replan:** After stepping action $u_{t+1}$ and observing $o_{t+1}$, update $\mathcal{V}_{t+1}$. If remaining plan suffix becomes hazardous under any $\alpha \in \mathcal{V}_{t+1}$ or fails to reach the goal:
  - Search for a safe suffix $w'$ under all $\alpha \in \mathcal{V}_{t+1}$ of length $L \in [1, H - (t+1)]$.
  - If found: set status `REPLANNED_ONLINE_SAFE`, update remaining plan, record replan event, and continue.
  - If not found: fall back to conservative recovery or halt.
- **Audit Tracking:** Deployment and audit dictionaries record `replanned: bool`, `replan_count: int`, and `replan_events: list[dict]`.

### 2.3 Risk-Controlled Version-Space Admission (`risk_controlled` Mode)
- **Admission Mode:** `risk_controlled` added to `ADMISSIONS`.
- **Metrics:** For every candidate deployment word $w \in \mathcal{W}_{\le H}$:
  - $\hat{R}_{\text{hazard}}(w; \mathcal{V}) = \frac{1}{|\mathcal{V}|} \sum_{\alpha \in \mathcal{V}} \mathbf{1}[h \in \alpha.\text{semantic}(w)]$
  - $\hat{G}_{\text{goal}}(w; \mathcal{V}) = \frac{1}{|\mathcal{V}|} \sum_{\alpha \in \mathcal{V}} \mathbf{1}[\mathcal{C}.\text{accepts}(\alpha.\text{semantic}(w))]$
- **Admission Criterion:** Word $w$ is admitted if $\hat{R}_{\text{hazard}}(w) \le \epsilon$ and $\hat{G}_{\text{goal}}(w) \ge 1 - \epsilon$ (where $\epsilon \in [0.0, 1.0)$, default $\epsilon = 0.0$ for robust consensus).
- **Selection:** Minimizes length, then minimizes hazard risk, then maximizes goal rate. Emits risk certificate fields.

### 2.4 Workbench & Independent Evidence Verification
- **Evidence Certificate:** `crosswire/certificates.py` validates `risk_controlled` and `replan` modes within certificate scope.
- **UI Workbench:**
  - Option lists include `ec2`, `replan`, `risk_controlled`.
  - Deployment panel highlights online replan detour steps with badges.
  - Public model evidence displays contradiction cores and replanning traces.

---

## 3. Verification Plan
- Unit tests for EC2 probing (`tests/test_ec2.py`).
- Unit tests for receding-horizon replanning shield (`tests/test_replan.py`).
- Unit tests for risk-controlled admission (`tests/test_risk_controlled.py`).
- End-to-end browser regression via Playwright (`tools/check_workbench.cjs`).
- Full test suite execution across all modules (158+ tests passing).
- Empirical comparative benchmark receipt generation and documentation.
