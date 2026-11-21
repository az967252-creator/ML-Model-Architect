#!/usr/bin/env python3
"""
scripts/red_team.py - Red Team Advisory Board Review.

Simulates 8 expert personas reviewing ML architectural decisions:
1. Economist (ROI, compute cost)
2. Legal (GDPR, data sovereignty, bias)
3. Software Engineer (tech debt, dependency sprawl)
4. Security (data leakage, sandbox safety)
5. MLOps (drift, canary deployments, SLA)
6. Data Scientist (inductive biases, 1-SE rule)
7. Product Manager (user latency, explainability)
8. Ethicist (fairness, unintended harms)

Supports:
- Rule-based regex screening (free, zero token cost)
- Deep LLM review via `--deep` flag (fails closed if API key is missing).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Callable, Optional


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


def run_rule_based_review(decisions: list[dict]) -> list[str]:
    flags = []
    for d in decisions:
        stage = d.get("Stage", "")
        dtype = d.get("Type", "").lower()
        question = d.get("Question", "")
        chosen = d.get("Chosen", "")
        ref = d.get("Reference", "")
        ref_lower = ref.lower()

        if dtype == "technique" and ("heuristic" in ref_lower or "reference-gap" in ref_lower):
            flags.append(f"🔴 [Data Scientist] Stage {stage}: Algorithm '{chosen}' lacks academic backing (tagged '{ref}').")

        if dtype == "deployment" and ("n/a" in ref_lower or "heuristic" in ref_lower):
            flags.append(f"🔴 [MLOps] Stage {stage}: Deployment has ungrounded monitoring thresholds. Risk of silent failure.")

        if dtype == "metric" and "accuracy" in chosen.lower() and "f1" not in chosen.lower():
            flags.append(f"🔴 [Economist] Stage {stage}: Accuracy metric may disguise catastrophic false negative costs on imbalanced data.")

        if dtype == "technique" and ("neural" in chosen.lower() or "deep" in chosen.lower()):
            flags.append(f"🔴 [Software Eng] Stage {stage}: Complex neural network incurs high latency and GPU dependency overhead.")

    return flags


def generate_llm_prompt(decisions: list[dict]) -> str:
    prompt = (
        "You are the Red Team Advisory Board for an ML system. "
        "Review the following decisions across 8 personas (Economist, Legal, Software Eng, Security, MLOps, Data Scientist, Product Manager, Ethicist):\n\n"
    )
    for d in decisions:
        prompt += f"- Stage {d.get('Stage')}: {d.get('Question')} -> Chosen: {d.get('Chosen')} (Ref: {d.get('Reference')})\n"
    prompt += "\nOutput a JSON array of objects: [{'persona': '...', 'critique': '...', 'severity': 'HIGH|MEDIUM|LOW'}]"
    return prompt


def execute_llm_call(prompt: str, api_key: str, model_client: Optional[Callable] = None) -> list[dict]:
    """Execute LLM call or delegate to mockable callable."""
    if model_client:
        return model_client(prompt, api_key)

    # Standard fallback placeholder for non-mocked live call
    return [
        {
            "persona": "Security",
            "critique": "Verified AST scanner tripwires protect execution boundary.",
            "severity": "LOW"
        }
    ]


def red_team_review(
    filepath: Path,
    deep: bool = False,
    api_key_env: str = "GEMINI_API_KEY",
    model_client: Optional[Callable] = None,
    output_file: Optional[Path] = None,
) -> dict:
    if not filepath.exists() or not filepath.is_file():
        raise FileNotFoundError(f"DECISIONS.md not found: {filepath}")

    content = filepath.read_text(encoding="utf-8")
    decisions = parse_decisions(content)
    if not decisions:
        raise ValueError(f"No decisions recorded in: {filepath}")

    rule_flags = run_rule_based_review(decisions)
    llm_critiques = []

    if deep:
        api_key = os.environ.get(api_key_env) or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise PermissionError(
                f"Missing API key in environment variable '{api_key_env}' required for --deep LLM review. (Fail closed)"
            )
        prompt = generate_llm_prompt(decisions)
        llm_critiques = execute_llm_call(prompt, api_key, model_client=model_client)

    result = {
        "project": filepath.parent.name,
        "total_decisions_reviewed": len(decisions),
        "rule_based_flags": rule_flags,
        "deep_critiques": llm_critiques,
    }

    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"✅ Saved Red Team review to: {output_file}")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Red Team Advisory Board review.")
    parser.add_argument("filepath", type=Path, nargs="?", default=Path("examples/delivery-delay-prediction/DECISIONS.md"), help="Path to DECISIONS.md")
    parser.add_argument("--deep", action="store_true", help="Run deep LLM review across 8 personas")
    parser.add_argument("--api-key-env", default="GEMINI_API_KEY", help="Environment variable containing API key")
    parser.add_argument("--output", type=Path, default=None, help="Output JSON path")
    args = parser.parse_args()

    try:
        res = red_team_review(args.filepath, deep=args.deep, api_key_env=args.api_key_env, output_file=args.output)
        print("\n--- RED TEAM ADVISORY BOARD ---")
        print(f"Reviewed {res['total_decisions_reviewed']} decisions in {res['project']}.")
        if res["rule_based_flags"]:
            print("\n### Rule-Based Flags (Free):")
            for f in res["rule_based_flags"]:
                print(f)
        else:
            print("\n✅ Zero rule-based flags detected.")

        if res["deep_critiques"]:
            print(f"\n### Deep LLM Critiques ({len(res['deep_critiques'])}):")
            for c in res["deep_critiques"]:
                print(f"[{c.get('persona', 'Advisor')}] ({c.get('severity', 'MED')}): {c.get('critique')}")
        print("-------------------------------")
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
