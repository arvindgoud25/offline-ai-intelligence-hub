import streamlit as st

from i18n.translator import tr
from storage.database import get_analytics


def render() -> None:
    st.header(tr("analytics_dashboard"))

    data = get_analytics()

    if data["total_documents"] == 0:
        st.info(tr("no_documents_analytics"))
        return

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(tr("total_documents"), data["total_documents"])
    col2.metric(tr("avg_processing_time"), f"{data['avg_processing_time']:.2f}s")
    col3.metric(tr("avg_extraction_time"), f"{data['avg_extraction_time']:.3f}s")
    col4.metric(tr("total_characters"), f"{data['total_characters']:,}")
    col5.metric(tr("success_rate"), f"{data['success_rate']}%")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        if data["documents_by_type"]:
            st.markdown(f"**{tr('documents_by_type')}**")
            st.bar_chart(data["documents_by_type"], horizontal=True)

    with col_b:
        if data["documents_by_file_type"]:
            st.markdown(f"**{tr('documents_by_file_format')}**")
            st.bar_chart(data["documents_by_file_type"], horizontal=True)

    col_c, col_d = st.columns(2)

    with col_c:
        complete = data["documents_by_status"].get("complete", 0)
        incomplete = data["total_documents"] - complete
        st.markdown(f"**{tr('success_vs_failed')}**")
        st.bar_chart({tr("complete"): complete, tr("incomplete"): incomplete}, horizontal=True)

    with col_d:
        st.markdown(f"**{tr('most_common_doc_type')}**")
        st.metric("", data["most_common_doc_type"])

    st.markdown("---")

    if data["recent_uploads"]:
        st.markdown(f"**{tr('recent_uploads')}**")
        for item in data["recent_uploads"]:
            st.markdown(
                f"- {item['filename']}  —  *{item['doc_type'] or tr('na')}*  ({item['created_at'][:10]})"
            )
