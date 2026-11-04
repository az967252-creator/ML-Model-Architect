<img width="1774" height="887" alt="8572272b-8871-4159-a90d-5261300b8763" src="https://github.com/user-attachments/assets/0b1e73e0-f551-4ca2-be93-569b1f54db91" />

<div align="center">

# ML Model Architect

### A strict, reference-driven framework that turns AI agents into disciplined, expert ML engineers.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![MCP Ready](https://img.shields.io/badge/MCP-Ready-purple.svg?style=flat-square)](https://modelcontextprotocol.io)
[![Stages: 5](https://img.shields.io/badge/stages-5-orange.svg?style=flat-square)](#the-5-stages-of-ml-architecture)
[![References: 12 groups](https://img.shields.io/badge/references-12%20groups-teal.svg?style=flat-square)](#repository-structure)

*"Stop the AI hallucination. Force it to read the papers."*

</div>

---

## Table of Contents

- [The Problem We Solve](#the-problem-we-solve)
- [Core Principle](#core-principle)
- [The 5 Stages of ML Architecture](#the-5-stages-of-ml-architecture)
- [Quick Start](#quick-start)
- [MCP Setup (Mandatory for Strict Mode)](#mcp-setup-mandatory-for-strict-mode)
- [Repository Structure](#repository-structure)
- [Reference Rigor — The 6 Criteria](#reference-rigor--the-6-criteria)
- [The Constitution at a Glance](#the-constitution-at-a-glance)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [License](#license)

---

## The Problem We Solve

AI coding agents move fast, and speed without verification creates real risk. Left unchecked, an agent will commonly:

- Invent hyperparameters that sound plausible but trace back to no published source.
- Pick evaluation metrics from memory rather than from the actual data distribution.
- Skip leakage checks because nothing in the workflow forces the question.
- Choose a deployment strategy without consulting any MLOps literature.

The result is a model that runs, but whose design decisions nobody can defend after the fact.

ML Model Architect addresses this by placing the agent under a constitution it cannot bypass: every non-mechanical decision must be backed by a verified reference, or the workflow stops.

> Built for engineers who care about how the model was built — not just the code.

---

## Core Principle

> **"The Reference Is the Judge."**
> Every technical decision must have a verified citation. No reference means **STOP** and record a *Reference Gap*. **Never invent.**

In practice, this framework makes the agent do four things it would not do on its own:

1. **Stop guessing** — ask the right questions before writing any code.
2. **Read the actual papers** — through the Model Context Protocol (MCP), not from memory.
3. **Anchor every architectural decision** to peer-reviewed research.
4. **Log every choice** in a Decision Ledger that can be audited later.

---

## The 5 Stages of ML Architecture

Each stage is a self-contained skill with its own input gate, exit checklist, and reference anchor. The agent cannot move forward until the previous stage is complete and approved.

| # | Stage | What Happens | Output Artifact |
|:---:|:---|:---|:---|
| **1** | **Goals & Requirements** | A dynamic MCQ engine extracts business goals from a vague request. All 11 knowledge items must be confirmed. | `REQUIREMENTS.md` |
| **2** | **Technique Selection** | A 5-level decision tree: task type, then data nature, priority, size, and finally the family. Every option carries pros, cons, and a reference anchor. | `TECH-CHOICE.md` |
| **3** | **Building & Training** | Code generation strictly guided by the academic paper for the selected group. A single `Pipeline`, no leakage, tracked in MLflow. | `TRAINING-REPORT.md` |
| **4** | **Evaluation & Diagnosis** | Metrics, nested CV, leakage checks, and bootstrap confidence intervals. Weaknesses are diagnosed using a referenced *Problem Catalog*. | `EVALUATION-REPORT.md` |
| **5** | **Deployment & Monitoring** | Strategy selection (Shadow / Canary / Blue-Green), drift alerts, and retraining policy — all backed by MLOps research. | `DEPLOYMENT-REPORT.md` |

```
Stage 1 --> Stage 2 --> Stage 3 --> Stage 4 --> Stage 5
  Goals      Technique    Training    Evaluation   Deployment
   |            |             |            |            |
   v            v             v            v            v
REQUIREMENTS  TECH-CHOICE  TRAINING    EVALUATION  DEPLOYMENT
    .md          .md       -REPORT.md  -REPORT.md  -REPORT.md
```

---

## Quick Start

### 1. Clone and open

```bash
git clone https://github.com/az967252-creator/ML-Model-Architect.git
cd ML-Model-Architect
```

Open the folder in the AI IDE of your choice: Cursor, Windsurf, Claude Code, VS Code with Copilot, Cline, or Aider.

### 2. Configure MCP (required for strict mode)

Follow the [MCP Setup](#mcp-setup-mandatory-for-strict-mode) section below. Without MCP, the agent cannot read papers directly and will fall back to *Fast Mode*, which produces no live citations.

### 3. Prompt your AI agent

Paste this as your first message:

```
You are now ML-Model-Architect.

1. Read _constitution/CONSTITUTION.md first.
2. Read skills/01-goals-and-requirements/SKILL.md next.
3. Follow all rules strictly.
4. Start Stage 1.
```

### 4. Answer the agent's questions

The agent will refuse to write code until it has enough information, and it will cite its sources at every step. Each stage produces a detailed Markdown report that you keep.

> Note: the agent converses in Egyptian Arabic (per `CONSTITUTION.md`, rule A5). All structural files — YAML, code, and reports — remain in English.

---

## MCP Setup (Mandatory for Strict Mode)

To enforce the *Reference is the Judge* rule, the agent must be able to read research papers directly from the internet using the **Model Context Protocol (MCP)**. The recommended server is **`openresearch-mcp`** — zero-auth and security-hardened.

<details>
<summary><b>Expand MCP setup instructions for your IDE</b></summary>

### 1. Cursor
Project-level: `.cursor/mcp.json` — Global: `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "openresearch": {
      "command": "uvx",
      "args": ["openresearch-mcp", "--stdio"]
    }
  }
}
```

### 2. Windsurf (Codeium)
File: `~/.codeium/windsurf/mcp_config.json`

```json
{
  "mcpServers": {
    "openresearch": {
      "command": "uvx",
      "args": ["openresearch-mcp", "--stdio"]
    }
  }
}
```

### 3. Google Antigravity
Global: `~/.gemini/config/mcp_config.json` — Project: `.antigravity/mcp_config.json`

```json
{
  "mcpServers": {
    "openresearch": {
      "command": "uvx",
      "args": ["openresearch-mcp", "--stdio"]
    }
  }
}
```

### 4. VS Code (GitHub Copilot)
File: `.mcp.json` at the root of your workspace

```json
{
  "mcpServers": {
    "openresearch": {
      "command": "uvx",
      "args": ["openresearch-mcp", "--stdio"]
    }
  }
}
```

### 5. Cline (VS Code Extension)
File: `~/.cline/data/settings/cline_mcp_settings.json`

```json
{
  "mcpServers": {
    "openresearch": {
      "command": "uvx",
      "args": ["openresearch-mcp", "--stdio"]
    }
  }
}
```

### 6. Claude Code (CLI)
A single command in your terminal:

```bash
claude mcp add openresearch -- uvx openresearch-mcp --stdio
```

### 7. Claude Desktop
File: `%APPDATA%\Claude\claude_desktop_config.json` (Windows) — `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "openresearch": {
      "command": "uvx",
      "args": ["openresearch-mcp", "--stdio"]
    }
  }
}
```

</details>

> If a paper is paywalled, the agent follows a fixed protocol: search arXiv, then Unpaywall, then stop and inform the user. It never silently substitutes a weaker source.

---

## Repository Structure

```
ML-Model-Architect/
|
|-- _constitution/                  # Global rules, loaded on every turn
|   `-- CONSTITUTION.md             # The constitution the agent cannot bypass
|
|-- skills/                         # 5 sequential stages, one SKILL.md each
|   |-- 01-goals-and-requirements/
|   |-- 02-technique-selection/
|   |-- 03-building-and-training/
|   |-- 04-evaluation-and-diagnosis/
|   `-- 05-deployment-and-monitoring/
|
|-- references/                     # 12 ML algorithm groups x 3 stages + deployment
|   |-- stage-2-selection/          # ref-00-index.md through ref-12
|   |-- stage-3-training/           # training-01 through training-12
|   |-- stage-4-evaluation/         # eval-01 through eval-12
|   `-- stage-5-deployment/         # deploy-monitor-common.md + by-type.md
|
|-- _shared/                        # 6 reusable output templates
|   |-- TEMPLATE-DECISION-LEDGER.md
|   |-- TEMPLATE-REQUIREMENTS.md
|   |-- TEMPLATE-TECH-CHOICE.md
|   |-- TEMPLATE-TRAINING-REPORT.md
|   |-- TEMPLATE-EVALUATION-REPORT.md
|   `-- TEMPLATE-DEPLOYMENT-REPORT.md
|
|-- scripts/                        # Verification helpers
|   |-- verify_dois.py              # Checks every DOI/URL is alive
|   |-- inspect_repo.py             # Audits repo structure
|   `-- verify_references.py        # Re-runs the 6-criteria gate
|
|-- projects/                       # Per-project ledgers, created at runtime
|   `-- <your-project>/
|       `-- DECISIONS.md            # Every decision lives here, or it did not happen
|
|-- references_to_verify.yaml       # Queue of references pending audit
|-- LICENSE
`-- README.md
```

---

## Reference Rigor — The 6 Criteria

The agent rejects any source that fails even one of the six criteria below. All six must pass together.

| # | Criterion | What It Means |
|:---:|:---|:---|
| 1 | **Peer review** | Published in a journal or conference — not a blog, a course, or a tutorial. |
| 2 | **Currency** | 2024 to 2026, except for foundational classics such as the original XGBoost or Adam papers. |
| 3 | **Citations** | The source itself carries a clear, traceable reference list. |
| 4 | **Transparency** | The methodology is visible enough to reproduce or critique. |
| 5 | **Integrity** | No retraction record and no undisclosed conflict of interest. |
| 6 | **Relevance** | Directly answers the question at hand, not something adjacent. |

A source that fails any criterion is logged under **Rejected Sources** and is never cited.

### Hierarchical Reference Escalation

When the stage-specific reference file does not cover a decision, the agent climbs six levels before declaring a *Reference Gap*:

```
Level 0   Stage-specific reference file
Level 1   General core databases (IEEE, ACM, Springer, ScienceDirect, PubMed), PRISMA search
Level 2   Sibling group references, the related algorithm family
Level 3   External systematic search, PRISMA 2020 protocol
Level 4   Existing systematic review or meta-analysis
Level 5   STOP. Reference Gap recorded in DECISIONS.md
```

---

## The Constitution at a Glance

`_constitution/CONSTITUTION.md` is the highest-authority file in the repository. If any skill contradicts it, the constitution wins.

| Part | Domain | Key Rule |
|:---:|:---|:---|
| **A** | Decision philosophy | Propose two to three options; the user decides. No silent assumptions. |
| **B** | Reference is the Judge | No technical decision without a reference anchor. Six-level escalation. |
| **C** | Token economics | Lazy context loading, stable prefixes for caching, a per-stage budget. |
| **D** | Stage gates | Input, Reference, Verification, Token, Exit — five gates, each able to halt the workflow. |
| **E** | Violation handling | If the agent is about to break a rule, it stops, names the rule, and asks. |
| **F** | Mandatory external search | Decisions require reading the actual source via MCP, never memory alone. |

> The failure mode this constitution exists to prevent is the silent violation. The agent is required to surface any rule it is about to break, not flag it after the fact.

---

## Requirements

| Requirement | Why |
|:---|:---|
| Any AI agent with file access | Claude Code, Cursor, Windsurf, Aider, Cline, or GitHub Copilot |
| Python 3.9 or newer | For the verification scripts in `scripts/` |
| `uvx` or `npx` | To run the MCP server, `openresearch-mcp` |

There is no backend, no database, and no install step beyond cloning the repository.

---

## Contributing

Pull requests are welcome. Before submitting, please:

1. Run the verification scripts. `python scripts/verify_references.py` must pass.
2. Update the Decision Ledger for any constitutional change you propose.
3. Cite your sources. Even documentation changes should be anchored to a reference.
4. Keep the established language split. Chat-style descriptions may be in Egyptian Arabic; code, YAML, and reference files remain in English.

See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the full checklist, if present.

---

## License

This project is licensed under the **MIT License**. See the [`LICENSE`](./LICENSE) file for details.

You are free to use, modify, and distribute this framework. If you build something valuable with it, a mention is appreciated but not required.

---

<div align="center">

**Built for engineers who care about how the model was built — not just the code.**

If this framework has been useful in your work, consider giving it a star.

[Report an issue](https://github.com/az967252-creator/ML-Model-Architect/issues) — [Request a stage](https://github.com/az967252-creator/ML-Model-Architect/issues/new) — [MIT License](https://opensource.org/licenses/MIT)

</div>
