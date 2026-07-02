# Offline AI Intelligence Hub

Transform unstructured data into structured JSON — entirely offline, on CPU.

## Pipeline

```
Upload File → Detect Type → Extract Text → Clean & Normalize
  → Local SLM → Structured JSON → SQLite → Search & Export
```

## Project Structure

```
├── app.py                  # Streamlit entry point
├── config.py               # App configuration
├── ingestion/              # File intake stage
│   ├── upload.py           # File upload handling
│   └── extractor.py        # Text extraction
├── processing/             # Core processing stage
│   ├── detector.py         # File type detection
│   ├── cleaner.py          # Text cleaning & normalization
│   └── processor.py        # AI inference (placeholder)
├── pipeline/               # Pipeline utilities
│   └── export.py           # Search & export
├── llm/                    # LLM interface (placeholder)
│   ├── local_llm.py
│   └── prompts.py
├── schemas/                # Document schemas (placeholder)
├── storage/                # Persistence layer
│   ├── database.py         # SQLite operations
│   └── models.py           # Data models
├── utils/                  # Shared utilities
│   └── helpers.py
├── ui/                     # Streamlit UI
│   ├── pages/
│   │   ├── upload.py
│   │   ├── search.py
│   │   └── view.py
│   └── components/
│       ├── sidebar.py
│       └── file_info.py
├── data/                   # Runtime data (gitignored)
└── exports/                # Exported files (gitignored)
```

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Design Decisions

- **Offline-first**: All inference runs on CPU with local models.
- **Modular**: Each pipeline stage is an independent module.
- **Extensible**: PDF, image, and audio support can be added by extending the detector and extractor modules.
- **SQLite**: Zero-configuration local storage.
