# Getting Started with ML Model Architect

This guide will get you from zero to your first strictly grounded, reference-driven AI ML project in under 10 minutes.

---

## Prerequisites
- Python 3.10+
- An AI IDE or coding agent (Cursor, Windsurf, Claude Code, Antigravity, VS Code, etc.)
- `uv` or `uvx` installed (for MCP literature retrieval)

---

## Step 1: Install the Framework CLI

Clone the repository and install the unified CLI tool:

~~~bash
git clone https://github.com/az967252-creator/ML-Model-Architect.git
cd ML-Model-Architect

# Install package in editable mode
pip install -e .

# Test that the CLI is ready:
mla --version
# (or use ./bin/mla on Windows/Linux)
~~~

---

## Step 2: Configure MCP (Mandatory for Live Literature)

The AI needs access to academic research databases to search arXiv and CrossRef without paywalls.
Add the following configuration to your IDE's MCP settings file:

~~~json
{
  "mcpServers": {
    "openresearch": {
      "command": "uvx",
      "args": ["openresearch-mcp@0.2.0", "--stdio"]
    }
  }
}
~~~

*Restart your IDE to load the MCP server.*

---

## Step 3: Start the Agent

Open the repository folder in your IDE and paste this prompt:

~~~text
You are now ML-Model-Architect.
1. Read _constitution/CONSTITUTION.md first.
2. Read skills/01-goals-and-requirements/SKILL.md next.
3. Follow all rules strictly.
4. Start Stage 1 for a new project: "Predicting Delivery Delays".
~~~

---

## Step 4: Answer the Grounding MCQ Questions (Stage 1)

The agent will **not** write code immediately. It will ask 5 structured MCQ questions covering:
1. Business problem & objective
2. Target definition & data pattern
3. Latency & hardware constraints
4. Cost priority (precision vs. recall)
5. Metric floor

Once answered, the agent generates `REQUIREMENTS.md` and initializes `DECISIONS.md`.

---

## Step 5: Technique Selection & Immutable Plan Locking (Stage 2)

1. The agent queries arXiv/CrossRef via MCP to identify state-of-the-art algorithms from the last 6 months.
2. It presents 2–3 candidate architectures with explicit tradeoffs and baseline floors.
3. Once you approve, it compiles the execution DAG into `PLAN.manifest.json`.
4. The plan is cryptographically locked via SHA-256:

~~~bash
# Lock the plan manifest to prevent unauthorized step skipping
mla plan lock PLAN.manifest.json
~~~

---

## Step 6: Grounded ReAct Loop in Sandbox (Stage 3)

The agent enters the self-correcting **Grounded ReAct Loop**:
- **THINK:** Analyzes client constraints and literature anchors.
- **ACT:** Writes clean scikit-learn `Pipeline` code to `/sandbox/`.
- **OBSERVE:** Runs 5-fold cross-validation and checks AST security:

~~~bash
# Check code security before execution
mla scan sandbox/pipeline.py

# Check execution step status
mla status PLAN.manifest.json
~~~

---

## Step 7: 1-SE Empirical Model Selection (Stage 4 & 5)

The agent compares candidate models against the baseline using the empirical 1-SE rule (Hastie et al., 2009):
- It outputs `EVALUATION-REPORT.md` selecting the simplest model within 1 standard error of the best score.
- It formulates `DEPLOYMENT-REPORT.md` with shadow/canary strategies and drift thresholds.

---

## Step 8: Visualize in the Governance Dashboard

Monitor all project artifacts, decision ledgers, and plan locks in real time:

~~~bash
mla dashboard
# (or: streamlit run app.py)
~~~

---

## Completed Reference Projects

To explore complete, runnable examples with manifests, reports, and pipelines:
- `examples/car-price-prediction/` (Tabular regression with non-linear interactions)
- `examples/delivery-delay-prediction/` (Tabular binary classification with high-recall priority)
- `examples/financial-anomaly-detection/` (Extreme imbalanced anomaly detection)
- `examples/case-study-churn/` (Telecom subscription churn with stratified cross-validation)
