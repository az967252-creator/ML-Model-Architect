# Security Policy

## Supported Versions
We are currently on version `1.0.0` (Stable).

## Reporting a Vulnerability
Because ML Model Architect relies on the **Model Context Protocol (MCP)** to fetch content from the internet, security is a top priority. 

If you discover a vulnerability (e.g., a prompt injection vector via a malicious academic paper), **please do not open a public issue.** 

Instead, email us directly at `security@mlmodelarchitect.dev` (placeholder) with:
1. A description of the vulnerability.
2. Steps to reproduce.
3. Potential impact.

We will acknowledge your email within 48 hours and provide a timeline for a patch.

## MCP Security Warnings
- **Prompt Injection:** Always pin the version of your MCP server (e.g., `openresearch-mcp==1.0.0`). Never blindly execute code suggested by an LLM that just read an untrusted web page.
- **Data Exfiltration:** The `openresearch-mcp` server only reads public data. Do not configure it with API keys to private repositories.
