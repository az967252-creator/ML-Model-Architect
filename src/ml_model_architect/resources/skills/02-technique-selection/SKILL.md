---
name: technique-selection
description: "5-level decision tree from preprocessing to optimization strategy. Every option carries pros/cons + reference anchor."
version: "2.1.0"
stage: 2
requires: CONSTITUTION.md
inputs: REQUIREMENTS.md
outputs: TECH-CHOICE.md, PLAN.manifest.json, PLAN.lock
---

# Stage 2 — Technique Selection

## Scope Bounding (Mandatory Boundary)

> ⚠️ **FRAMEWORK SCOPE BOUNDARY:**
> ML Model Architect strictly bounds its architectural reasoning and empirical pipelines to:
> 1. **Tabular Data** (static & streaming tabular records)
> 2. **Tabular Time-Series & Forecasting** (lagged autoregressive features, temporal tabular records)
> 3. **Tabular Anomaly Detection** (unsupervised, semi-supervised outlier detection)
> 4. **Tabular Clustering & Metric Learning**
>
> **Out of Scope Tasks:**
> - Computer Vision (end-to-end CNN/ViT) -> Route to specialized frameworks (e.g., PyTorch Image Models / timm, torchvision).
> - Audio / Speech Processing -> Route to specialized audio frameworks (e.g., torchaudio, Whisper).
> - End-to-End Multimodal / Generative LLM pre-training -> Route to Hugging Face Transformers / vLLM.
> - Reinforcement Learning -> Route to Ray RLlib / Stable-Baselines3.

---

## Input Gate

> **MCP REQUIREMENT:** Before selecting any family, use your MCP tool (OpenAlex/arXiv) to read the actual paper for the chosen group.

REQUIREMENTS.md must exist and pass Stage 1 exit gate.
If not: STOP with message "المرحلة 1 مش مكتملة".

---

## Part A — The Rigorous 5-Level Decision Tree

### Level 1: Preprocessing & Feature Representation
Determine how raw inputs are represented inside a single scikit-learn Pipeline (zero leakage):
- **Missing Value Imputation**: Simple mean/median (heuristic) vs. KNN/Iterative vs. native tree handling.
- **Categorical Encoding**: One-Hot (low-cardinality) vs. Target/James-Stein vs. Native histogram binning (CatBoost/LightGBM).
- **Continuous Feature Scaling**: StandardScaler vs. RobustScaler (for heavy tails/outliers) vs. QuantileTransformer vs. None (tree invariance).
- **Text-as-Tabular**: Bag-of-Words / TF-IDF vs. frozen sentence embeddings.

### Level 2: Data Nature & Temporal Dynamics
Determine the data generation process:
- **Tabular-Static**: Independent, identically distributed records without time coupling.
- **Tabular-Streaming**: Concept drift potential, rolling online metrics required.
- **Time-Series-as-Tabular**: Autoregressive lag features, rolling statistics, calendar embeddings with strict time-based split.
- **Pure Time-Series**: Univariate / multivariate autoregressive state-space models (ARIMA, Exponential Smoothing, DeepAR).

### Level 3: Model Architecture Family
Determine the candidate model families based on empirical strengths:
- **Linear / Generalized Linear**: Fast, convex, highly interpretable baseline (ref-01). Dominates on high-dimensional sparse data.
- **Tree Models (Bagged & Random Forests)**: Robust, minimal tuning, handles non-linearities without scaling (ref-02).
- **Gradient Boosted Trees (XGBoost, LightGBM, CatBoost)**: Current empirical state-of-the-art across tabular benchmarks (ref-03). Dominates on mixed tabular data.
- **Tabular Deep Learning (FT-Transformer, SAINT)**: Effective when combining dense tabular features with text/embeddings or semi-supervised transfer (ref-04).
- **Tabular Foundation Models (TabPFN)**: Instant inference without gradient tuning for small datasets (N < 10,000) (ref-05).
- **Distance-Based / Metric Learning (k-NN, SVM)**: Local geometry, small sample regimes (ref-06, ref-07).
- **Specialized Unsupervised (Isolation Forest, HDBSCAN, PCA)**: Anomaly detection and clustering (ref-09, ref-10, ref-11).

### Level 4: Loss Function & Regularization
Select objective aligned with Stage 1 business metric:
- **Regression**: Mean Squared Error (MSE) vs. Huber loss (outlier robust) vs. Quantile loss (asymmetric cost).
- **Classification**: Binary/Multiclass Cross-Entropy vs. Focal loss (severe class imbalance) vs. Weighted Cross-Entropy.
- **Regularization Penalty**: L1 (Lasso, sparse selection) vs. L2 (Ridge, collinear grouping) vs. Elastic Net combination.

### Level 5: Optimization & Search Strategy
Determine the hyperparameter search and complexity control strategy:
- **Deterministic Baseline**: Default reference hyperparameters.
- **1-SE Complexity Sweep**: Hastie et al. 1-SE rule over complexity parameter (C, alpha, max_depth).
- **Bayesian Optimization**: Optuna Tree-structured Parzen Estimator (TPE) bounded inside Docker sandbox.

---

## Part B — Option Display Format (Mandatory)

```markdown
Why now: <one line explaining current level decision>
Question: <the question>

  A) <option name> (heuristic suggestions permitted for options A/B/C per Rule A1)
     Strengths: <list>
     Weaknesses: <list>
     Best for: <when this wins>
     Reference Anchor: <DOI @ locator or (heuristic)>

  B) ...
  C) ...

  D) خيار تاني (اكتبه)
  E) مش عارف
```

Rules:
- 3 options (heuristically structured if labeled) + "خيار تاني" + "مش عارف".
- Every option has strengths, weaknesses, and a reference anchor or `(heuristic)`.
- Final selected decision MUST be verified against the peer-reviewed reference.

---

## Part C — Lazy Reference Loading

- Load `references/stage-2-selection/ref-00-index.md` first.
- Load `ref-XX-*.md` ONLY when the user reaches that group.

---

## Part D — Exclusion Transparency

For each excluded family or representation, show one clear line:
`"استبعدنا <family> لأن <reason from Stage 1 constraints>."`

---

## Part E — Exit Gate

- [ ] Representation & preprocessing strategy specified (Level 1).
- [ ] Data nature & temporal dynamics agreed (Level 2).
- [ ] Baseline model and Candidate model families selected (Level 3).
- [ ] Loss function and regularizer defined (Level 4).
- [ ] Optimization and 1-SE rule protocol defined (Level 5).
- [ ] Deterministic plan compiled into `PLAN.manifest.json` (from `_shared/TEMPLATE-PLAN-MANIFEST.json`).
- [ ] Plan locked cryptographically: `python scripts/lock_plan.py PLAN.manifest.json`.
- [ ] Lock verified: `python scripts/run_policy.py verify PLAN.manifest.json`.
