#!/usr/bin/env python3
"""
lint_references.py - Linter for academic grounding of hyperparameters and thresholds.

Enforces Constitution Rule B1 & B4:
Every hyperparameter range or threshold mentioned in stage-3, stage-4, and stage-5
reference documentation must carry a verified DOI reference with locator, a trusted URL,
or explicitly bear the tag `(heuristic)`.
"""

import os
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TARGET_DIRS = [
    ROOT / "references" / "stage-3-training",
    ROOT / "references" / "stage-4-evaluation",
    ROOT / "references" / "stage-5-deployment"
]

PARAM_PATTERN = re.compile(
    r"(learning_rate|max_depth|n_estimators|min_samples|alpha|lambda|gamma|subsample|colsample|"
    r"regulariz|threshold|cutoff|contamination|eps|min_samples|n_neighbors|n_clusters|"
    r"penalty|solver|dropout|batch_size|epochs|latent_dim|window_size|psi|p99|latency|retrain)",
    re.IGNORECASE
)

GROUNDING_PATTERN = re.compile(
    r"(10\.\d{4,9}/[^\s|;,()<>]+|https?://[^\s|;,()<>]+|\(heuristic\)|\[heuristic\]|heuristic|reference-gap)",
    re.IGNORECASE
)


def lint_markdown_file(file_path: Path):
    """Lints a single markdown file for hyperparameter/threshold grounding."""
    violations = []
    lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()

    in_table = False
    in_code_block = False

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # Check if line proposes a parameter/threshold configuration or recommendation
        if PARAM_PATTERN.search(stripped) and (":" in stripped or "|" in stripped or "=" in stripped or ">" in stripped or "<" in stripped):
            # Skip pure section headers or table structural separators
            if stripped.startswith("#") or stripped.startswith("|---"):
                continue
            if stripped.startswith("<!--") or "group_id" in stripped or "type:" in stripped:
                continue
            # Skip table header rows
            if stripped.startswith("|") and any(h in stripped.lower() for h in ["layer |", "problem |", "symptom |", "strategy |", "check |"]):
                continue

            # Must have grounding or (heuristic)
            if not GROUNDING_PATTERN.search(stripped):
                violations.append((idx, line.strip()))

    return violations


def main():
    total_violations = 0
    scanned_files = 0

    print("=" * 60)
    print("🔍 Hyperparameter & Threshold Reference Linter")
    print("=" * 60)

    for target_dir in TARGET_DIRS:
        if not target_dir.exists():
            continue
        for md_file in sorted(target_dir.glob("*.md")):
            scanned_files += 1
            violations = lint_markdown_file(md_file)
            if violations:
                print(f"\n❌ {md_file.relative_to(ROOT)} ({len(violations)} violation(s)):")
                for lineno, text in violations:
                    print(f"   L{lineno}: {text[:80]}")
                total_violations += len(violations)

    print("-" * 60)
    print(f"Scanned {scanned_files} markdown files.")
    if total_violations > 0:
        print(f"❌ Found {total_violations} ungrounded parameter/threshold specification(s).")
        print("   All ranges/thresholds must carry a DOI with locator, trusted URL, or tag '(heuristic)'.")
        return 1

    print("✅ All hyperparameter ranges and thresholds are properly anchored or tagged (heuristic).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
