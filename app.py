#!/usr/bin/env python3
"""
app.py - Streamlit Dashboard for ML Model Architect.

Interactive governance, decision ledger, and metrics visualization.
Can be run via:
    streamlit run app.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

try:
    import streamlit as st
    import pandas as pd
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


def run_dashboard():
    if not STREAMLIT_AVAILABLE:
        print("Streamlit or pandas is not installed. Run: pip install streamlit pandas", file=sys.stderr)
        return 1

    st.set_page_config(page_title="ML Model Architect Dashboard", layout="wide")
    st.title("ML Model Architect — Governance & Audit Dashboard")
    st.markdown("**A strict, reference-driven framework that turns AI agents into disciplined ML engineers.**")

    examples_dir = ROOT / "examples"
    if not examples_dir.exists():
        st.error(f"Examples directory not found at: {examples_dir}")
        return 1

    projects = [d.name for d in examples_dir.iterdir() if d.is_dir() and not d.name.startswith("__") and d.name != "catalog"]

    if not projects:
        st.warning("No projects found in examples/ directory.")
        return 0

    st.sidebar.header("Project Selection")
    selected_project = st.sidebar.selectbox("Choose a project:", projects)
    project_path = examples_dir / selected_project

    st.header(f"Project: {selected_project.replace('-', ' ').title()}")

    # 1. Deterministic Plan Manifest
    plan_file = project_path / "PLAN.manifest.json"
    if plan_file.exists():
        st.subheader("📋 Deterministic Plan & Run Policy")
        try:
            with open(plan_file, "r", encoding="utf-8") as pf:
                plan_data = json.load(pf)

            col1, col2, col3 = st.columns(3)
            col1.metric("Plan Version", plan_data.get("plan_version", "1.0.0"))
            col2.metric("Execution Steps", len(plan_data.get("execution_dag", [])))

            lock_file = project_path / "PLAN.lock"
            is_locked = lock_file.exists()
            col3.metric("Cryptographic Lock", "LOCKED (SHA-256)" if is_locked else "UNLOCKED")

            with st.expander("View Execution DAG Steps", expanded=False):
                for step in plan_data.get("execution_dag", []):
                    st.markdown(f"**Stage {step.get('stage')}: `{step.get('step_id')}`** — {step.get('action_type')}")
                    st.caption(f"Ref: `{step.get('reference_anchor')}` | Target: `{step.get('target_file', 'N/A')}`")
        except Exception as e:
            st.error(f"Error parsing plan manifest: {e}")
        st.divider()

    # 2. Decision Ledger
    dec_file = project_path / "DECISIONS.md"
    if dec_file.exists():
        st.subheader("📜 Decision Audit Ledger")
        content = dec_file.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines() if l.strip().startswith("|") and "---" not in l]
        if len(lines) > 1:
            headers = [h.strip() for h in lines[0].split("|")[1:-1]]
            data = []
            for line in lines[1:]:
                cols = [c.strip() for c in line.split("|")[1:-1]]
                if len(cols) == len(headers):
                    data.append(cols)

            df = pd.DataFrame(data, columns=headers)
            st.dataframe(df, use_container_width=True, hide_index=True)

            col1, col2, col3 = st.columns(3)
            col1.metric("Total Decisions", len(df))
            refs_count = df["Reference"].apply(lambda x: "10." in x or "http" in x).sum()
            col2.metric("Verified References", f"{refs_count} / {len(df)}")
            rigor_score = round((refs_count / len(df)) * 100) if len(df) > 0 else 0
            col3.metric("Rigor Score", f"{rigor_score}%")
        else:
            st.info("No decisions logged yet.")
        st.divider()

    # 3. Training & Evaluation Reports
    col_rep1, col_rep2 = st.columns(2)
    with col_rep1:
        st.subheader("📊 Training Report")
        train_file = project_path / "TRAINING-REPORT.md"
        if train_file.exists():
            st.markdown(train_file.read_text(encoding="utf-8"))
        else:
            st.info("TRAINING-REPORT.md not found.")

    with col_rep2:
        st.subheader("⚖️ Evaluation Report")
        eval_file = project_path / "EVALUATION-REPORT.md"
        if eval_file.exists():
            st.markdown(eval_file.read_text(encoding="utf-8"))
        else:
            st.info("EVALUATION-REPORT.md not found.")

    # 4. Pre-Mortem Risk Analysis
    premortem_file = project_path / "PRE_MORTEM.md"
    if premortem_file.exists():
        st.divider()
        st.subheader("🛡️ Pre-Mortem Risk Analysis")
        st.markdown(premortem_file.read_text(encoding="utf-8"))

    return 0


if __name__ == "__main__":
    if STREAMLIT_AVAILABLE:
        run_dashboard()
    else:
        print("Streamlit dashboard is optional. Install with: pip install -r requirements-dashboard.txt")
        sys.exit(0)
