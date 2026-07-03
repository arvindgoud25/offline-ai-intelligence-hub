import json

import streamlit as st

from pipeline.export import export
from storage.database import get_document, delete_document, search_documents_filtered
from ui.components.file_info import render_file_info


def render() -> None:
    st.header("Document Details")

    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    query = c1.text_input("Search", placeholder="Filename, type, or text...", label_visibility="collapsed")
    doc_type_filter = c2.selectbox(
        "Type", ["", "Resume", "Invoice", "Medical Report", "Meeting Notes", "Research Paper", "General"],
        label_visibility="collapsed",
    )
    status_filter = c3.selectbox(
        "Status", ["", "complete", "partial", "failed"],
        label_visibility="collapsed",
    )
    date_filter = c4.text_input("Date", placeholder="YYYY-MM-DD", label_visibility="collapsed")

    records = search_documents_filtered(
        query=query,
        doc_type_filter=doc_type_filter,
        status_filter=status_filter,
        date_filter=date_filter,
        limit=200,
    )

    if not records:
        st.info("No documents found matching your filters.")
        return

    options = {f"{r.id} — {r.filename} ({r.created_at[:10]})": r.id for r in records}
    selected_label = st.selectbox("Select a document", list(options.keys()))
    doc_id = options[selected_label]

    doc = get_document(doc_id)
    if not doc:
        st.error("Document not found.")
        return

    render_file_info(doc)

    tab1, tab2, tab3 = st.tabs(["Raw Text", "Cleaned Text", "Structured Data"])

    with tab1:
        st.text(doc.raw_text[:5000] if doc.raw_text else "(empty)")

    with tab2:
        st.text(doc.cleaned_text[:5000] if doc.cleaned_text else "(empty)")

    with tab3:
        st.json(doc.structured_data if doc.structured_data else {})

    doc_dict = doc.__dict__.copy()
    if isinstance(doc_dict.get("structured_data"), dict):
        doc_dict["structured_data"] = json.dumps(doc_dict["structured_data"])

    col_a, col_b, col_c, _ = st.columns([1, 1, 1, 2])

    with col_a:
        json_output = export([doc_dict], "json")
        st.download_button(
            "Download JSON",
            data=json_output,
            file_name=f"{doc.filename}.json",
            mime="application/json",
        )

    with col_b:
        txt_output = export([doc_dict], "txt")
        st.download_button(
            "Download TXT",
            data=txt_output,
            file_name=f"{doc.filename}.txt",
            mime="text/plain",
        )

    with col_c:
        metadata = {
            "filename": doc.filename,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "doc_type": doc.doc_type,
            "processing_status": doc.processing_status,
            "processing_time": doc.processing_time,
            "created_at": doc.created_at,
        }
        st.download_button(
            "Download Metadata",
            data=json.dumps(metadata, indent=2),
            file_name=f"{doc.filename}_metadata.json",
            mime="application/json",
        )

    if st.button("Delete Document", type="primary"):
        delete_document(doc_id)
        st.rerun()
