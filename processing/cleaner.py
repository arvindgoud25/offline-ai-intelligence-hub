import re
import unicodedata

from config import CLEANING_PRESETS, DEFAULT_CLEANING_PRESET


def clean(text: str, preset: str | None = None) -> str:
    if preset is None:
        preset = DEFAULT_CLEANING_PRESET

    steps = CLEANING_PRESETS[preset]

    if steps.get("strip_whitespace"):
        text = text.strip()

    if steps.get("remove_empty_lines"):
        lines = [l for l in text.splitlines() if l.strip()]
        text = "\n".join(lines)

    if steps.get("normalize_unicode"):
        text = unicodedata.normalize("NFKC", text)

    if steps.get("normalize_quotes"):
        text = text.replace("\u201c", '"').replace("\u201d", '"')
        text = text.replace("\u2018", "'").replace("\u2019", "'")

    if steps.get("remove_urls"):
        text = re.sub(r"https?://\S+", "", text)

    if steps.get("remove_emails"):
        text = re.sub(r"\S+@\S+", "", text)

    if steps.get("collapse_whitespace"):
        text = re.sub(r" +", " ", text)

    return text.strip()
