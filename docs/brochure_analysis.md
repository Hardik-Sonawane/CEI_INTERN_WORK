# Hyundai Brochure Analysis – Architecture

## Objective

Analyze all Hyundai brochures and identify every type of information available,
then convert that information into structured, metadata-rich knowledge that
powers more accurate RAG retrieval.

This document describes the upgraded **DriveWise Document Intelligence Pipeline**.

---

## Phase 1 – Completed (Base RAG)

| Component | Description |
|---|---|
| `pdf_parser.py` | Extracts text from PDF brochures page-by-page |
| `cleaner.py` | Normalizes raw text (whitespace, encoding) |
| `chunker.py` | Splits text into semantic chunks with overlap |
| `metadata_generator.py` | Attaches brand, model, page, section metadata to chunks |
| `embedding_generator.py` | Encodes chunks → ChromaDB vector store |
| `retriever.py` | Semantic search with metadata filtering |
| `reranker.py` | Cross-encoder re-ranking of retrieved results |
| `context_manager.py` | Builds prompt context from ranked chunks |
| `gemini_generator.py` | Generates grounded answers via Gemini API |
| `source_attribution.py` | Formats source references in the response |
| `app_pipeline.py` | Orchestrates the full RAG pipeline |
| `streamlit_app.py` | Interactive Streamlit UI |

---

## Phase 2 – In Progress (Metadata-Aware Intelligence)

### New Components

#### `page_classifier.py`
- Classifies each brochure page into an automotive section
- Uses a structured keyword dictionary (10 categories)
- Assigns an **importance score** based on keyword density
- Outputs: `data/page_metadata/<Brand>_<Model>_page_metadata.json`

**Sections identified:**
- Engine / Powertrain
- Safety & ADAS
- Interior
- Exterior
- Dimensions
- Performance & Fuel Economy
- Infotainment & Connectivity
- Features & Convenience
- Variants & Pricing
- Overview / Brand

#### `knowledge_extractor.py`
- Extracts structured automotive facts from page text
- Regex-based extraction for numerical specs
- Keyword-based extraction for feature lists
- Maps to `data/schema/automotive_schema_v1.json`
- Outputs: `data/structured_data/<Brand>_<Model>_knowledge.json`
- Merges into: `data/structured_data/<Brand>_<Model>_consolidated.json`

#### `brochure_analyzer.py`
- Orchestrates: PDF Parse → Page Classify → Knowledge Extract → Merge
- Can process a single brochure or all PDFs in `data/pdfs/`

#### `prompts/automotive_extraction_prompt.txt`
- Structured Gemini prompt for AI-powered knowledge extraction
- Phase 3 will use this for richer, LLM-driven structured output

---

## Master Automotive Schema Categories

Defined in `data/schema/automotive_schema_v1.json`:

| Category | Description |
|---|---|
| `vehicle_information` | Brand, model, variant |
| `variants` | Trim levels and pricing |
| `engine_powertrain` | Engine specs, transmission, drivetrain |
| `performance` | Mileage, top speed, acceleration |
| `fuel_efficiency` | ARAI-certified figures |
| `dimensions` | L×W×H, wheelbase, clearance |
| `capacity` | Boot space, fuel tank |
| `suspension_brakes` | Suspension type, brake type |
| `wheels_tyres` | Tyre size, alloy specs |
| `exterior` | Body features, lighting, colours |
| `interior` | Cabin features, materials |
| `comfort_convenience` | HVAC, cruise control, smart features |
| `infotainment` | Screen, connectivity, audio |
| `connectivity` | BlueLink, OTA, hotspot |
| `safety` | Airbags, ADAS, passive safety |
| `adas` | Lane assist, AEB, blind spot |
| `lighting` | LED, DRL, projector |
| `seating` | Capacity, ventilation, adjustment |
| `climate_control` | AC type, rear AC, air purifier |
| `storage` | Boot, cabin storage points |
| `colors` | Available colour options |
| `warranty` | Warranty terms |
| `accessories` | OEM accessories |

---

## Data Flow

```
data/pdfs/<Model>.pdf
       |
       v
  pdf_parser.py  --> raw page text (list of strings)
       |
       +----> page_classifier.py --> data/page_metadata/
       |
       +----> knowledge_extractor.py --> data/structured_data/
       |
       v
  chunker.py + metadata_generator.py
       |
       v
  embedding_generator.py --> chroma_db/
       |
       v
  retriever.py (semantic search + metadata filter)
       |
       v
  reranker.py --> context_manager.py --> gemini_generator.py
       |
       v
  Streamlit UI (app/streamlit_app.py)
```
