#!/usr/bin/env python3
"""Count and validate constitutional rules in _constitution/CONSTITUTION.md.

Ensures monotonic numbering across Parts A-G and validates total rule count against
the canonical architecture specification (35 rules).
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

RULE_RE = re.compile(r"^###\s+([A-G]\d+)\s+[—-]\s+(.+)$", re.MULTILINE)
EXPECTED_COUNTS = {
    "A": 5,
    "B": 9,
    "C": 6,
    "D": 5,
    "E": 1,
    "F": 5,
    "G": 4,
}
TOTAL_EXPECTED_RULES = sum(EXPECTED_COUNTS.values())  # 35


def parse_rules(constitution_path: Path) -> dict:
    """Parse CONSTITUTION.md and return rule metadata."""
    if not constitution_path.exists():
        raise FileNotFoundError(f"Constitution file not found at: {constitution_path}")

    text = constitution_path.read_text(encoding="utf-8")
    matches = RULE_RE.findall(text)

    rules_by_part = defaultdict(list)
    for rule_id, title in matches:
        part = rule_id[0]
        num = int(rule_id[1:])
        rules_by_part[part].append((rule_id, num, title.strip()))

    return {
        "rules_by_part": dict(rules_by_part),
        "total": len(matches),
        "all_rule_ids": [m[0] for m in matches],
    }


def validate_rules(parsed: dict, expected_total: int = TOTAL_EXPECTED_RULES) -> list[str]:
    """Validate rule sequence integrity and count."""
    errors = []
    rules_by_part = parsed["rules_by_part"]

    # Check for expected parts
    for part, exp_count in EXPECTED_COUNTS.items():
        if part not in rules_by_part:
            errors.append(f"Missing entire Part {part} (expected {exp_count} rules)")
            continue
        actual = rules_by_part[part]
        if len(actual) != exp_count:
            errors.append(f"Part {part}: expected {exp_count} rules, found {len(actual)} ({[r[0] for r in actual]})")
        # Check monotonic numbering starting from 1
        nums = [r[1] for r in actual]
        expected_nums = list(range(1, exp_count + 1))
        if nums != expected_nums:
            errors.append(f"Part {part}: numbering is non-monotonic or has gaps/duplicates: {nums} != {expected_nums}")

    # Check total
    if parsed["total"] != expected_total:
        errors.append(f"Total rule count mismatch: found {parsed['total']}, expected {expected_total}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Count and validate constitutional rules.")
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "_constitution" / "CONSTITUTION.md",
        help="Path to CONSTITUTION.md",
    )
    parser.add_argument(
        "--expected",
        type=int,
        default=TOTAL_EXPECTED_RULES,
        help="Expected total rule count (default: 35)",
    )
    args = parser.parse_args()

    try:
        parsed = parse_rules(args.path)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    errors = validate_rules(parsed, expected_total=args.expected)

    print("=== Constitutional Rules Inventory ===")
    for part in sorted(EXPECTED_COUNTS.keys()):
        rules = parsed["rules_by_part"].get(part, [])
        print(f"Part {part}: {len(rules)} rules -> {', '.join(r[0] for r in rules)}")
    print("---------------------------------------")
    print(f"Total Rules Counted: {parsed['total']} (Expected: {args.expected})")

    if errors:
        print("\nVALIDATION FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print("Status: OK (All rules valid and monotonically numbered)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
