from pathlib import Path

from processing.detector import detect_file_type


def extract_text(path: Path) -> str:
    file_type = detect_file_type(path)

    if file_type in ("text",):
        return path.read_text(encoding="utf-8", errors="replace")

    msg = f"Text extraction not implemented for type: {file_type}"
    raise NotImplementedError(msg)
