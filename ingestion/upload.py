import shutil
from pathlib import Path

from config import MAX_UPLOAD_SIZE_MB, UPLOAD_DIR


def save_uploaded_file(uploaded_file) -> Path:
    dest = UPLOAD_DIR / uploaded_file.name
    with open(dest, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return dest


def validate_file_size(uploaded_file) -> bool:
    size_mb = len(uploaded_file.getbuffer()) / (1024 * 1024)
    return size_mb <= MAX_UPLOAD_SIZE_MB


def delete_file(path: Path) -> None:
    if path.exists():
        path.unlink()


def clear_uploads() -> None:
    shutil.rmtree(UPLOAD_DIR, ignore_errors=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
