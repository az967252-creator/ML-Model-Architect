#!/usr/bin/env python3
import sys
from pathlib import Path

def generate_premortem(filepath):
    if not Path(filepath).exists():
        print(f"ERROR: {filepath} not found.")
        sys.exit(1)
        
    content = Path(filepath).read_text(encoding="utf-8")
    risks = []
    if "heuristic" in content.lower():
        risks.append("Model might be overfitting because hyperparameters lack academic validation (heuristic used).")
    if "neural network" in content.lower():
        risks.append("Neural Network might be too complex for the dataset, leading to high latency and GPU costs.")
    if "accuracy" in content.lower() and "f1" not in content.lower():
        risks.append("Using Accuracy as the only metric is dangerous for imbalanced datasets; stakeholders might reject the model.")
        
    if not risks:
        risks.append("No immediate red flags detected, but continuous monitoring is required to prevent data drift.")
        
    report = "# Pre-mortem Analysis: Why this project might fail in 6 months\n\n"
    for i, r in enumerate(risks, 1):
        report += f"## Scenario {i}\n**Risk:** {r}\n**Mitigation:** Implement continuous monitoring and trigger retraining pipelines (see Rule B8).\n\n"
        
    out_file = Path(filepath).parent / "PRE_MORTEM.md"
    out_file.write_text(report, encoding="utf-8")
    print(f"✅ Generated {out_file}")

if __name__ == "__main__":
    generate_premortem(sys.argv[1] if len(sys.argv) > 1 else "examples/delivery-delay-prediction/DECISIONS.md")
