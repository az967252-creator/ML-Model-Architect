# Contributing to ML Model Architect

First off, thank you for considering contributing! This framework is built to enforce rigor and discipline in AI-driven ML engineering.

## How to Contribute

1. **Fork the repo** and create your branch from `main`.
2. **Make your changes.**
3. **Ensure the constitution is upheld:** If you add a new rule or algorithm, you must add a reference (DOI or URL) and update the `references/` directory.
4. **Run the enforcement script:**
   ~~~bash
   python scripts/enforce_constitution.py examples/delivery-delay-prediction/DECISIONS.md
   ~~~
5. **Submit a Pull Request.**

## Adding a New Reference

If you want to add a new algorithm group or update an existing one:
- Create the reference file in `references/stage-2-selection/`.
- Ensure it has the YAML frontmatter (`group_id`, `name`, etc.).
- Provide the verified DOI or URL in the text.
