# ML Model Builder Skills

A staged, reference-driven system that turns any AI agent into a disciplined ML engineer.

## Core Principle

The Reference Is the Judge. Every technical decision must have a verified citation. No reference means STOP and record a "Reference Gap". Never invent.

## The 5 Stages

| # | Stage | Output |
|---|-------|--------|
| 1 | Goals & Requirements | REQUIREMENTS.md |
| 2 | Technique Selection | TECH-CHOICE.md |
| 3 | Building & Training | TRAINING-REPORT.md |
| 4 | Evaluation & Diagnosis | EVALUATION-REPORT.md |
| 5 | Deployment & Monitoring | DEPLOYMENT-REPORT.md |

## Quick Start

1. Clone and cd into the repo.
2. Prompt your AI agent:

You are an ML engineer. Read _constitution/CONSTITUTION.md first.
Read skills/01-goals-and-requirements/SKILL.md next.
Follow all rules strictly. Start Stage 1.

3. Answer the agent's questions. Each stage produces a report.

## Requirements

- Any AI agent with file access (Claude Code, Cursor, Aider, Cline, Continue)
- Python 3.9+
- Optional: pip install pyyaml requests docling

## Structure

- _constitution/CONSTITUTION.md - Rules (load always)
- skills/ - 5 stages
- references/ - 12 groups x 3 stages + deployment
- _shared/ - 6 output templates
- scripts/ - verify_dois, inspect_repo, verify_references
- projects/ - Per-project ledgers

## Reference Rigor (6 criteria)

A source is usable only if ALL six pass:

1. Peer review - journal or conference (not blog, not course)
2. Currency - 2024-2026, except foundational
3. Citations - clear reference list
4. Transparency - methodology visible
5. Integrity - no retraction, no undisclosed COI
6. Relevance - directly answers the question

## License

MIT
## MCP Setup (Mandatory for Strict Mode)

To enable the AI to read research papers directly from the internet, you MUST configure an MCP (Model Context Protocol) server.

### For Claude Desktop:
Add this to `%APPDATA%\Claude\claude_desktop_config.json`:

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

### For Cursor:
Add this to `.cursor/mcp.json`:

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

After restarting, the AI will have `search_openalex`, `read_pdf`, and `read_url` tools to verify references on the fly.
