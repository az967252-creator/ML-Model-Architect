#!/usr/bin/env python3
"""
scripts/generate_diagram.py - Generate valid Mermaid Architecture Flowcharts from DECISIONS.md.

Produces strict, valid Mermaid diagram syntax suitable for GitHub Markdown rendering
and Mermaid CLI (mmdc) compilation.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


def sanitize_label(text: str) -> str:
    """Sanitize string for Mermaid node label (removes unescaped quotes/brackets)."""
    text = text.replace('"', "'").replace("[", "(").replace("]", ")").replace("<", "&lt;").replace(">", "&gt;")
    return text.strip()


def generate_mermaid_diagram(filepath: Path, output_file: Optional[Path] = None) -> str:
    """Generate Mermaid flowchart from DECISIONS.md."""
    if not filepath.exists() or not filepath.is_file():
        raise FileNotFoundError(f"DECISIONS.md not found: {filepath}")

    content = filepath.read_text(encoding="utf-8")
    lines = [l for l in content.splitlines() if l.strip().startswith("|") and "---" not in l]
    if len(lines) <= 1:
        raise ValueError(f"No decisions recorded in {filepath}")

    headers = [h.strip() for h in lines[0].split("|")[1:-1]]
    rows = []
    for line in lines[1:]:
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) == len(headers):
            rows.append(dict(zip(headers, cols)))

    mermaid_lines = [
        "```mermaid",
        "flowchart TD",
    ]

    prev_node = None
    for idx, d in enumerate(rows, 1):
        stage = sanitize_label(d.get("Stage", str(idx)))
        dtype = sanitize_label(d.get("Type", "Decision"))
        question = sanitize_label(d.get("Question", ""))
        chosen = sanitize_label(d.get("Chosen", ""))
        ref = sanitize_label(d.get("Reference", "heuristic"))

        node_id = f"step_{idx}"
        label = f"Stage {stage} [{dtype}]: {question} → {chosen} ({ref})"
        mermaid_lines.append(f'    {node_id}["{label}"]')

        if prev_node:
            mermaid_lines.append(f"    {prev_node} --> {node_id}")
        prev_node = node_id

    mermaid_lines.append("```")
    diagram_md = "\n".join(mermaid_lines) + "\n"

    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(diagram_md, encoding="utf-8")
        print(f"✅ Generated diagram at: {output_file}")

    return diagram_md


def is_valid_mermaid(content: str) -> bool:
    """Validates basic syntax of Mermaid block."""
    if not (content.startswith("```mermaid") and content.strip().endswith("```")):
        return False
    body = content.replace("```mermaid", "").replace("```", "").strip()
    if not (body.startswith("flowchart") or body.startswith("graph")):
        return False
    # Check that all node definitions have matching quotes
    for line in body.splitlines():
        line = line.strip()
        if '["' in line and not line.endswith('"]'):
            if '-->|"' in line:
                continue
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Mermaid Architecture Diagram.")
    parser.add_argument("filepath", type=Path, nargs="?", default=Path("examples/delivery-delay-prediction/DECISIONS.md"), help="Path to DECISIONS.md")
    parser.add_argument("--output", type=Path, default=None, help="Output markdown path")
    args = parser.parse_args()

    try:
        out_path = args.output or (args.filepath.parent / "DIAGRAM.md")
        generate_mermaid_diagram(args.filepath, out_path)
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
