#!/usr/bin/env python3
import sys
import re
from pathlib import Path

def generate_prompt(decisions_to_review):
    prompt = "You are the Red Team Advisory Board for an ML project. Your team consists of 8 experts:\n"
    prompt += "1. Economist (ROI, cost), 2. Legal (GDPR, bias), 3. Software Eng (tech debt), 4. Security (leakage),\n"
    prompt += "5. MLOps (drift, deployment), 6. Data Scientist (math, overfitting), 7. Product Manager (UX), 8. Ethicist (fairness).\n\n"
    prompt += "Review the following ML decisions and output a JSON array of critiques. Only active relevant personas.\n\n"
    prompt += "Decisions:\n"
    for d in decisions_to_review:
        prompt += f"- Stage {d['stage']}: {d['question']} (Chosen: {d['chosen']}, Ref: {d['ref']})\n"
    prompt += "\nOutput format: [{'persona': 'Name', 'critique': '...'}]"
    return prompt

def analyze_ledger(filepath):
    if not Path(filepath).exists():
        print(f"ERROR: {filepath} not found.")
        sys.exit(1)
        
    content = Path(filepath).read_text(encoding="utf-8")
    lines = [line for line in content.split("\n") if line.strip().startswith("|") and "---" not in line]
    
    red_flags = []
    new_decisions = []
    
    for line in lines[1:]:
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) < 8: continue
        
        d = {"stage": cols[0], "type": cols[2], "question": cols[3], "chosen": cols[5], "ref": cols[7]}
        
        if d["type"] == "technique" and d["ref"].lower() in ["heuristic", "reference-gap"]:
            red_flags.append(f"🔴 [Data Scientist] Algorithm '{d['chosen']}' selected using '{d['ref']}'.")
        elif d["type"] == "deployment" and "N/A" in d["ref"]:
             red_flags.append(f"🔴 [MLOps] Deployment has no monitoring reference. High risk of silent failure.")
        else:
            new_decisions.append(d)

    print("\n--- RED TEAM ADVISORY BOARD ---")
    if red_flags:
        print("### Rule-Based Flags (Free):")
        for rf in red_flags: print(rf)
    
    if new_decisions:
        print("\n### LLM Deep Review Prompt (Copy & Paste to AI):")
        print(generate_prompt(new_decisions))
    else:
        print("\n✅ No new decisions to review.")
    print("-------------------------------")

if __name__ == "__main__":
    analyze_ledger(sys.argv[1] if len(sys.argv) > 1 else "examples/delivery-delay-prediction/DECISIONS.md")
