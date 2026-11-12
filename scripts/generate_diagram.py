#!/usr/bin/env python3
import sys
from pathlib import Path

def generate_diagram(filepath):
    if not Path(filepath).exists():
        print(f"ERROR: {filepath} not found.")
        sys.exit(1)
        
    content = Path(filepath).read_text(encoding="utf-8")
    lines = [line for line in content.split("\n") if line.strip().startswith("|") and "---" not in line]
    
    mermaid = ["```mermaid", "graph TD"]
    
    for i, line in enumerate(lines[1:], start=1):
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) < 8: continue
        
        stage = cols[0]
        dec_type = cols[2]
        question = cols[3].replace('"', '')
        chosen = cols[5].replace('"', '')
        
        node_id = f"D{i}"
        mermaid.append(f'    {node_id}["Stage {stage}: {question}"]')
        mermaid.append(f'    {node_id} -->|"{dec_type} -> {chosen}"| {node_id}_res')
        
    mermaid.append("```")
    
    out_file = Path(filepath).parent / "DIAGRAM.md"
    out_file.write_text("\n".join(mermaid), encoding="utf-8")
    print(f"✅ Generated {out_file}")

if __name__ == "__main__":
    generate_diagram(sys.argv[1] if len(sys.argv) > 1 else "examples/delivery-delay-prediction/DECISIONS.md")
