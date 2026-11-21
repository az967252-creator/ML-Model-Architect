#!/usr/bin/env python3
"""
pdf_to_markdown.py - Convert reference PDFs to Markdown with images.

Usage:
    pip install docling
    python scripts/pdf_to_markdown.py [--pdf-dir references/pdf] [--out-dir references/verified/full_text]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


def convert_pdfs(pdf_dir: Path, out_dir: Path, converter: Any = None) -> int:
    """Convert all PDF files in pdf_dir to Markdown in out_dir."""
    if not pdf_dir.exists():
        print(f"ERROR: PDF directory not found: {pdf_dir}", file=sys.stderr)
        return 1

    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}.")
        return 0

    if converter is None:
        try:
            from docling.document_converter import DocumentConverter
            converter = DocumentConverter()
        except ImportError:
            print("ERROR: Docling is required for PDF conversion. Install with: pip install docling", file=sys.stderr)
            return 1

    out_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    for pdf in pdf_files:
        print(f"Converting: {pdf.name}")
        try:
            result = converter.convert(pdf)
            md = result.document.export_to_markdown()
            out_file = out_dir / (pdf.stem + ".md")
            out_file.write_text(md, encoding="utf-8")
            print(f"  -> {out_file}")
            success_count += 1
        except Exception as e:
            print(f"  ERROR converting {pdf.name}: {e}", file=sys.stderr)

    print(f"Converted {success_count}/{len(pdf_files)} PDFs to Markdown.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert reference PDFs to Markdown.")
    parser.add_argument("--pdf-dir", type=Path, default=Path("references/pdf"), help="Directory containing PDF files")
    parser.add_argument("--out-dir", type=Path, default=Path("references/verified/full_text"), help="Output directory")
    args = parser.parse_args()

    return convert_pdfs(args.pdf_dir, args.out_dir)


if __name__ == "__main__":
    sys.exit(main())
