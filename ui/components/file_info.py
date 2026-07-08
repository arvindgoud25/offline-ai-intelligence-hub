import streamlit as st

from i18n.translator import tr
from storage.models import Document
from utils.helpers import format_file_size


def _status_emoji(status: str) -> str:
    return {
        "complete": f":green[{tr('complete')}]",
        "partial": f":orange[{tr('partial')}]",
        "failed": f":red[{tr('failed')}]",
    }.get(status, status)


def render_file_info(doc: Document) -> None:
    c1, c2, c3 = st.columns(3)
    c1.metric(tr("file_metric"), doc.filename)
    c2.metric(tr("type_metric"), doc.file_type)
    c3.metric(tr("size_metric"), format_file_size(doc.file_size))
    c1.markdown(f"**{tr('detected_label')}** {doc.doc_type or tr('na')}")
    c2.markdown(f"**{tr('status_label')}** {_status_emoji(doc.processing_status)}")
    c3.markdown(f"**{tr('time_label')}** {doc.processing_time:.2f}s")
