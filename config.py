import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "storage.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_EXTENSIONS = {
    ".txt": "text",
    ".csv": "text",
    ".json": "text",
    ".xml": "text",
    ".md": "text",
    ".pdf": "document",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
    ".mp3": "audio",
    ".wav": "audio",
    ".flac": "audio",
}

CLEANING_PRESETS = {
    "minimal": {"strip_whitespace": True, "remove_empty_lines": True},
    "normal": {
        "strip_whitespace": True,
        "remove_empty_lines": True,
        "normalize_unicode": True,
        "normalize_quotes": True,
    },
    "aggressive": {
        "strip_whitespace": True,
        "remove_empty_lines": True,
        "normalize_unicode": True,
        "normalize_quotes": True,
        "remove_urls": True,
        "remove_emails": True,
        "collapse_whitespace": True,
    },
}

DEFAULT_CLEANING_PRESET = "normal"
MAX_UPLOAD_SIZE_MB = 50
APP_TITLE = "Offline AI Intelligence Hub"
APP_ICON = "🧠"

# LLM backend configuration
LLM_BACKEND = "ollama"
OLLAMA_MODEL = "llama3.2"
