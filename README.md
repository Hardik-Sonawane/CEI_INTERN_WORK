# Celebal Project - Hyundai RAG System

A Retrieval-Augmented Generation (RAG) system for querying Hyundai vehicle manuals.

## Project Structure

```
celebal_project/
├── data/
│   ├── raw/           # Raw PDF manuals (Hyundai vehicles)
│   ├── processed/     # Cleaned and processed text data
│   └── chunks/        # Chunked documents ready for embedding
├── chroma_db/         # Persistent Vector Database (ChromaDB)
├── logs/              # Application execution logs
├── notebooks/         # Jupyter notebooks for experiments
├── src/               # Core source code (loaders, chunkers, embeddings)
├── app/               # Application UI / API (FastAPI, Streamlit, etc.)
├── requirements.txt   # Python dependencies
├── README.md          # Project documentation
└── main.py            # Main entry point
```

## Setup & Running

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the main application:
   ```bash
   python main.py
   ```
