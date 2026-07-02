import streamlit as st

from pipeline.export import export, FORMATS
from storage.database import search_documents
from utils.helpers import truncate_text


def render() -> None:
    st.header("Search & Export")

    query = st.text_input("Search documents", placeholder="Type to search...")

    records = search_documents(query) if query else search_documents()

    if not records:
        st.info("No documents found.")
        return

    st.success(f"Found {len(records)} document(s).")

    for doc in records:
        with st.expander(f"{doc.filename}  —  {doc.created_at[:10]}"):
            st.text(f"Type: {doc.file_type}")
            st.text(truncate_text(doc.cleaned_text or doc.raw_text, 500))

    fmt = st.selectbox("Export format", list(FORMATS.keys()))
    if st.button("Export"):
        data = [r.__dict__ for r in records]
        output = export(data, fmt)
        st.download_button(
            label=f"Download as {fmt.upper()}",
            data=output,
            file_name=f"export.{fmt}",
            mime="text/plain",
        )
