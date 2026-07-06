from pathlib import Path

from processing.detector import detect_file_type


def extract_text_from_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def extract_text_from_pdf(path: Path) -> str:
    try:
        import fitz
    except ImportError:
        raise ImportError(
            "PyMuPDF is required for PDF extraction. "
            "Install it with: pip install PyMuPDF"
        )
    try:
        parts = []
        with fitz.open(path) as doc:
            for page in doc:
                text = page.get_text()
                if text.strip():
                    parts.append(text)
        return "\n".join(parts).strip()
    except Exception as exc:
        raise ValueError(f"Failed to extract text from PDF: {exc}")


def extract_text_from_image(path: Path) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        raise ImportError(
            "Pillow and pytesseract are required for image OCR. "
            "Install them with: pip install Pillow pytesseract"
        )
    try:
        return pytesseract.image_to_string(Image.open(path)).strip()
    except pytesseract.TesseractNotFoundError:
        raise RuntimeError(
            "Tesseract OCR engine is not installed on this system.\n"
            "Install it with your system package manager, e.g.:\n"
            "  Ubuntu/Debian: sudo apt install tesseract-ocr\n"
            "  macOS: brew install tesseract\n"
            "  Windows: https://github.com/UB-Mannheim/tesseract/wiki"
        )
    except Exception as exc:
        raise ValueError(f"Failed to extract text from image: {exc}")


_model = None


def extract_text_from_audio(path: Path) -> str:
    global _model
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ImportError(
            "faster-whisper is required for audio transcription. "
            "Install it with: pip install faster-whisper"
        )
    try:
        if _model is None:
            _model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = _model.transcribe(str(path))
        return " ".join(seg.text for seg in segments).strip()
    except Exception as exc:
        raise ValueError(f"Failed to transcribe audio: {exc}")


TEXT_EXTENSIONS = {".txt", ".csv", ".json", ".xml", ".md"}
PDF_EXTENSIONS = {".pdf"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac"}

_EXTRACTORS = {
    **{ext: extract_text_from_txt for ext in TEXT_EXTENSIONS},
    **{ext: extract_text_from_pdf for ext in PDF_EXTENSIONS},
    **{ext: extract_text_from_image for ext in IMAGE_EXTENSIONS},
    **{ext: extract_text_from_audio for ext in AUDIO_EXTENSIONS},
}


def extract_text(path: Path) -> str:
    ext = path.suffix.lower()
    extractor = _EXTRACTORS.get(ext)
    if extractor is None:
        file_type = detect_file_type(path)
        raise NotImplementedError(
            f"Text extraction not implemented for type: {file_type}"
        )
    if not path.exists() or path.stat().st_size == 0:
        raise ValueError(f"File is missing or empty: {path.name}")
    return extractor(path)
