from pathlib import Path

from config import SUPPORTED_EXTENSIONS


def detect_file_type(path: Path) -> str:
    ext = path.suffix.lower()
    return SUPPORTED_EXTENSIONS.get(ext, "unknown")


def is_supported(path: Path) -> bool:
    return detect_file_type(path) != "unknown"
