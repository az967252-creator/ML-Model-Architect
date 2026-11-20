import streamlit as st
import pandas as pd
import os
import glob
import re

st.set_page_config(page_title="ML Model Architect Dashboard", layout="wide")

st.title("ML Model Architect — Governance & Audit Dashboard")
st.markdown("**A strict, reference-driven framework that turns AI agents into disciplined ML engineers.**")

# Find all projects in the examples folder
examples_dir = os.path.join(os.path.dirname(__file__), "examples")
projects = [d for d in os.listdir(examples_dir) if os.path.isdir(os.path.join(examples_dir, d)) and not d.startswith('__') and d != 'catalog']

# Sidebar
st.sidebar.header("Project Selection")
selected_project = st.sidebar.selectbox("Choose a project:", projects)

project_path = os.path.join(examples_dir, selected_project)

# Display Decisions Ledger
st.header(f"Project: {selected_project.capitalize().replace('-', ' ')}")

# Display Deterministic Plan Manifest if exists
plan_file = os.path.join(project_path, "PLAN.manifest.json")
if os.path.exists(plan_file):
    st.subheader("[PLAN] Deterministic Plan & Run Policy")
    try:
        import json
        with open(plan_file, "r", encoding="utf-8") as pf:
            plan_data = json.load(pf)
        
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("Plan Version", plan_data.get("plan_version", "1.0.0"))
        col_p2.metric("Execution Steps", len(plan_data.get("execution_dag", [])))
        
        lock_file = plan_file.replace(".manifest.json", ".lock")
        is_locked = os.path.exists(lock_file)
        col_p3.metric("Cryptographic Lock", "LOCKED (SHA-256)" if is_locked else "UNLOCKED")
        
        with st.expander("View Execution DAG Steps", expanded=False):
            for step in plan_data.get("execution_dag", []):
                st.markdown(f"**Stage {step.get('stage')}: `{step.get('step_id')}`** — {step.get('action_type')}")
                st.caption(f"Ref: `{step.get('reference_anchor')}` | Target: `{step.get('target_file', 'N/A')}`")
    except Exception as e:
        st.error(f"Error parsing plan manifest: {e}")
    st.divider()

dec_file = os.path.join(project_path, "DECISIONS.md")
if os.path.exists(dec_file):
    st.subheader("[LEDGER] Decision Ledger")
    
    # Parse the markdown table into a pandas dataframe
    with open(dec_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = [line for line in content.split("\n") if line.strip().startswith("|") and "---" not in line]
    if len(lines) > 1:
        headers = [h.strip() for h in lines[0].split("|")[1:-1]]
        data = []
        for line in lines[1:]:
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) == len(headers):
                data.append(cols)
        
        df = pd.DataFrame(data, columns=headers)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Decisions", len(df))
        
        refs_count = df["Reference"].apply(lambda x: "10." in x or "http" in x).sum()
        col2.metric("Valid References", f"{refs_count} / {len(df)}")
        
        rigor_score = int((refs_count / len(df)) * 100) if len(df) > 0 else 0
        col3.metric("Rigor Score", f"{rigor_score}%")
    else:
        st.info("No decisions logged yet.")

else:
    st.warning("DECISIONS.md not found in this project.")

# Display Training Report
st.divider()
st.subheader("[REPORT] Training Report")
train_file = os.path.join(project_path, "TRAINING-REPORT.md")
if os.path.exists(train_file):
    with open(train_file, "r", encoding="utf-8") as f:
        st.markdown(f.read())
else:
    st.info("TRAINING-REPORT.md not found in this project.")

# Display Pre-mortem if exists
premortem_file = os.path.join(project_path, "PRE_MORTEM.md")
if os.path.exists(premortem_file):
    st.divider()
    st.subheader("[RISK] Pre-mortem Analysis")
    with open(premortem_file, "r", encoding="utf-8") as f:
        st.markdown(f.read())
