#!/usr/bin/env python3
"""
verify_references.py - Convert reference PDFs to Markdown with images.

Usage:
    pip install docling
    python scripts/verify_references.py

Place PDF files in references/pdf/ before running.
"""
import sys
from pathlib import Path

try:
    from docling.document_converter import DocumentConverter
except ImportError:
    print("Install Docling first: pip install docling")
    sys.exit(1)

PDF_DIR = Path("references/pdf")
OUT_DIR = Path("references/verified/full_text")
OUT_DIR.mkdir(parents=True, exist_ok=True)

converter = DocumentConverter()

for pdf in sorted(PDF_DIR.glob("*.pdf")):
    print(f"Converting: {pdf.name}")
    try:
        result = converter.convert(pdf)
        md = result.document.export_to_markdown()
        out_file = OUT_DIR / (pdf.stem + ".md")
        out_file.write_text(md, encoding="utf-8")
        print(f"  -> {out_file}")
    except Exception as e:
        print(f"  ERROR: {e}")

print("Done. Check references/verified/full_text/")
