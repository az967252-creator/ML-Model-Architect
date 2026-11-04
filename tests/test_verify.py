import subprocess
import sys
import os
from pathlib import Path

# Create a dummy YAML to test failures
bad_yaml = r"""
groups:
  - id: "test"
    name: "Test"
    refs:
      - citation: "No title"
        title: ""
        year: 2020
        doi_or_url: "10.1000/182"
      - citation: "Bad DOI"
        title: "Some title"
        year: 2020
        doi_or_url: "10.9999/fake"
      - citation: "Bad Year"
        title: "XGBoost: A Scalable Tree Boosting System"
        year: 1990
        doi_or_url: "10.1145/2939672.2939785"
"""

Path("references_to_verify.yaml").write_text(bad_yaml, encoding="utf-8")

print("Running verify_dois.py against bad YAML (expecting exit code 1)...")
result = subprocess.run([sys.executable, "scripts/verify_dois.py"], capture_output=True, text=True)
print(result.stdout)

if result.returncode == 1:
    print("✅ TEST PASSED: Script correctly failed on bad references.")
else:
    print("❌ TEST FAILED: Script did not exit with 1.")
    sys.exit(1)
