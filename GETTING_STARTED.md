# Getting Started with ML Model Architect

This guide will get you from zero to your first AI-driven ML project in under 10 minutes.

## Prerequisites
- An AI IDE (Cursor, Claude Code, Windsurf, etc.)
- `uv` or `uvx` installed (for MCP).

## Step 1: Configure MCP
The AI needs internet access to read academic papers.
Add the following to your IDE's MCP configuration file (see the main README for exact paths):

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
Restart your IDE.

## Step 2: Start the Agent
Open the ML-Model-Architect folder in your IDE and paste this exact prompt:

> You are now ML-Model-Architect.
> 1. Read _constitution/CONSTITUTION.md first.
> 2. Read skills/01-goals-and-requirements/SKILL.md next.
> 3. Follow all rules strictly.
> 4. Start Stage 1 for a new project: "Predicting Delivery Delays".

## Step 3: Answer the Questions
The agent will NOT write code immediately. It will ask you MCQ questions.
Answer them. You will see it building a DECISIONS.md file and generating REQUIREMENTS.md.

## Step 4: Watch it Read Papers
When it moves to Stage 2 (Technique Selection), it will use the MCP server to read papers (like XGBoost) before suggesting it. 

*Note: If you want to see a completed project, check the examples/ folder.*
