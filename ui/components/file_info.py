import streamlit as st

from storage.models import Document
from utils.helpers import format_file_size


def render_file_info(doc: Document) -> None:
    col1, col2, col3 = st.columns(3)
    col1.metric("File", doc.filename)
    col2.metric("Type", doc.file_type)
    col3.metric("Size", format_file_size(doc.file_size))
