"""
knowledge_extractor.py
----------------------
Converts brochure page text into structured automotive knowledge
using the automotive schema (data/schema/automotive_schema_v1.json).

Uses keyword-based extraction (no LLM required) and optionally
Gemini-based extraction for richer structured output.

Outputs structured JSON to data/structured_data/.
"""

import os
import json
import re


# ─────────────────────────────────────────────
#  Configuration
# ─────────────────────────────────────────────

SCHEMA_PATH = "data/schema/automotive_schema_v1.json"
OUTPUT_DIR = "data/structured_data"

# Regex patterns for common automotive specs
PATTERNS = {
    "engine_displacement": r"(\d[\d.,]*\s*(?:L|liter|litre|cc|cm3))",
    "horsepower": r"(\d+)\s*(?:hp|bhp|ps|kw)",
    "torque": r"(\d+)\s*(?:nm|n\.m|newton)",
    "rpm": r"(\d[\d,]+)\s*rpm",
    "top_speed": r"(\d+)\s*km/?h",
    "mileage": r"(\d+\.?\d*)\s*(?:kmpl|km/l|mpg)",
    "airbags": r"(\d+)\s*airbag",
    "length": r"length[:\s]+(\d{4,5})\s*mm",
    "width": r"width[:\s]+(\d{3,4})\s*mm",
    "height": r"height[:\s]+(\d{3,4})\s*mm",
    "wheelbase": r"wheelbase[:\s]+(\d{4,5})\s*mm",
    "ground_clearance": r"ground\s*clearance[:\s]+(\d{2,3})\s*mm",
    "boot_space": r"boot\s*(?:space|capacity)[:\s]+(\d+)\s*(?:litres?|L)",
    "fuel_tank": r"fuel\s*tank[:\s]+(\d+)\s*(?:litres?|L)",
    "seating_capacity": r"(\d)\s*(?:seater|seat\s*capacity|seats)",
}


def load_schema():
    """Loads the automotive schema template."""
    if not os.path.exists(SCHEMA_PATH):
        return {}
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_specs_from_text(text):
    """
    Uses regex patterns to extract structured automotive specs
    from raw page text.

    Returns:
        dict of extracted values keyed by spec name
    """
    text_lower = text.lower()
    extracted = {}

    for spec, pattern in PATTERNS.items():
        match = re.search(pattern, text_lower)
        if match:
            extracted[spec] = match.group(1).strip()

    return extracted


def extract_safety_features(text):
    """Extracts a list of safety features mentioned in text."""
    safety_terms = [
        "abs", "ebd", "esc", "airbag", "hill assist", "hill descent",
        "traction control", "blind spot", "lane keep assist",
        "lane departure", "forward collision", "autonomous emergency braking",
        "aeb", "parking sensor", "rear camera", "360 camera",
        "tyre pressure", "tpms", "isofix", "seatbelt pretensioner"
    ]
    text_lower = text.lower()
    return [term for term in safety_terms if term in text_lower]


def extract_infotainment_features(text):
    """Extracts infotainment features mentioned in text."""
    infotainment_terms = [
        "android auto", "apple carplay", "bluetooth", "usb",
        "navigation", "gps", "wifi", "hotspot", "voice recognition",
        "bluelink", "connected car", "ota", "over-the-air",
        "wireless charging", "rear entertainment"
    ]
    text_lower = text.lower()
    return [term for term in infotainment_terms if term in text_lower]


def extract_exterior_features(text):
    """Extracts exterior features mentioned in text."""
    exterior_terms = [
        "led headlamp", "drl", "led tail lamp", "alloy wheel",
        "roof rail", "sunroof", "panoramic sunroof", "electric sunroof",
        "chrome", "shark fin antenna", "body kit", "spoiler",
        "rear wiper", "auto headlamp", "fog lamp", "projector lamp"
    ]
    text_lower = text.lower()
    return [term for term in exterior_terms if term in text_lower]


def extract_knowledge_from_page(page_text, page_number, brand, model):
    """
    Extracts structured knowledge from a single brochure page.

    Returns:
        dict: Structured knowledge block for this page
    """
    schema = load_schema()

    # Start with schema as template
    knowledge = {
        "brand": brand,
        "model": model,
        "page_number": page_number,
        "raw_text_length": len(page_text)
    }

    # Merge schema categories
    for category in schema:
        knowledge[category] = {}

    # Extract numerical specs
    specs = extract_specs_from_text(page_text)
    if specs:
        if "engine_displacement" in specs or "horsepower" in specs or "torque" in specs:
            knowledge["engine_powertrain"].update(specs)
        if "length" in specs or "width" in specs or "wheelbase" in specs:
            knowledge["dimensions"].update(specs)
        if "mileage" in specs or "top_speed" in specs:
            knowledge["performance"].update(specs)
        if "boot_space" in specs or "fuel_tank" in specs:
            knowledge["capacity"].update(specs)
        if "seating_capacity" in specs:
            knowledge["seating"].update(specs)

    # Extract feature lists
    safety_features = extract_safety_features(page_text)
    if safety_features:
        knowledge["safety"]["features"] = safety_features
        if "airbags" in specs:
            knowledge["safety"]["airbag_count"] = specs["airbags"]

    infotainment_features = extract_infotainment_features(page_text)
    if infotainment_features:
        knowledge["infotainment"]["features"] = infotainment_features

    exterior_features = extract_exterior_features(page_text)
    if exterior_features:
        knowledge["exterior"]["features"] = exterior_features

    return knowledge


def extract_knowledge_from_brochure(
    pages,
    brand,
    model,
    output_dir=OUTPUT_DIR
):
    """
    Processes all pages of a brochure and saves structured knowledge JSON.

    Args:
        pages      : List of page text strings
        brand      : e.g. "Hyundai"
        model      : e.g. "Creta"
        output_dir : Where to save structured output

    Returns:
        List of per-page knowledge dicts
    """
    os.makedirs(output_dir, exist_ok=True)

    all_knowledge = []

    for page_num, page_text in enumerate(pages, start=1):
        knowledge = extract_knowledge_from_page(
            page_text, page_num, brand, model
        )
        all_knowledge.append(knowledge)

    # Save per-model file
    filename = f"{brand}_{model}_knowledge.json"
    output_path = os.path.join(output_dir, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_knowledge, f, indent=2, ensure_ascii=False)

    print(f"[KnowledgeExtractor] Saved {len(pages)} page knowledge blocks -> {output_path}")

    return all_knowledge


def merge_model_knowledge(brand, model, output_dir=OUTPUT_DIR):
    """
    Merges per-page knowledge into a single consolidated model knowledge dict.
    Non-empty values from individual pages are merged into one flat structure.
    """
    filename = f"{brand}_{model}_knowledge.json"
    path = os.path.join(output_dir, filename)

    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        all_pages = json.load(f)

    merged = {
        "brand": brand,
        "model": model,
        "total_pages_analyzed": len(all_pages)
    }

    for page in all_pages:
        for key, value in page.items():
            if key in ("brand", "model", "page_number", "raw_text_length"):
                continue
            if isinstance(value, dict) and value:
                if key not in merged:
                    merged[key] = {}
                merged[key].update(value)
            elif isinstance(value, list) and value:
                if key not in merged:
                    merged[key] = []
                merged[key] = list(set(merged[key] + value))

    # Save consolidated file
    consolidated_path = os.path.join(
        output_dir, f"{brand}_{model}_consolidated.json"
    )
    with open(consolidated_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    print(f"[KnowledgeExtractor] Consolidated knowledge -> {consolidated_path}")
    return merged


# ─────────────────────────────────────────────
#  Standalone test
# ─────────────────────────────────────────────

if __name__ == "__main__":

    sample_pages = [
        # Page 1 - Engine
        "The 1.5L CRDi diesel engine produces 115 bhp and 250 Nm torque "
        "at 1500 rpm with 6-speed manual transmission.",
        # Page 2 - Safety
        "Creta features 6 airbags, ABS with EBD, ESC, Hill Assist, "
        "TPMS, rear parking sensors, and ISOFIX child seat anchors.",
        # Page 3 - Infotainment
        "10.25-inch touchscreen with Android Auto, Apple CarPlay, "
        "Bluetooth, USB, navigation, and Hyundai BlueLink.",
        # Page 4 - Dimensions
        "Length: 4300 mm, Width: 1790 mm, Height: 1635 mm, "
        "Wheelbase: 2610 mm, Ground Clearance: 190 mm.",
    ]

    results = extract_knowledge_from_brochure(
        pages=sample_pages,
        brand="Hyundai",
        model="Creta_Test"
    )

    merged = merge_model_knowledge("Hyundai", "Creta_Test")

    print("\n--- Consolidated Knowledge ---")
    print(json.dumps(merged, indent=2))
