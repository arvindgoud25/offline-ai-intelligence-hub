from typing import Any

from llm.local_llm import get_backend_status, is_ready, generate_structured_json


def process_text(text: str, doc_type: str = "", schema: dict[str, Any] | None = None) -> dict[str, Any]:
    if is_ready():
        return generate_structured_json(text, doc_type, schema)
    return {}
