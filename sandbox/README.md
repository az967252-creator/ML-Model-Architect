# Sandbox Directory

**DO NOT RUN CODE IN THIS DIRECTORY WITHOUT REVIEWING IT.**

Per Rule F4 of the Constitution, the AI agent will drop any Python code generated from untrusted MCP web content here. 
As a human, your job is to review this code for Prompt Injection risks before executing it.

## How to use:
1. AI writes script: `sandbox/generated_model.py`
2. You open the file in your IDE.
3. You verify it doesn't contain malicious commands (e.g., `os.system`, `requests.post` to unknown servers).
4. You run it manually in your terminal.
5. You paste the output back to the AI.
