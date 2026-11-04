#!/usr/bin/env python3
import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime, timedelta

# arXiv API endpoint
ARXIV_API = "http://export.arxiv.org/api/query"

# Groups to search
GROUPS = {
    "01_Linear_Models": "all:logistic regression OR all:ridge regression",
    "03_Gradient_Boosting": "all:XGBoost OR all:LightGBM OR all:CatBoost",
    "04_Neural_Networks": "all:deep learning tabular data",
    "05_Tabular_Foundation": "all:TabPFN OR all:tabular foundation models",
    "12_Time_Series": "all:time series forecasting deep learning"
}

def fetch_latest(query):
    # Calculate date 30 days ago
    date_str = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
    
    params = {
        "search_query": query,
        "start": 0,
        "max_results": 3,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    response = requests.get(ARXIV_API, params=params)
    if response.status_code != 200:
        return []
        
    root = ET.fromstring(response.content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    papers = []
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
        published = entry.find('atom:published', ns).text[:10]
        link = entry.find('atom:id', ns).text
        papers.append({
            "title": title,
            "published": published,
            "url": link
        })
    return papers

def main():
    print("Fetching latest SOTA papers from arXiv...")
    results = {}
    
    for group, query in GROUPS.items():
        print(f"Searching for {group}...")
        results[group] = fetch_latest(query)
        
    # Save results to a markdown file for the PR
    with open("SOTA-UPDATES.md", "w", encoding="utf-8") as f:
        f.write("# 🚀 Automated State-of-the-Art (SOTA) Updates\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write("Here are the latest papers from the last 30 days. The AI agent should read these via MCP to stay updated.\n\n")
        
        for group, papers in results.items():
            f.write(f"## {group.replace('_', ' ')}\n\n")
            if not papers:
                f.write("*No new papers found this month.*\n\n")
                continue
            for p in papers:
                f.write(f"- **[{p['title']}]({p['url']})** (Published: {p['published']})\n")
            f.write("\n")
            
    print("Done. Check SOTA-UPDATES.md")

if __name__ == "__main__":
    main()
