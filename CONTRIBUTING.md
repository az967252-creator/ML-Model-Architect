# Contributing to ML Model Architect

First off, thank you for considering contributing! This framework is built to enforce rigor and discipline in AI-driven ML engineering. We welcome contributions that align with our core philosophy: **"The Reference guides, the Experiment decides."**

##  How to Contribute

1. **Fork the repo** and create your branch from `main`.
2. **Make your changes.**
3. **Follow the Constitution:** Any new rule, algorithm, or technique MUST be backed by a verified reference (DOI or Institutional URL). 
4. **Run the Verification Suite** locally before submitting a PR:
   ~~~bash
   # 1. Verify the DOIs and Whitelist
   python scripts/verify_dois.py
   
   # 2. Run Unit Tests
   python tests/test_verify.py
   python tests/test_skills.py
   
   # 3. Verify the Decision Ledger format
   python scripts/enforce_constitution.py examples/delivery-delay-prediction/DECISIONS.md
   ~~~
5. **Submit a Pull Request.** The CI pipeline (GitHub Actions) will automatically run your tests. If it's red, fix it before we can merge.

##  Adding a New Reference

If you want to add a new algorithm group or update an existing one:
1. Create the reference file in `references/stage-2-selection/`.
2. Ensure it has the YAML frontmatter (`group_id`, `name`, etc.).
3. Provide the verified DOI or Institutional URL in the text.
4. Add the paper's metadata (Title, Year, DOI) to `references_to_verify.yaml`. 
5. If the paper is paywalled, ensure you provide an alternative from `trusted_domains.yaml` (Rule B8).

## Security & Sandbox Rules

- **Prompt Injection Risk:** If your code involves fetching untrusted data via MCP, you MUST use the `sandbox/` directory.
- **Automated Scan:** All Python scripts dropped in `sandbox/` must pass `python scripts/scan_sandbox.py` before a human is allowed to execute them (Rule F4.1).

##  Adding a New Skill (Stage)

If you are adding a new stage (highly discouraged, as 5 stages cover the lifecycle):
1. Create a folder in `skills/`.
2. Ensure it contains an `Exit Gate` and explicit `MCP REQUIREMENT` checks.
3. Update `tests/test_skills.py` to assert that your new stage includes the required gates.
4. Update the Constitution if necessary.

##  Code Style

- We follow PEP 8 for Python code.
- We use standard Markdown for documentation.
- All commit messages should be descriptive (e.g., `feat: add whitelist check`, `fix: resolve test isolation bug`).

Thank you for helping us build the future of Agentic ML Governance!
