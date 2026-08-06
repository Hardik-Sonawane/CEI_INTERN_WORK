"""
page_classifier.py
------------------
Analyzes each brochure page individually and classifies it into
an automotive section (Engine, Safety, Interior, etc.) using a
structured keyword dictionary.

Outputs per-page JSON metadata files to data/page_metadata/.
"""

import os
import json


# ─────────────────────────────────────────────
#  Automotive keyword dictionary
# ─────────────────────────────────────────────

SECTION_KEYWORDS = {
    "Engine": [
        "engine", "displacement", "cc", "horsepower", "hp", "torque",
        "rpm", "cylinder", "petrol", "diesel", "turbo", "transmission",
        "gearbox", "clutch", "drivetrain", "4wd", "awd", "fwd", "rwd",
        "powertrain", "crdi", "mpfi", "vtvt", "dual clutch", "dct",
        "automatic", "manual", "amt", "cvt", "imt"
    ],
    "Safety": [
        "airbag", "abs", "ebd", "esc", "traction control", "brake",
        "hill assist", "rear camera", "parking sensor", "blind spot",
        "lane", "collision", "impact", "isofix", "seatbelt", "pretensioner",
        "safety", "crash", "pedestrian", "emergency brake", "stability"
    ],
    "Interior": [
        "interior", "cabin", "dashboard", "instrument cluster", "steering",
        "seat", "leather", "upholstery", "sunroof", "panoramic", "ambient",
        "lighting", "headroom", "legroom", "armrest", "ventilated", "heated"
    ],
    "Exterior": [
        "exterior", "grille", "bumper", "alloy wheel", "tyre", "tire",
        "color", "colour", "paint", "body", "spoiler", "antenna", "chrome",
        "roof rail", "fender", "door handle", "side mirror", "headlamp",
        "tail lamp", "fog lamp", "drl", "led"
    ],
    "Dimensions": [
        "length", "width", "height", "wheelbase", "ground clearance",
        "turning radius", "mm", "dimension", "footprint", "overhang"
    ],
    "Performance": [
        "0-100", "top speed", "acceleration", "mileage", "kmpl", "range",
        "fuel economy", "performance", "sport mode", "drive mode",
        "adrenaline", "0 to 100", "sprint"
    ],
    "Infotainment": [
        "infotainment", "touchscreen", "display", "android auto",
        "apple carplay", "navigation", "gps", "speaker", "audio",
        "bluetooth", "wifi", "hotspot", "usb", "voice", "bluelink",
        "connected car", "ota", "over-the-air"
    ],
    "Features": [
        "feature", "convenience", "cruise control", "auto hold",
        "paddle shift", "wireless charging", "drive mode", "smart key",
        "push button", "rear ac", "air purifier", "tpms", "auto wiper",
        "rain sensing", "auto headlamp", "walk-in", "follow-me-home"
    ],
    "Variants": [
        "variant", "trim", "e", "s", "sx", "ex", "ht", "st", "n line",
        "price", "on-road", "ex-showroom", "base", "top", "mid", "edition"
    ],
    "Overview": [
        "welcome", "about", "brand", "hyundai", "innovation", "design",
        "philosophy", "introduction", "overview", "award", "heritage",
        "commitment", "value", "trust"
    ]
}


# Minimum score threshold to label a page
SCORE_THRESHOLD = 1


def classify_page(page_text: str) -> dict:
    """
    Classifies a single page of brochure text.

    Returns:
        dict with keys:
            - primary_section (str)
            - keywords_found  (list[str])
            - importance_score (int)
            - section_scores  (dict[str, int])
    """
    text_lower = page_text.lower()

    section_scores = {}
    all_keywords_found = []

    for section, keywords in SECTION_KEYWORDS.items():
        hits = [kw for kw in keywords if kw in text_lower]
        section_scores[section] = len(hits)
        all_keywords_found.extend(hits)

    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for kw in all_keywords_found:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)

    # Determine primary section
    best_section = max(section_scores, key=lambda s: section_scores[s])
    best_score = section_scores[best_section]

    if best_score < SCORE_THRESHOLD:
        best_section = "Unknown"

    # Importance score = total keyword hits (proxy for information density)
    importance_score = sum(section_scores.values())

    return {
        "primary_section": best_section,
        "keywords_found": unique_keywords,
        "importance_score": importance_score,
        "section_scores": section_scores
    }


def classify_brochure(
    pages,
    brand,
    model,
    output_dir="data/page_metadata"
):
    """
    Classifies all pages of a brochure and saves per-page metadata JSON.

    Args:
        pages      : List of page text strings (index = page number)
        brand      : Brand name, e.g. "Hyundai"
        model      : Model name, e.g. "Creta"
        output_dir : Directory to save JSON files

    Returns:
        List of page metadata dicts
    """
    os.makedirs(output_dir, exist_ok=True)

    all_page_metadata = []

    for page_num, page_text in enumerate(pages, start=1):

        result = classify_page(page_text)

        page_meta = {
            "brand": brand,
            "model": model,
            "page_number": page_num,
            "primary_section": result["primary_section"],
            "keywords_found": result["keywords_found"],
            "importance_score": result["importance_score"],
            "section_scores": result["section_scores"]
        }

        all_page_metadata.append(page_meta)

    # Save combined JSON for the model
    output_filename = f"{brand}_{model}_page_metadata.json"
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_page_metadata, f, indent=2, ensure_ascii=False)

    print(f"[PageClassifier] Saved {len(pages)} page records -> {output_path}")

    return all_page_metadata


def load_page_metadata(
    brand,
    model,
    output_dir="data/page_metadata"
):
    """
    Loads previously generated page metadata for a given brand/model.
    """
    filename = f"{brand}_{model}_page_metadata.json"
    path = os.path.join(output_dir, filename)

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_pages_by_section(
    brand,
    model,
    section,
    output_dir="data/page_metadata"
):
    """
    Returns a list of page numbers that belong to a given section.
    Useful for pre-filtering before semantic search.
    """
    metadata = load_page_metadata(brand, model, output_dir)
    return [
        m["page_number"]
        for m in metadata
        if m["primary_section"].lower() == section.lower()
    ]


# ─────────────────────────────────────────────
#  Standalone test
# ─────────────────────────────────────────────

if __name__ == "__main__":

    sample_pages = [
        # Page 1 - Overview
        "Welcome to Hyundai. Our brand stands for innovation, trust, and design.",
        # Page 2 - Engine
        "The 1.5L CRDi diesel engine produces 115 hp and 250 Nm torque "
        "with a 6-speed manual transmission.",
        # Page 3 - Safety
        "Creta features 6 airbags, ABS with EBD, ESC, Hill Start Assist, "
        "and rear parking sensors.",
        # Page 4 - Infotainment
        "The 10.25-inch touchscreen supports Android Auto, Apple CarPlay, "
        "Bluetooth, and Hyundai BlueLink connected car technology.",
    ]

    results = classify_brochure(
        pages=sample_pages,
        brand="Hyundai",
        model="Creta_Test"
    )

    for r in results:
        print(
            "Page {:>2} | Section: {:<15} | Importance: {:>3} | Keywords: {}".format(
                r["page_number"],
                r["primary_section"],
                r["importance_score"],
                r["keywords_found"]
            )
        )
