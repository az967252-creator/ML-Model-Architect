<div align="center">

# 🏛️ ML Model Architect

**A strict, reference-driven framework that turns AI agents into disciplined, expert ML engineers.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![MCP Ready](https://img.shields.io/badge/MCP-Ready-purple.svg)](https://modelcontextprotocol.io)

*Stop the AI hallucination. Force it to read the papers.*

</div>

---

## 🧠 Core Principle

> **"The Reference Is the Judge."** 
> Every technical decision must have a verified citation. No reference means **STOP** and record a "Reference Gap". **Never invent.**

This framework forces AI agents (like Cursor, Claude Code, Windsurf) to stop guessing, start asking the right questions, and back every architectural decision with peer-reviewed academic research.

---

## 🚀 The 5 Stages of ML Architecture

| # | Stage | What Happens? | Output File |
|:---:|:---|:---|:---|
| **1** | **Goals & Requirements** | The AI asks dynamic MCQ questions to extract business goals. | `REQUIREMENTS.md` |
| **2** | **Technique Selection** | The AI navigates a 5-level decision tree based on the data. | `TECH-CHOICE.md` |
| **3** | **Building & Training** | Code generation strictly guided by academic papers. | `TRAINING-REPORT.md` |
| **4** | **Evaluation & Diagnosis** | Error analysis using a referenced "Problem Catalog". | `EVALUATION-REPORT.md` |
| **5** | **Deployment & Monitoring** | Strategy selection (Canary/Shadow) backed by MLOps research. | `DEPLOYMENT-REPORT.md` |

---

## ⚡ Quick Start

**1. Clone the repository and open it in your favorite AI IDE.**

~~~bash
git clone https://github.com/az967252-creator/ML-Model-Architect.git
cd ML-Model-Architect
~~~

**2. Prompt your AI Agent (Cursor, Claude Code, etc.) with:**

~~~text
You are now ML-Model-Architect. 
Read _constitution/CONSTITUTION.md first.
Read skills/01-goals-and-requirements/SKILL.md next.
Follow all rules strictly. Start Stage 1.
~~~

**3. Answer the Agent's Questions.** 
The AI will refuse to write code until it has enough information, and it will cite its sources. Every stage produces a detailed Markdown report.

---

## 🔌 MCP Setup (Mandatory for Strict Mode)

To enforce the "Reference is the Judge" rule, the AI must be able to read research papers directly from the internet using the **Model Context Protocol (MCP)**. The recommended server is **`openresearch-mcp`** (zero-auth, security-hardened).

<details>
<summary><b>🖥️ Click here to expand MCP setup instructions for ALL IDEs</b></summary>

### 1. Cursor
**File:** `.cursor/mcp.json` (inside your project folder) or `~/.cursor/mcp.json` (global)

~~~json
{
  "mcpServers": {
    "openresearch": {
      "command": "uvx",
      "args": ["openresearch-mcp", "--stdio"]
    }
  }
}
~~~

### 2. Windsurf (Codeium)
**File:** `~/.codeium/windsurf/mcp_config.json`
*(UI Path: Settings > Tools > Windsurf Settings > Add Server > View Raw Config)*

~~~json
{
  "mcpServers": {
    "openresearch": {
      "command": "uvx",
      "args": ["openresearch-mcp", "--stdio"]
    }
  }
}
~~~

### 3. Google Antigravity
**File:** `~/.gemini/config/mcp_config.json` or project-level `.antigravity/mcp_config.json`
*(UI Path: Agent Panel -> `...` Menu -> MCP Servers -> Manage MCP Servers -> View Raw Config)*

~~~json
{
  "mcpServers": {
    "openresearch": {
      "command": "uvx",
      "args": ["openresearch-mcp", "--stdio"]
    }
  }
}
~~~

### 4. VS Code (GitHub Copilot)
**File:** `.mcp.json` (at the root of your workspace) or `~/.copilot/mcp-config.json` (global)
*(UI Path: `Ctrl+Shift+P` -> `MCP: Add Server` -> Select `STDIO` -> Enter command)*

~~~json
{
  "mcpServers": {
    "openresearch": {
      "command": "uvx",
      "args": ["openresearch-mcp", "--stdio"]
    }
  }
}
~~~

### 5. Cline (VS Code Extension)
**File:** `~/.cline/data/settings/cline_mcp_settings.json`
*(UI Path: Cline Extension -> MCP Servers Tab -> Edit MCP Settings)*

~~~json
{
  "mcpServers": {
    "openresearch": {
      "command": "uvx",
      "args": ["openresearch-mcp", "--stdio"]
    }
  }
}
~~~

### 6. Claude Code (CLI)
Run this single command in your terminal (no file editing needed):

~~~bash
claude mcp add openresearch -- uvx openresearch-mcp --stdio
~~~

### 7. Claude Desktop
**File:** `%APPDATA%\Claude\claude_desktop_config.json`

~~~json
{
  "mcpServers": {
    "openresearch": {
      "command": "uvx",
      "args": ["openresearch-mcp", "--stdio"]
    }
  }
}
~~~

*After adding the config and restarting your IDE, the AI will have `search_openalex`, `read_pdf`, and `read_url` tools to verify references on the fly.*
</details>

---

## 📂 Repository Structure

~~~text
ML-Model-Architect/
│
├── _constitution/          # Global rules (load always)
├── skills/                 # 5 sequential stages
├── references/             # 12 ML algorithm groups × 3 stages + deployment
├── _shared/                # 6 output templates
├── scripts/                # verify_dois, inspect_repo, verify_references
├── projects/               # Per-project ledgers (created at runtime)
├── references_to_verify.yaml
└── README.md
~~~

---

## 🔬 Reference Rigor (The 6 Criteria)

The AI will reject any source that does not pass **ALL six** criteria:

1. **Peer review** - Journal or conference (not blog, not course).
2. **Currency** - 2024-2026, except foundational classics.
3. **Citations** - Clear reference list.
4. **Transparency** - Methodology visible.
5. **Integrity** - No retraction, no undisclosed COI.
6. **Relevance** - Directly answers the question.

---

## ⚙️ Requirements

- Any AI agent with file access (Claude Code, Cursor, Windsurf, Aider, Cline).
- Python 3.9+ (for verification scripts).
- `uvx` or `npx` (for running MCP servers).

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
<div align="center">
  <i>Built for engineers who care about <b>how</b> the model was built, not just the code.</i>
</div>
