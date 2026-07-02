import re
from typing import Any

from schemas import DOCUMENT_SCHEMAS

RESUME_KEYWORDS = [
    "resume", "cv", "curriculum vitae", "work experience", "employment history",
    "education", "skills", "professional summary", "objective", "references available",
    "proficient in", "work history",
]

INVOICE_KEYWORDS = [
    "invoice", "invoice number", "invoice date", "amount due", "bill to",
    "payment terms", "subtotal", "total due", "tax", "customer id",
    "purchase order", "due date", "statement",
]

MEDICAL_KEYWORDS = [
    "patient", "diagnosis", "symptoms", "prescription", "medical report",
    "clinical findings", "physician", "treatment", "dosage", "medication",
    "laboratory", "specimen", "radiology", "history of present illness",
]

MEETING_KEYWORDS = [
    "agenda", "meeting minutes", "attendees", "discussion", "action items",
    "meeting called", "next steps", "follow-up", "decisions made",
    "meeting notes", "minutes of meeting",
]

RESEARCH_KEYWORDS = [
    "abstract", "introduction", "methodology", "conclusion", "references",
    "research paper", "experiment", "hypothesis", "literature review",
    "results", "discussion", "proposed method", "related work",
]

_DOC_TYPE_KEYWORDS: dict[str, list[str]] = {
    "Resume": RESUME_KEYWORDS,
    "Invoice": INVOICE_KEYWORDS,
    "Medical Report": MEDICAL_KEYWORDS,
    "Meeting Notes": MEETING_KEYWORDS,
    "Research Paper": RESEARCH_KEYWORDS,
}


def classify_document(text: str) -> tuple[str, float]:
    text_lower = text.lower()
    scores: dict[str, float] = {}
    for doc_type, keywords in _DOC_TYPE_KEYWORDS.items():
        matches = sum(1 for kw in keywords if re.search(rf"\b{re.escape(kw)}\b", text_lower))
        if matches:
            scores[doc_type] = matches / len(keywords)
    if not scores:
        return ("General", 0.0)
    best = max(scores, key=scores.get)
    return (best, scores[best])


def get_schema_for_type(doc_type: str) -> dict[str, Any] | None:
    return DOCUMENT_SCHEMAS.get(doc_type)
