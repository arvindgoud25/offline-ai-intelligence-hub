# Offline AI Intelligence Hub

Transform unstructured documents (PDFs, images, audio, text) into structured JSON — entirely offline, on CPU, using local LLMs.

## Features

- **100% Offline** — No cloud APIs, no data leaves your machine.
- **CPU-Only** — Runs on consumer hardware; no GPU required.
- **Multi-Format Ingestion** — Text (.txt, .csv, .json, .xml, .md), PDFs, images (OCR via Tesseract), and audio (transcription via Whisper).
- **AI-Powered Structuring** — Uses Ollama-backed local LLMs to extract structured JSON from raw text. Five built-in document schemas: Resume, Invoice, Medical Report, Meeting Notes, Research Paper.
- **Search & Filter** — Full-text search across documents with filters by document type, processing status, and date.
- **Export** — Download individual documents or bulk-export in JSON, CSV, JSONL, or plain text format.
- **Analytics Dashboard** — Visual insights: documents by type, file format, processing status, success/failure rates, average extraction time, and resource usage.
- **Performance Metrics** — Per-stage timers (text extraction, LLM inference, total pipeline), peak CPU, and memory usage for every document.

## Architecture

```
                     ┌─────────────────────┐
                     │   Streamlit UI (4 pages)
                     │  Upload · Search & Export
                     │  View Documents · Analytics
                     └──────┬──────────────┘
                            │
                     ┌──────▼──────────────┐
                     │   Document Pipeline  │
                     │                     │
                     │  File Upload        │
                     │  Type Detection     │
                     │  Text Extraction    │
                     │  Text Cleaning      │
                     │  Classification     │
                     │  AI Structuring     │
                     │  Database Storage   │
                     └──────┬──────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
       ┌──────▼─────┐ ┌────▼────┐ ┌──────▼──────┐
       │  Ollama LLM │ │ SQLite  │ │  File Store  │
       │ (or None)   │ │ (local) │ │  (uploads/)  │
       └────────────┘ └─────────┘ └─────────────┘
```

## Folder Structure

```
├── app.py                  # Streamlit entry point
├── config.py               # App configuration & constants
├── ingestion/              # File intake stage
│   ├── upload.py           # File upload & size validation
│   └── extractor.py        # Text extraction (PDF, images, audio, text)
├── processing/             # Core processing stage
│   ├── classifier.py       # Document type classification
│   ├── cleaner.py          # Text cleaning & normalization
│   ├── detector.py         # File type / MIME detection
│   └── processor.py        # Orchestrates LLM call for structuring
├── pipeline/               # Pipeline utilities
│   └── export.py           # JSON / CSV / JSONL / TXT export
├── llm/                    # LLM interface
│   ├── local_llm.py        # OllamaBackend + NoneBackend fallback
│   └── prompts.py          # Per-document-type extraction prompts
├── schemas/                # JSON schemas per document type
│   └── __init__.py
├── storage/                # Persistence layer
│   ├── database.py         # SQLite CRUD, search, analytics
│   └── models.py           # Document dataclass
├── utils/                  # Shared utilities
│   └── helpers.py          # Text stats, file size formatting
├── ui/                     # Streamlit UI
│   ├── pages/
│   │   ├── upload.py       # Upload & pipeline execution
│   │   ├── search.py       # Search & bulk export
│   │   ├── view.py         # Document detail viewer
│   │   └── analytics.py    # Analytics dashboard
│   └── components/
│       ├── sidebar.py      # Model status indicator
│       └── file_info.py    # File metadata component
├── data/                   # Runtime data (gitignored)
│   ├── uploads/            # Uploaded files
│   └── storage.db          # SQLite database
├── exports/                # Exported files (gitignored)
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites

- Python 3.10+
- Tesseract OCR (`pytesseract` — for image OCR support)
- Ollama (optional — for AI structuring; see [Running with Ollama](#running-with-ollama))

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd offline-ai-intelligence-hub

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Tesseract (Ubuntu/Debian)
sudo apt install tesseract-ocr
# On macOS: brew install tesseract
# On Windows: download from https://github.com/UB-Mannheim/tesseract/wiki
```

## Running Locally

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

When running without Ollama, the app falls back to a `NoneBackend` — documents are ingested, classified, and stored, but structured data extraction is skipped. All other features (search, export, analytics) remain fully functional.

## Running with Ollama

1. Install [Ollama](https://ollama.com) for your platform.
2. Pull a model (default is `llama3.2`):
   ```bash
   ollama pull llama3.2
   ```
3. Start the Ollama service:
   ```bash
   ollama serve
   ```
4. Launch the app:
   ```bash
   streamlit run app.py
   ```

The sidebar will show a green **Connected** indicator when Ollama is detected. All uploaded documents will be automatically structured into JSON based on their detected type.

### Changing the Model

Edit `config.py`:

```python
OLLAMA_MODEL = "llama3.2"  # Change to any model pulled via Ollama
```

## Screenshots

<!-- TODO: Add screenshots -->
<!-- Upload Page: pipeline stages, performance metrics -->
<!-- Search & Export: filtered results, bulk export controls -->
<!-- View Documents: file info, raw/cleaned/structured tabs, download buttons -->
<!-- Analytics Dashboard: metric cards, bar charts, recent uploads -->

## Technologies

| Component | Technology |
|-----------|-----------|
| Frontend  | Streamlit |
| Backend   | Python 3.10+ |
| Database  | SQLite (via `sqlite3`) |
| OCR       | Tesseract (`pytesseract`) |
| Audio     | Whisper (`faster-whisper`) |
| LLM       | Ollama (local, CPU-only) |
| PDF       | PyMuPDF (`fitz`) |
| Monitoring| `psutil` |

## Future Improvements

- Incremental processing (re-process only reprocessed documents)
- Batch upload (multiple files at once)
- File format conversion (markdown, HTML, etc.)
- Model auto-download on first run
- Multi-language OCR and transcription
- Document comparison / diff view
- Export with custom field selection
- Dark/light theme toggle
- User authentication for multi-user setups
- REST API for headless operation
