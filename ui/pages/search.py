import json
from typing import Any

import streamlit as st

from pipeline.export import FORMATS, export
from storage.database import get_all_documents, search_documents_filtered
from utils.helpers import format_file_size


def _doc_to_dict(doc: Any) -> dict:
    d = doc.__dict__.copy()
    if isinstance(d.get("structured_data"), dict):
        d["structured_data"] = json.dumps(d["structured_data"])
    return d


def _render_export_ui(records: list, scope_label: str) -> None:
    if not records:
        return
    fmt = st.selectbox(
        f"Export format ({scope_label})", list(FORMATS.keys()), key=f"fmt_{scope_label}"
    )
    if st.button(f"Export {scope_label}", key=f"btn_{scope_label}"):
        data = [_doc_to_dict(r) for r in records]
        output = export(data, fmt)
        st.download_button(
            label=f"Download as {fmt.upper()}",
            data=output,
            file_name=f"{scope_label.lower().replace(' ', '_')}.{fmt}",
            mime="text/plain",
        )


def render() -> None:
    st.header("Search & Export")

    c1, c2, c3 = st.columns([2, 1, 1])
    query = c1.text_input(
        "Search",
        placeholder="Search by filename, text, or content...",
        label_visibility="collapsed",
    )
    doc_type_filter = c2.selectbox(
        "Document Type",
        [
            "",
            "Resume",
            "Invoice",
            "Medical Report",
            "Meeting Notes",
            "Research Paper",
            "General",
        ],
        label_visibility="collapsed",
    )
    status_filter = c3.selectbox(
        "Status",
        ["", "complete", "partial", "failed"],
        label_visibility="collapsed",
    )

    records = search_documents_filtered(
        query=query,
        doc_type_filter=doc_type_filter,
        file_type_filter="",
        status_filter=status_filter,
    )

    if not records:
        st.info("No matching documents found.")
        return

    st.success(f"Found {len(records)} document(s).")

    for doc in records:
        with st.container(border=True):
            meta_cols = st.columns([2, 1, 1, 1])
            meta_cols[0].markdown(f"**{doc.filename}**")
            meta_cols[1].markdown(f":label: {doc.doc_type or 'N/A'}")
            status_emoji = {
                "complete": ":green[Complete]",
                "partial": ":orange[Partial]",
                "failed": ":red[Failed]",
            }
            meta_cols[2].markdown(
                status_emoji.get(doc.processing_status, doc.processing_status)
            )
            meta_cols[3].markdown(f":calendar: {doc.created_at[:10]}")

            with st.expander("View details"):
                detail_tabs = st.tabs(["Extracted Text", "Structured JSON", "Metadata"])

                with detail_tabs[0]:
                    st.text(doc.cleaned_text or doc.raw_text or "(empty)")

                with detail_tabs[1]:
                    st.json(doc.structured_data if doc.structured_data else {})

                with detail_tabs[2]:
                    st.markdown(
                        f"""
- **Filename:** {doc.filename}
- **File type:** {doc.file_type}
- **File size:** {format_file_size(doc.file_size)}
- **Document type:** {doc.doc_type or "N/A"}
- **Processing status:** {doc.processing_status or "N/A"}
- **Processing time:** {doc.processing_time:.2f}s
- **Created:** {doc.created_at}
"""
                    )

    st.markdown("---")
    _render_export_ui(records, "Search Results")
    all_docs = get_all_documents()
    _render_export_ui(all_docs, "All Documents")
