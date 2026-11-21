#!/usr/bin/env python3
"""
fetch_sota.py - Monthly State-of-the-Art (SOTA) Paper Harvester for ML Model Architect.

Scans arXiv via HTTPS with timeout and retry logic across all 12 ML algorithm groups.
Applies a strict 30-day cutoff and records candidate papers in references/candidates.yaml.
"""

import os
import sys
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent

ARXIV_API = "https://export.arxiv.org/api/query"
HDR = {"User-Agent": "ML-Model-Architect-SOTA/1.0 (mailto:az967252@users.noreply.github.com)"}
RETRY_DELAYS = (2, 5, 10)

GROUPS = {
    "01": {"name": "Linear Models", "query": 'all:"logistic regression" OR all:"ridge regression" OR all:"elastic net"'},
    "02": {"name": "Tree Models", "query": 'all:"decision tree" OR all:"random forest"'},
    "03": {"name": "Gradient Boosting", "query": 'all:XGBoost OR all:LightGBM OR all:CatBoost'},
    "04": {"name": "Neural Networks", "query": 'all:"tabular deep learning" OR all:"FT-Transformer"'},
    "05": {"name": "Tabular Foundation Models", "query": 'all:TabPFN OR all:"tabular foundation model"'},
    "06": {"name": "Clustering", "query": 'all:"k-means clustering" OR all:HDBSCAN'},
    "07": {"name": "Nearest Neighbors", "query": 'all:"k-nearest neighbors" OR all:"approximate nearest neighbors"'},
    "08": {"name": "Probabilistic Models", "query": 'all:"naive bayes" OR all:"gaussian process regression"'},
    "09": {"name": "Ensembles & Stacking", "query": 'all:"stacking classifier" OR all:"ensemble learning tabular"'},
    "10": {"name": "Dimensionality Reduction", "query": 'all:"principal component analysis" OR all:UMAP OR all:t-SNE'},
    "11": {"name": "Anomaly Detection", "query": 'all:"isolation forest" OR all:"tabular anomaly detection"'},
    "12": {"name": "Time Series", "query": 'all:"time series forecasting" OR all:"temporal fusion transformer"'}
}


def http_get_with_retry(url, params=None, timeout=15):
    """Fetches URL with timeout and retry on 429 or 5xx."""
    for attempt in range(len(RETRY_DELAYS) + 1):
        try:
            r = requests.get(url, params=params, headers=HDR, timeout=timeout)
            if r.status_code == 200:
                return r
            if r.status_code != 429 and r.status_code < 500:
                return r
        except requests.exceptions.RequestException:
            pass
        if attempt < len(RETRY_DELAYS):
            time.sleep(RETRY_DELAYS[attempt])
    return None


def fetch_group_candidates(group_id, info, cutoff_date):
    """Fetches candidate papers for a group published on or after cutoff_date."""
    params = {
        "search_query": info["query"],
        "start": 0,
        "max_results": 5,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }

    resp = http_get_with_retry(ARXIV_API, params=params)
    if resp is None or resp.status_code != 200:
        print(f"  [WARN] Failed to retrieve papers for Group {group_id} ({info['name']})")
        return []

    try:
        root = ET.fromstring(resp.content)
    except Exception as e:
        print(f"  [WARN] Failed to parse XML for Group {group_id}: {e}")
        return []

    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    papers = []

    for entry in root.findall('atom:entry', ns):
        title_el = entry.find('atom:title', ns)
        pub_el = entry.find('atom:published', ns)
        id_el = entry.find('atom:id', ns)

        if title_el is None or pub_el is None or id_el is None:
            continue

        title = title_el.text.strip().replace('\n', ' ')
        pub_str = pub_el.text[:10]  # YYYY-MM-DD
        url = id_el.text.strip()

        # Extract arXiv identifier and DOI
        arxiv_id = url.split("/abs/")[-1].split("v")[0]
        doi = f"10.48550/arXiv.{arxiv_id}" if arxiv_id else ""

        try:
            pub_date = datetime.strptime(pub_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        # Strict 30-day cutoff filter
        if pub_date >= cutoff_date:
            papers.append({
                "title": title,
                "published": pub_str,
                "url": url,
                "doi": doi
            })

    return papers


def main():
    print("=" * 60)
    print("🔬 SOTA Paper Candidate Harvester (30-day cutoff, 12 Groups)")
    print("=" * 60)

    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=30)).date()
    print(f"Scanning arXiv for papers published since: {cutoff_date.isoformat()}")

    all_candidates = []
    group_summary = {}

    for gid, ginfo in GROUPS.items():
        print(f"Checking Group {gid}: {ginfo['name']}...")
        papers = fetch_group_candidates(gid, ginfo, cutoff_date)
        group_summary[gid] = papers
        for p in papers:
            all_candidates.append({
                "group_id": gid,
                "group_name": ginfo["name"],
                "title": p["title"],
                "published": p["published"],
                "url": p["url"],
                "doi": p["doi"]
            })
        time.sleep(1)  # Respectful arXiv API pacing

    # Output to references/candidates.yaml
    candidates_path = ROOT / "references" / "candidates.yaml"
    output_data = {
        "harvested_at": datetime.now(timezone.utc).isoformat(),
        "cutoff_date": cutoff_date.isoformat(),
        "total_candidates": len(all_candidates),
        "candidates": all_candidates
    }

    candidates_path.parent.mkdir(parents=True, exist_ok=True)
    candidates_path.write_text(yaml.dump(output_data, sort_keys=False), encoding="utf-8")
    print(f"✅ Successfully wrote {len(all_candidates)} candidate papers to {candidates_path}")

    # Generate Markdown Summary
    sota_md_path = ROOT / "SOTA-UPDATES.md"
    with open(sota_md_path, "w", encoding="utf-8") as f:
        f.write("# Automated State-of-the-Art (SOTA) Candidates\n\n")
        f.write(f"Harvested on: {datetime.now(timezone.utc).strftime('%Y-%m-%d')} (30-day cutoff: {cutoff_date.isoformat()})\n\n")
        f.write("Candidate papers must be verified and peer-reviewed before inclusion in verified catalog.\n\n")
        for gid, papers in group_summary.items():
            f.write(f"## Group {gid} — {GROUPS[gid]['name']}\n\n")
            if not papers:
                f.write("*No new arXiv candidates identified in the last 30 days.*\n\n")
            else:
                for p in papers:
                    f.write(f"- **[{p['title']}]({p['url']})** (Published: {p['published']}, DOI: `{p['doi']}`)\n")
                f.write("\n")
    print(f"✅ Summary generated in {sota_md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
