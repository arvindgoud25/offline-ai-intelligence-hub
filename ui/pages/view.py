import streamlit as st

from storage.database import search_documents, get_document, delete_document
from ui.components.file_info import render_file_info


def render() -> None:
    st.header("Document Details")

    records = search_documents(limit=100)
    if not records:
        st.info("No documents in the database.")
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

    if st.button("Delete Document", type="primary"):
        delete_document(doc_id)
        st.rerun()
