from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Document:
    id: int | None = None
    filename: str = ""
    file_type: str = ""
    file_size: int = 0
    doc_type: str = ""
    processing_status: str = ""
    raw_text: str = ""
    cleaned_text: str = ""
    structured_data: dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
