import streamlit as st

from storage.models import Document
from utils.helpers import format_file_size


def _status_emoji(status: str) -> str:
    return {"complete": ":green[Complete]", "partial": ":orange[Partial]", "failed": ":red[Failed]"}.get(status, status)


def render_file_info(doc: Document) -> None:
    c1, c2, c3 = st.columns(3)
    c1.metric("File", doc.filename)
    c2.metric("Type", doc.file_type)
    c3.metric("Size", format_file_size(doc.file_size))
    c1.markdown(f"**Detected:** {doc.doc_type or 'N/A'}")
    c2.markdown(f"**Status:** {_status_emoji(doc.processing_status)}")
    c3.markdown(f"**Time:** {doc.processing_time:.2f}s")
