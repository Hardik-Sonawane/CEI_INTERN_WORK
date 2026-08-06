# DriveWise Extraction Rules

## Purpose

These rules guide the structured extraction of automotive information from
Hyundai brochure pages. They apply to both the regex-based `knowledge_extractor.py`
and the LLM-based Gemini extraction prompt.

---

## General Rules

1. **Extract only what is stated** – Do not infer, estimate, or fabricate information.
2. **Preserve exact values** – Include units exactly as written (e.g., "115 bhp", "250 Nm").
3. **Handle abbreviations** – Map common abbreviations to full forms where unambiguous:
   - ABS → Anti-lock Braking System
   - EBD → Electronic Brakeforce Distribution
   - ESC → Electronic Stability Control
   - ADAS → Advanced Driver Assistance Systems
   - CRDi → Common Rail Direct Injection
   - VTVT → Variable Timing with Variable Timing on both Intake & Exhaust
4. **Empty categories** – If a category has no data on a page, output `{}` or `[]` — never `null`.
5. **No marketing language** – Skip subjective phrases like "world-class", "premium feel".

---

## Category-Specific Rules

### Engine / Powertrain
- Extract displacement in cc or Litre form, whichever is stated.
- Identify fuel type: Petrol, Diesel, Electric, Hybrid, CNG.
- Extract max power and max torque with RPM ranges if given.
- Transmission: Manual, Automatic, AMT, DCT, CVT, iMT — note number of speeds.

### Safety
- Count airbags explicitly if stated (e.g., "6 airbags").
- List ADAS features as individual items.
- Distinguish active safety (ABS, ESC) from passive safety (airbags, seatbelts).

### Dimensions
- All values must include unit "mm" for lengths; "litres" for volumes.
- Do not mix cm and mm in the same field.

### Performance
- ARAI-certified mileage takes priority; mention "ARAI" label if present.
- Acceleration expressed as "0-100 km/h in X seconds".
- Top speed in km/h.

### Infotainment
- Note screen diagonal size (inches) explicitly.
- List connectivity features as separate items (Android Auto, Apple CarPlay, etc.).
- BlueLink = Hyundai's connected car platform — list its features separately if mentioned.

### Variants
- Note variant name exactly (e.g., "E", "S", "SX", "SX(O)", "N Line").
- Extract prices only if explicitly stated — include "ex-showroom" or "on-road" label.

### Colors
- List all color names exactly as printed (e.g., "Ranger Khaki", "Titan Grey").
- Note whether a color is standard, optional, or exclusive to a variant.

---

## Handling Ambiguity

| Situation | Rule |
|---|---|
| Value present but unit unclear | Extract value as-is, flag as "unit_unclear" |
| Feature mentioned vaguely | Include it but mark as "mentioned" not "confirmed" |
| Table data without headers | Skip — cannot safely map to schema |
| Image-only pages | Output all empty categories |

---

## Output Quality Checks

After extraction, verify:
- [ ] All numerical specs have units
- [ ] Safety feature list has no duplicates
- [ ] No category contains `null` — use `{}` or `[]` instead
- [ ] Variant names match the official Hyundai naming convention
- [ ] Airbag count is a number, not a description
