<img width="100%" height="887" alt="ML Model Architect Banner" src="https://github.com/user-attachments/assets/0b1e73e0-f551-4ca2-be93-569b1f54db91" />

<div align="center">

# ML Model Architect

### A strict, reference-driven framework that turns AI agents into disciplined, expert ML engineers.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![MCP Ready](https://img.shields.io/badge/MCP-Ready-purple.svg?style=flat-square)](https://modelcontextprotocol.io)
[![Zero-Paywall](https://img.shields.io/badge/Zero--Paywall-B8-blue.svg?style=flat-square)](#zero-paywall-and-sota-discovery-rules-b8--b9)
[![Sandboxed](https://img.shields.io/badge/Sandboxed-F4-red.svg?style=flat-square)](#security-and-sandboxing-rules-f4--f41)
[![Stages: 5](https://img.shields.io/badge/stages-5-orange.svg?style=flat-square)](#the-5-stages-of-ml-architecture)
[![References: 12 groups](https://img.shields.io/badge/references-12%20groups-teal.svg?style=flat-square)](#repository-structure)

*"Grounded ML: Verifiable references driving empirical validation."*

</div>

---

## Table of Contents

- [The Problem We Solve](#the-problem-we-solve)
- [Core Principle](#core-principle)
- [Proof of Value](#proof-of-value)
- [The 5 Stages of ML Architecture](#the-5-stages-of-ml-architecture)
- [Quick Start](#quick-start)
- [MCP Setup (Mandatory for Strict Mode)](#mcp-setup-mandatory-for-strict-mode)
- [Zero-Paywall and SOTA Discovery (Rules B8 & B9)](#zero-paywall-and-sota-discovery-rules-b8--b9)
- [Security and Sandboxing (Rules F4 & F4.1)](#security-and-sandboxing-rules-f4--f41)
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

ML Model Architect addresses this by placing the agent under a strict constitution: every non-mechanical decision must be backed by a verified reference, or the workflow stops.

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

## Proof of Value

Check out [`BENCHMARK.md`](BENCHMARK.md) for a side-by-side comparison of how an AI agent behaves with and without this framework.

## Illustrative Example

*(Note: The following transcript is an illustrative example to show the interaction flow, not a recorded log of a specific model run.)*

**Without ML Model Architect:**
> *User:* "Build a model for car prices."
> *Agent:* "Sure, here is a Random Forest with default parameters." (No citations, no leakage check).

**With ML Model Architect:**
> *User:* "Build a model for car prices."
> *Agent:* "Let's start Stage 1. What is the business metric? ... Now moving to Stage 2. I recommend Linear Regression based on the baseline CV results. Before I proceed, let me verify the DOI via MCP... Now, Stage 3: I will use a Pipeline to prevent data leakage."

---

## The 5 Stages of ML Architecture

| # | Stage | What Happens | Output Artifact |
|:---:|:---|:---|:---|
| **1** | **Goals & Requirements** | A dynamic MCQ engine extracts business goals from a vague request. | `REQUIREMENTS.md` |
| **2** | **Technique Selection** | A 5-level decision tree. Every option carries pros, cons, and a reference anchor. | `TECH-CHOICE.md` |
| **3** | **Building & Training** | Code generation strictly guided by the academic paper. A single `Pipeline`, no leakage. | `TRAINING-REPORT.md` |
| **4** | **Evaluation & Diagnosis** | Metrics, nested CV, leakage checks. | `EVALUATION-REPORT.md` |
| **5** | **Deployment & Monitoring** | Strategy selection (Shadow / Canary / Blue-Green), drift alerts, and retraining policy. | `DEPLOYMENT-REPORT.md` |

---

## Quick Start

### 1. Clone and open
~~~bash
git clone https://github.com/az967252-creator/ML-Model-Architect.git
cd ML-Model-Architect
~~~

### 2. Configure MCP (required for strict mode)
Follow the MCP Setup section below. Without MCP, the agent cannot fetch live references.

### 3. Prompt your AI agent
~~~text
You are now ML-Model-Architect.
1. Read _constitution/CONSTITUTION.md first.
2. Read skills/01-goals-and-requirements/SKILL.md next.
3. Follow all rules strictly. Start Stage 1.
~~~

---

## MCP Setup (Mandatory for Strict Mode)

The recommended server is **`openresearch-mcp`**.

<details>
<summary><b>Expand MCP setup instructions for your IDE</b></summary>

### 1. Cursor
Project-level: `.cursor/mcp.json` — Global: `~/.cursor/mcp.json`
~~~json
{"mcpServers": {"openresearch": {"command": "uvx", "args": ["openresearch-mcp@0.2.0", "--stdio"]}}}
~~~

### 2. Windsurf (Codeium)
File: `~/.codeium/windsurf/mcp_config.json`
~~~json
{"mcpServers": {"openresearch": {"command": "uvx", "args": ["openresearch-mcp@0.2.0", "--stdio"]}}}
~~~

### 3. Google Antigravity
Global: `~/.gemini/config/mcp_config.json` — Project: `.antigravity/mcp_config.json`
~~~json
{"mcpServers": {"openresearch": {"command": "uvx", "args": ["openresearch-mcp@0.2.0", "--stdio"]}}}
~~~

### 4. VS Code (GitHub Copilot)
File: `.mcp.json` at the root of your workspace
~~~json
{"mcpServers": {"openresearch": {"command": "uvx", "args": ["openresearch-mcp@0.2.0", "--stdio"]}}}
~~~

### 5. Cline (VS Code Extension)
File: `~/.cline/data/settings/cline_mcp_settings.json`
~~~json
{"mcpServers": {"openresearch": {"command": "uvx", "args": ["openresearch-mcp@0.2.0", "--stdio"]}}}
~~~

### 6. Claude Code (CLI)
~~~bash
claude mcp add openresearch -- uvx openresearch-mcp@0.2.0 --stdio
~~~

### 7. Claude Desktop
File: `%APPDATA%\Claude\claude_desktop_config.json`
~~~json
{"mcpServers": {"openresearch": {"command": "uvx", "args": ["openresearch-mcp@0.2.0", "--stdio"]}}}
~~~

</details>

> If a paper is paywalled, the agent follows a fixed protocol: search arXiv, then Unpaywall. Amended by Rule B8: if both fail, it escalates to `trusted_domains.yaml`.

> **⚠️ MCP Security Warning**: 
> The `openresearch-mcp` tool fetches content from the internet. Always pin the version (e.g., `openresearch-mcp@0.2.0` with `uvx`) and review the fetched text before executing code.

---

## Zero-Paywall and SOTA Discovery (Rules B8 & B9)

- **Zero-Paywall.** If a paper is paywalled, the AI pivots to `trusted_domains.yaml` and logs it as `institutional-whitelist`. It never stops.
- **Dynamic SOTA.** Before finalizing a technique, the AI uses MCP to search arXiv for papers from the last 6 months. A GitHub Action runs monthly to fetch new references.

---

## Security and Sandboxing (Rules F4 & F4.1)

1. The AI is **forbidden** from executing generated code. It must write it to `/sandbox/` and wait for human review.
2. You must run `python scripts/scan_sandbox.py` before executing anything from `/sandbox/`.

---

## Repository Structure

~~~text
ML-Model-Architect/
|-- _constitution/          # Rules A-F
|-- skills/                 # 5 sequential stages
|-- references/             # 12 ML groups x 3 stages
|-- _shared/                # Output templates
|-- scripts/                # verify_dois, scan_sandbox, fetch_sota
|-- tests/                  # Mocked unit tests (test_skills, test_verify)
|-- sandbox/                # AI-generated code for human review
|-- examples/               # Full end-to-end examples
|-- trusted_domains.yaml    # Zero-Paywall whitelist
|-- references_to_verify.yaml
|-- requirements.txt
`-- README.md
~~~

---

## Reference Rigor — The 6 Criteria

| # | Criterion | What It Means |
|:---:|:---|:---|
| 1 | **Peer review** | Published in a journal or conference — not a blog, course, or tutorial. |
| 2 | **Currency** | 2024 to 2026, except for foundational classics (e.g., XGBoost). |
| 3 | **Citations** | Clear, traceable reference list. |
| 4 | **Transparency** | Methodology is visible enough to reproduce. |
| 5 | **Integrity** | No retraction record and no undisclosed conflict of interest. |
| 6 | **Relevance** | Directly answers the question at hand. |

### Hierarchical Reference Escalation
Level 0: Stage-specific file -> Level 1: Core databases -> Level 2: Sibling groups -> Level 3: PRISMA 2020 -> Level 4: Meta-analysis -> Level 5: STOP (Reference Gap).

---

## The Constitution at a Glance

| Part | Domain | Key Rule |
|:---:|:---|:---|
| **A** | Decision philosophy | Propose 2-3 options; user decides. No silent assumptions. |
| **B** | Reference is the Judge | No technical decision without a reference anchor. |
| **C** | Token economics | Lazy context loading, stable prefixes for caching. |
| **D** | Stage gates | Input, Reference, Verification, Token, Exit. |
| **E** | Violation handling | If the agent breaks a rule, it stops and asks. |
| **F** | Mandatory search | Read the actual source via MCP, never memory alone. |

---

## Contributing
Please see [CONTRIBUTING.md](./CONTRIBUTING.md).

## Requirements
- Any AI agent with file access.
- Python 3.10+.
- `uvx`.

To run the validation scripts: `pip install -r requirements.txt`.

## License
This project is licensed under the **MIT License**. See the [`LICENSE`](./LICENSE) file for details.
