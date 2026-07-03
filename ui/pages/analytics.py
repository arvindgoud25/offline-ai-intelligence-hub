import streamlit as st

from storage.database import get_analytics
from utils.helpers import format_file_size


def render() -> None:
    st.header("Analytics Dashboard")

    data = get_analytics()

    if data["total_documents"] == 0:
        st.info("No documents in the database. Upload some documents to see analytics.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Documents", data["total_documents"])
    col2.metric("Avg Processing Time", f'{data["avg_processing_time"]:.2f}s')
    col3.metric("Total Characters", f'{data["total_characters"]:,}')
    col4.metric("Success Rate", f'{data["success_rate"]}%')

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        if data["documents_by_type"]:
            st.markdown("**Documents by Type**")
            st.bar_chart(data["documents_by_type"], horizontal=True)

    with col_b:
        if data["documents_by_file_type"]:
            st.markdown("**Documents by File Format**")
            st.bar_chart(data["documents_by_file_type"], horizontal=True)

    if data["documents_by_status"]:
        st.markdown("**Processing Status Breakdown**")
        st.bar_chart(data["documents_by_status"], horizontal=True)

    st.markdown("---")

    if data["recent_uploads"]:
        st.markdown("**Recent Uploads**")
        for item in data["recent_uploads"]:
            st.markdown(f"- {item['filename']}  —  *{item['doc_type'] or 'N/A'}*  ({item['created_at'][:10]})")
