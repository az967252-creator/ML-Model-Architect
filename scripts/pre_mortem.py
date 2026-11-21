#!/usr/bin/env python3
"""
scripts/pre_mortem.py - Generate a Pre-Mortem Risk Analysis.

Parses DECISIONS.md to evaluate potential operational and architectural failure modes
based on decision types, heuristic tags, data constraints, and deployment patterns.
Fails closed if the input file does not exist or contains no valid decisions.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional


def parse_decisions(content: str) -> list[dict]:
    lines = [l for l in content.splitlines() if l.strip().startswith("|") and "---" not in l]
    if len(lines) <= 1:
        return []
    headers = [h.strip() for h in lines[0].split("|")[1:-1]]
    rows = []
    for line in lines[1:]:
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) == len(headers):
            rows.append(dict(zip(headers, cols)))
    return rows


def generate_premortem(filepath: Path, output_file: Optional[Path] = None) -> str:
    if not filepath.exists() or not filepath.is_file():
        raise FileNotFoundError(f"DECISIONS.md file not found: {filepath}")

    content = filepath.read_text(encoding="utf-8")
    decisions = parse_decisions(content)
    if not decisions:
        raise ValueError(f"No decisions recorded in: {filepath}")

    risks = []

    for d in decisions:
        stage = d.get("Stage", "")
        dtype = d.get("Type", "").lower()
        question = d.get("Question", "")
        chosen = d.get("Chosen", "")
        ref = d.get("Reference", "")
        ref_lower = ref.lower()

        # Check for heuristic / reference gap
        if "heuristic" in ref_lower or "reference-gap" in ref_lower:
            if dtype == "technique":
                risks.append({
                    "risk": f"Technique selection ('{chosen}') lacks peer-reviewed literature backing (tagged '{ref}').",
                    "scenario": "Under production traffic with unseen feature interactions, the algorithm degrades severely because inductive biases were ungrounded.",
                    "mitigation": "Conduct systematic PRISMA literature review (Rule B5) or run rigorous stress-testing against simpler baselines."
                })
            elif dtype == "parameter":
                risks.append({
                    "risk": f"Hyperparameters for '{chosen}' chosen heuristically without empirical bounds.",
                    "scenario": "Model overfits the training distribution and suffers high variance when deployed to production.",
                    "mitigation": "Perform automated Optuna Bayesian optimization bounded by foundational ranges (Rule B3)."
                })
            elif dtype in {"threshold", "deployment"}:
                risks.append({
                    "risk": f"Deployment/Monitoring threshold ('{chosen}') tagged as heuristic.",
                    "scenario": "Drift alert triggers false positives or misses true distribution drift, causing alert fatigue or silent failure.",
                    "mitigation": "Anchor drift metrics to baseline test-fold Kolmogorov-Smirnov statistics (Rule B8)."
                })

        # Check metric framing
        if dtype == "metric":
            if "accuracy" in chosen.lower() and "f1" not in chosen.lower() and "auc" not in chosen.lower():
                risks.append({
                    "risk": "Using standard Accuracy as the primary objective metric.",
                    "scenario": "Severe class imbalance produces a 95%+ accurate model that predicts the majority class and fails all minority cases.",
                    "mitigation": "Re-frame optimization objective to Precision-Recall AUC or Cost-Weighted Loss (Rule B1)."
                })

        # Check complex model selection
        if dtype == "technique" and ("neural" in chosen.lower() or "deep" in chosen.lower()):
            risks.append({
                "risk": f"Deep learning model ('{chosen}') chosen for tabular data.",
                "scenario": "Inference latency violates SLA requirements and operational maintenance cost skyrockets compared to gradient boosting.",
                "mitigation": "Validate via Hastie 1-SE rule (Rule G3); revert to tree-based baseline if performance difference is within 1 standard error."
            })

        # Check deployment strategy
        if dtype == "deployment":
            if "direct" in chosen.lower() or "in-place" in chosen.lower():
                risks.append({
                    "risk": "Direct in-place production deployment without canary or shadow traffic.",
                    "scenario": "A catastrophic serialization error or unhandled NaN payload crashes the live API serving pipeline.",
                    "mitigation": "Mandate Shadow or Canary deployment pattern for the first 14 days of serving (Rule B8)."
                })

    if not risks:
        risks.append({
            "risk": "Silent feature distribution shift or covariate drift over time.",
            "scenario": "Upstream data pipelines change encoding schemas, causing silent model degradation with zero runtime exceptions.",
            "mitigation": "Implement continuous data drift monitoring (PSI / KS-test) and automated retraining pipelines (Rule B8)."
        })

    lines = [
        f"# Pre-Mortem Risk Analysis — {filepath.parent.name}",
        "",
        "> **Objective:** Anticipate and eliminate failure modes before models enter production environments.",
        "",
        "## Evaluated Failure Scenarios",
        "",
    ]

    for idx, r in enumerate(risks, 1):
        lines.append(f"### Scenario {idx}: {r['risk']}")
        lines.append(f"- **Failure Mode:** {r['scenario']}")
        lines.append(f"- **Mandated Mitigation:** {r['mitigation']}")
        lines.append("")

    report = "\n".join(lines).strip() + "\n"

    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(report, encoding="utf-8")
        print(f"✅ Generated pre-mortem analysis at: {output_file}")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Pre-Mortem Risk Analysis.")
    parser.add_argument("filepath", type=Path, nargs="?", default=Path("examples/delivery-delay-prediction/DECISIONS.md"), help="Path to DECISIONS.md")
    parser.add_argument("--output", type=Path, default=None, help="Output markdown path")
    args = parser.parse_args()

    try:
        out_path = args.output or (args.filepath.parent / "PRE_MORTEM.md")
        generate_premortem(args.filepath, out_path)
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
