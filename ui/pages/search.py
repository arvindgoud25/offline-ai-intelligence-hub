import json
from typing import Any

import streamlit as st

from i18n.translator import tr
from pipeline.export import FORMATS, export
from storage.database import get_all_documents, search_documents_filtered
from utils.helpers import format_file_size


def _doc_to_dict(doc: Any) -> dict:
    d = doc.__dict__.copy()
    if isinstance(d.get("structured_data"), dict):
        d["structured_data"] = json.dumps(d["structured_data"])
    return d


def _render_export_ui(records: list, scope_label: str, scope_key: str) -> None:
    if not records:
        return
    fmt = st.selectbox(
        tr("export_format").format(scope=scope_label),
        list(FORMATS.keys()),
        key=f"fmt_{scope_key}",
    )
    if st.button(tr("export_button").format(scope=scope_label), key=f"btn_{scope_key}"):
        data = [_doc_to_dict(r) for r in records]
        output = export(data, fmt)
        st.download_button(
            label=tr("download_as").format(fmt=fmt.upper()),
            data=output,
            file_name=f"{scope_key}.{fmt}",
            mime="text/plain",
        )


def render() -> None:
    st.header(tr("search_export"))

    c1, c2, c3 = st.columns([2, 1, 1])
    query = c1.text_input(
        tr("search"),
        placeholder=tr("search_placeholder"),
        label_visibility="collapsed",
    )
    doc_type_filter = c2.selectbox(
        tr("document_type_filter"),
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
        tr("status_filter"),
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
        st.info(tr("no_matching_documents"))
        return

    st.success(tr("found_documents").format(count=len(records)))

    for doc in records:
        with st.container(border=True):
            meta_cols = st.columns([2, 1, 1, 1])
            meta_cols[0].markdown(f"**{doc.filename}**")
            meta_cols[1].markdown(f":label: {doc.doc_type or tr('na')}")
            status_emoji = {
                "complete": f":green[{tr('complete')}]",
                "partial": f":orange[{tr('partial')}]",
                "failed": f":red[{tr('failed')}]",
            }
            meta_cols[2].markdown(
                status_emoji.get(doc.processing_status, doc.processing_status)
            )
            meta_cols[3].markdown(f":calendar: {doc.created_at[:10]}")

            with st.expander(tr("view_details")):
                detail_tabs = st.tabs(
                    [tr("extracted_text_tab"), tr("structured_json_tab"), tr("metadata_tab")]
                )

                with detail_tabs[0]:
                    st.text(doc.cleaned_text or doc.raw_text or tr("empty_text"))

                with detail_tabs[1]:
                    st.json(doc.structured_data if doc.structured_data else {})

                with detail_tabs[2]:
                    st.markdown(
                        f"""
- **{tr('filename_label')}** {doc.filename}
- **{tr('file_type_label')}** {doc.file_type}
- **{tr('file_size_label')}** {format_file_size(doc.file_size)}
- **{tr('document_type_label')}** {doc.doc_type or tr("na")}
- **{tr('processing_status_label')}** {doc.processing_status or tr("na")}
- **{tr('processing_time_label')}** {doc.processing_time:.2f}s
- **{tr('created_label')}** {doc.created_at}
"""
                    )

    st.markdown("---")
    _render_export_ui(records, tr("search_results"), "search_results")
    all_docs = get_all_documents()
    _render_export_ui(all_docs, tr("all_documents"), "all_documents")
