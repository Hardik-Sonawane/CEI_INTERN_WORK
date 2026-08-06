"""
brochure_analyzer.py
--------------------
Orchestrates the full brochure analysis pipeline:
  1. Parse PDF pages
  2. Classify each page (page_classifier)
  3. Extract structured knowledge (knowledge_extractor)

Run this script once per brochure to generate:
  - data/page_metadata/<Brand>_<Model>_page_metadata.json
  - data/structured_data/<Brand>_<Model>_knowledge.json
  - data/structured_data/<Brand>_<Model>_consolidated.json
"""

import os
import sys


def _get_page_texts(pdf_path):
    """Extracts plain text strings from PDF, one per page."""
    # Allow running from project root
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from src.pdf_parser import extract_pdf
    pages_data = extract_pdf(pdf_path)
    return [p["text"] for p in pages_data]


def analyze_brochure(pdf_path, brand, model):
    """
    Full analysis pipeline for a single brochure PDF.

    Args:
        pdf_path : Absolute or relative path to the PDF file
        brand    : e.g. "Hyundai"
        model    : e.g. "Creta"
    """
    from src.page_classifier import classify_brochure
    from src.knowledge_extractor import extract_knowledge_from_brochure, merge_model_knowledge

    print(f"\n{'='*60}")
    print(f"  Analyzing: {brand} {model}")
    print(f"  PDF: {pdf_path}")
    print(f"{'='*60}")

    # Step 1 - Parse PDF into page-wise text
    print("\n[Step 1] Parsing PDF...")
    pages = _get_page_texts(pdf_path)
    print(f"  -> {len(pages)} pages extracted")


    # Step 2 - Classify each page
    print("\n[Step 2] Classifying pages...")
    page_metadata = classify_brochure(
        pages=pages,
        brand=brand,
        model=model
    )


    # Print quick summary
    section_counts = {}
    for pm in page_metadata:
        section = pm["primary_section"]
        section_counts[section] = section_counts.get(section, 0) + 1

    print("  Section distribution:")
    for section, count in sorted(section_counts.items(), key=lambda x: -x[1]):
        print(f"    {section:<20} {count:>3} pages")

    # Step 3 – Extract structured knowledge
    print("\n[Step 3] Extracting structured knowledge...")
    extract_knowledge_from_brochure(
        pages=pages,
        brand=brand,
        model=model
    )

    # Step 4 – Merge into consolidated knowledge
    print("\n[Step 4] Merging consolidated knowledge...")
    merged = merge_model_knowledge(brand, model)
    non_empty = {k: v for k, v in merged.items() if v and k not in ("brand", "model", "total_pages_analyzed")}
    print(f"  -> {len(non_empty)} categories with extracted data")

    print(f"\n[DONE] Analysis complete for {brand} {model}\n")
    return page_metadata, merged


def analyze_all_brochures(pdf_dir="data/pdfs", brand="Hyundai"):
    """
    Analyzes all PDFs in a directory.

    Args:
        pdf_dir : Directory containing PDF brochures
        brand   : Brand name to assign to all brochures
    """
    if not os.path.exists(pdf_dir):
        print(f"[ERROR] PDF directory not found: {pdf_dir}")
        return

    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]

    if not pdf_files:
        print(f"[WARNING] No PDF files found in {pdf_dir}")
        return

    print(f"\nFound {len(pdf_files)} PDFs to analyze:")
    for f in pdf_files:
        print(f"  - {f}")

    for pdf_file in pdf_files:
        model = os.path.splitext(pdf_file)[0]  # Use filename without extension as model name
        pdf_path = os.path.join(pdf_dir, pdf_file)
        analyze_brochure(pdf_path, brand, model)

    print("\n[ALL DONE] All brochures analyzed successfully.")


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":

    # Analyze a specific brochure
    # analyze_brochure("data/pdfs/Creta.pdf", "Hyundai", "Creta")

    # Or analyze all brochures in the pdfs folder
    analyze_all_brochures(pdf_dir="data/pdfs", brand="Hyundai")
