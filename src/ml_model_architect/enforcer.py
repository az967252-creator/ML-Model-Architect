#!/usr/bin/env python3
"""Validate a DECISIONS.md ledger against the constitution (rules B1/B4).

Checks, for every row in the decision ledger:
  * Type must belong to the closed taxonomy:
    (framing, technique, parameter, threshold, deployment, metric, evaluation, data, other)
  * 'other' and 'framing' require a detailed reason of at least 20 characters
  * For technical decisions:
    - Reference must be a DOI (with locator), a trusted URL, or an allowed token (heuristic, reference-gap, ...)
    - DOIs MUST include a specific locator (e.g. '@ Sec 3.1', '(page 5)', '[Table 2]')
    - Heuristic ratio must not exceed --max-heuristic-ratio (default 0.4)
    - With --online, every DOI really exists (Crossref, then DataCite).

Exit codes: 0 = OK, 1 = violations, 2 = online verification incomplete
(network error) -- unless --allow-offline is given.
"""
import argparse
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote, urlparse

import yaml

ALLOWED_TOKENS = {"heuristic", "reference-gap", "n/a (business context)"}
CLOSED_TYPES = {
    "framing",
    "technique",
    "parameter",
    "threshold",
    "deployment",
    "metric",
    "evaluation",
    "data",
    "other",
}
CHECKED_TYPES = {"technique", "parameter", "threshold", "deployment", "metric", "evaluation"}
REQUIRED_HEADERS = ("stage", "type", "question", "reference")

DOI_RE = re.compile(r"10\.\d{4,9}/[^\s|;,()<>]+")
URL_RE = re.compile(r"https?://[^\s|;,()<>]+")
ARXIV_RE = re.compile(r"arxiv:\s*(\d{4}\.\d{4,5})", re.IGNORECASE)
SEPARATOR_RE = re.compile(r"^\|[\s:\-|]+\|$")
DOI_HOSTS = {"doi.org", "dx.doi.org"}
LOCATOR_RE = re.compile(r"(@|sec|section|page|p\.|pp\.|table|fig|figure|ch\.|chapter)\s*[0-9a-zA-Z\.\-_]+", re.IGNORECASE)


# --------------------------------------------------------------------------
# Trusted-URL whitelist
# --------------------------------------------------------------------------
def load_whitelist(path=None):
    """Return a list of (host, path_prefix) rules from trusted_domains.yaml."""
    if path:
        path = Path(path)
    else:
        root = Path(__file__).resolve().parent.parent
        path = root / "references" / "trusted_domains.yaml"
        if not path.exists():
            path = root / "trusted_domains.yaml"
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rules = []
    for entry in data.get("domains", []):
        entry = re.sub(r"^https?://", "", str(entry).strip().lower())
        host, _, rest = entry.partition("/")
        host = host.removeprefix("www.")
        prefix = "/" + rest.strip("/") if rest.strip("/") else ""
        if host:
            rules.append((host, prefix))
    return rules


def is_trusted_url(url, rules):
    """True if the URL's real hostname (and path, when the rule has one) is whitelisted."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    host = (parsed.hostname or "").lower().removeprefix("www.")
    if parsed.scheme not in ("http", "https") or not host:
        return False
    path = parsed.path or "/"
    for rule_host, prefix in rules:
        if host == rule_host or host.endswith("." + rule_host):
            if not prefix or path == prefix or path.startswith(prefix + "/"):
                return True
    return False


# --------------------------------------------------------------------------
# Online DOI check (optional)
# --------------------------------------------------------------------------
def check_doi(doi, retries=2):
    """Return 'OK', 'FAKE' or 'NETWORK_ERROR'. Crossref first, DataCite second."""
    import requests

    path = quote(doi, safe="/")
    for attempt in range(retries + 1):
        try:
            r = requests.get(f"https://api.crossref.org/works/{path}", timeout=10)
            if r.status_code == 200:
                return "OK"
            if r.status_code == 404:
                d = requests.get(f"https://api.datacite.org/dois/{path}", timeout=10)
                if d.status_code == 200:
                    return "OK"
                if d.status_code == 404:
                    return "FAKE"
        except requests.exceptions.RequestException:
            pass
        if attempt < retries:
            time.sleep(1.5 * (attempt + 1))
    return "NETWORK_ERROR"


# --------------------------------------------------------------------------
# Ledger parsing
# --------------------------------------------------------------------------
def parse_tables(text):
    """Split markdown into tables; return a list of (header_cells, [(line, cells), ...])."""
    blocks, current = [], []
    for line in text.splitlines():
        if line.strip().startswith("|"):
            current.append(line.strip())
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)

    tables = []
    for block in blocks:
        rows = [ln for ln in block if not SEPARATOR_RE.match(ln)]
        if not rows:
            continue
        split = lambda ln: [c.strip() for c in ln.strip().strip("|").split("|")]
        tables.append((split(rows[0]), [(ln, split(ln)) for ln in rows[1:]]))
    return tables


def evaluate_reference(ref, rules, locator_text=""):
    """Return (problems, dois_to_check) for one Reference cell."""
    ref = ref.strip()
    if not ref:
        return ["empty reference"], []
    if ref.lower() in ALLOWED_TOKENS:
        return [], []

    dois = [d.rstrip(".") for d in DOI_RE.findall(ref)]
    dois += [f"10.48550/arXiv.{i}" for i in ARXIV_RE.findall(ref)]
    urls = [u.rstrip(".") for u in URL_RE.findall(ref)
            if (urlparse(u).hostname or "").lower() not in DOI_HOSTS]

    problems = [f"untrusted URL {u}" for u in urls if not is_trusted_url(u, rules)]
    if not dois and not urls:
        problems.append(f"'{ref}' is neither a DOI, a trusted URL, nor an allowed token")

    # Structural check for DOI locator
    if dois:
        has_locator = bool(LOCATOR_RE.search(ref) or (locator_text and LOCATOR_RE.search(locator_text)) or "@" in ref)
        if not has_locator:
            for d in dois:
                problems.append(f"DOI '{d}' missing specific locator (section/page/table, e.g. '@ Sec 3.1')")

    return problems, dois


# --------------------------------------------------------------------------
# Main logic
# --------------------------------------------------------------------------
def enforce(filepath, online=False, allow_offline=False, max_heuristic_ratio=0.4, doi_checker=check_doi, whitelist=None):
    """Check one ledger file. Returns the exit code (0, 1 or 2)."""
    path = Path(filepath)
    if not path.exists():
        print(f"ERROR: {filepath} not found.")
        return 1

    rules = load_whitelist() if whitelist is None else whitelist
    tables = parse_tables(path.read_text(encoding="utf-8"))
    ledgers = [t for t in tables if all(h in [x.lower() for x in t[0]] for h in REQUIRED_HEADERS)]
    if not ledgers:
        print("❌ ERROR: no decision table with the headers Stage, Type, Question, Reference.")
        return 1

    violations, unverified, checked, verified = 0, 0, 0, 0
    heuristic_count = 0

    for header, rows in ledgers:
        h = [x.lower() for x in header]
        type_i = h.index("type")
        q_i = h.index("question")
        ref_i = h.index("reference")
        reason_i = h.index("reason") if "reason" in h else None
        locator_i = h.index("locator") if "locator" in h else None

        for line, cells in rows:
            if len(cells) != len(h):
                print(f"❌ VIOLATION: malformed row ({len(cells)} cells, expected {len(h)}): {line[:50]}...")
                violations += 1
                continue

            raw_type = cells[type_i].strip().lower()
            question = cells[q_i].strip()
            reason = cells[reason_i].strip() if reason_i is not None and reason_i < len(cells) else ""
            locator_text = cells[locator_i].strip() if locator_i is not None and locator_i < len(cells) else ""
            ref = cells[ref_i].strip()

            # Rule 1: Closed set of decision types
            if raw_type not in CLOSED_TYPES:
                print(f"❌ VIOLATION: decision '{question}' has unknown type '{raw_type}'. Must be one of {sorted(CLOSED_TYPES)}.")
                violations += 1
                continue

            # Rule 2: 'other' and 'framing' require reason >= 20 characters
            if raw_type in {"other", "framing"}:
                if len(reason) < 20:
                    print(f"❌ VIOLATION: decision '{question}' (type '{raw_type}') requires a reason of >= 20 characters (got {len(reason)}).")
                    violations += 1

            if raw_type not in CHECKED_TYPES:
                continue

            checked += 1

            # Track heuristics count
            if ref.lower() in {"heuristic", "reference-gap"}:
                heuristic_count += 1

            problems, dois = evaluate_reference(ref, rules, locator_text=locator_text)
            for p in problems:
                print(f"❌ VIOLATION: decision '{question}': {p}")
                violations += 1

            if online:
                for doi in dois:
                    status = doi_checker(doi)
                    if status == "OK":
                        verified += 1
                    elif status == "FAKE":
                        print(f"❌ FAKE DOI: decision '{question}' cites {doi}")
                        violations += 1
                    elif status == "NETWORK_ERROR":
                        print(f"⚠️ could not verify {doi} (network error)")
                        unverified += 1

    # Check heuristic ratio
    if checked > 0:
        ratio = heuristic_count / checked
        print(f"ℹ️ Heuristic references: {heuristic_count}/{checked} ({ratio:.1%}, max allowed: {max_heuristic_ratio:.1%})")
        if ratio > max_heuristic_ratio:
            print(f"❌ VIOLATION: heuristic ratio {ratio:.1%} exceeds maximum allowed threshold of {max_heuristic_ratio:.1%}.")
            violations += 1

    if violations:
        print(f"\n❌ Found {violations} violation(s) in {checked} technical decision(s).")
        return 1
    if unverified and not allow_offline:
        print(f"\n⚠️ Verification INCOMPLETE: {unverified} DOI(s) could not be checked.")
        return 2
    detail = f"{verified} DOI(s) verified online" if online else "formats only, no network check"
    print(f"✅ {checked} technical decision(s) OK ({detail}).")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", default=["examples/delivery-delay-prediction/DECISIONS.md"])
    parser.add_argument("--online", action="store_true", help="also verify every DOI on Crossref/DataCite")
    parser.add_argument("--allow-offline", action="store_true", help="network errors are warnings, not failures")
    parser.add_argument("--max-heuristic-ratio", type=float, default=0.4, help="maximum ratio of heuristic/reference-gap decisions (default 0.4)")
    args = parser.parse_args(argv)
    worst = 0
    for f in args.files:
        print(f"== {f}")
        worst = max(worst, enforce(f, online=args.online, allow_offline=args.allow_offline, max_heuristic_ratio=args.max_heuristic_ratio))
    return worst


if __name__ == "__main__":
    sys.exit(main())
