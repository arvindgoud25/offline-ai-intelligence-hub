import csv
import json
from io import StringIO
from typing import Any


def to_json(records: list[dict], indent: int = 2) -> str:
    return json.dumps(records, indent=indent, ensure_ascii=False, default=str)


def to_csv(records: list[dict]) -> str:
    if not records:
        return ""

    fieldnames = list(dict.fromkeys(k for r in records for k in r))
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue()


def to_jsonl(records: list[dict]) -> str:
    lines = [json.dumps(r, ensure_ascii=False, default=str) for r in records]
    return "\n".join(lines)


def to_txt(records: list[dict]) -> str:
    parts: list[str] = []
    for r in records:
        text = r.get("cleaned_text") or r.get("raw_text") or ""
        parts.append(f"--- {r.get('filename', 'unknown')} ---\n{text}\n")
    return "\n".join(parts)


FORMATS = {
    "json": to_json,
    "csv": to_csv,
    "jsonl": to_jsonl,
    "txt": to_txt,
}


def export(records: list[dict], fmt: str = "json") -> str:
    fn = FORMATS.get(fmt)
    if fn is None:
        msg = f"Unsupported export format: {fmt}"
        raise ValueError(msg)
    return fn(records)
