import time

import psutil
import streamlit as st

from config import SUPPORTED_EXTENSIONS
from i18n.translator import tr
from ingestion.extractor import extract_text
from ingestion.upload import save_uploaded_file, validate_file_size
from llm.local_llm import get_backend_status
from processing.classifier import classify_document, get_schema_for_type
from processing.cleaner import clean
from processing.detector import detect_file_type, is_supported
from processing.processor import process_text
from storage.database import insert_document
from storage.models import Document
from utils.helpers import compute_text_stats, format_file_size


def render() -> None:
    st.header(tr("upload_document"))
    st.caption(f"{tr('supported_files')}: " + ", ".join(SUPPORTED_EXTENSIONS))

    uploaded_file = st.file_uploader(
        tr("choose_file"),
        type=list(SUPPORTED_EXTENSIONS.keys()),
    )

    if not uploaded_file:
        st.info(tr("upload_to_begin"))
        return

    if not validate_file_size(uploaded_file):
        st.error(tr("file_too_large"))
        return

    path = save_uploaded_file(uploaded_file)

    if not is_supported(path):
        st.error(f"{tr('unsupported_file')}: {path.suffix}")
        return

    pipeline_start = time.perf_counter()
    mem_start = psutil.Process().memory_info().rss

    with st.status(tr("processing"), expanded=True) as status:
        st.write(tr("saving_uploaded_file"))
        file_type = detect_file_type(path)
        file_size = len(uploaded_file.getbuffer())

        st.write(tr("extracting_text"))
        t0 = time.perf_counter()
        try:
            raw_text = extract_text(path)
        except (NotImplementedError, ImportError, RuntimeError, ValueError) as exc:
            st.error(str(exc))
            return
        extract_time = time.perf_counter() - t0

        st.write(tr("cleaning_text"))
        cleaned_text = clean(raw_text)

        st.write(tr("classifying_document"))
        doc_type, confidence = classify_document(cleaned_text)
        schema = get_schema_for_type(doc_type)

        st.write(tr("running_ai"))
        processing_status = "partial"
        llm_time = 0.0
        t1 = time.perf_counter()
        try:
            structured = process_text(cleaned_text, doc_type=doc_type, schema=schema)
            if structured:
                processing_status = "complete"
        except Exception as exc:
            structured = {}
            processing_status = "failed"
            st.warning(f"AI structuring failed: {exc}")
        llm_time = time.perf_counter() - t1

        total_time = time.perf_counter() - pipeline_start
        cpu_peak = psutil.cpu_percent(interval=None)
        mem_used = psutil.Process().memory_info().rss - mem_start

        ocr_time = extract_time if file_type in ("image", "document") else 0.0

        perf = {
            "extract_time": round(extract_time, 3),
            "llm_time": round(llm_time, 3),
            "ocr_time": round(ocr_time, 3),
            "total_time": round(total_time, 3),
            "peak_cpu": cpu_peak,
            "peak_memory_bytes": mem_used,
        }

        st.write(tr("saving_database"))
        doc = Document(
            filename=uploaded_file.name,
            file_type=file_type,
            file_size=file_size,
            doc_type=doc_type,
            processing_status=processing_status,
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            structured_data=structured,
            processing_time=total_time,
            performance_metrics=perf,
        )
        doc_id = insert_document(doc)

        status.update(
            label=tr("processing_complete"),
            state="complete",
        )

    st.success(f"{tr('document_saved')}: {doc_id}")

    # ------------------------------------------------------------------
    # 1. Processing Pipeline
    # ------------------------------------------------------------------
    with st.container(border=True):
        st.markdown("**Processing Pipeline**")
        cols = st.columns(4)
        cols[0].markdown(f":white_check_mark: {tr('file_uploaded_step')}")
        cols[1].markdown(f":white_check_mark: {tr('type_detected_step')}")
        cols[2].markdown(f":white_check_mark: {tr('text_extracted_step')}")
        if structured:
            cols[3].markdown(f":white_check_mark: {tr('ai_structured_step')}")
        else:
            cols[3].markdown(f":hourglass: {tr('ready_for_ai_structuring_step')}")

    # ------------------------------------------------------------------
    # 2. Document Details
    # ------------------------------------------------------------------
    with st.container(border=True):
        st.markdown(f"**{tr('document_details')}**")
        c1, c2, c3 = st.columns(3)
        c1.write(f":page_facing_up: {doc.filename}")
        c2.write(f":label: {file_type}")
        c3.write(f":floppy_disk: {format_file_size(file_size)}")
        c1.write(f":stopwatch: {total_time:.2f}s")
        c2.write(":white_check_mark: Status: Complete")
        c3.write(f":calendar: {doc.created_at[:10]}")

    # ------------------------------------------------------------------
    # 3. Document Classification
    # ------------------------------------------------------------------
    with st.container(border=True):
        st.markdown(f"**{tr('document_classification')}**")
        st.info(f"**Detected type:** {doc_type}  _(confidence: {confidence:.0%})_")
        if schema:
            with st.expander(tr("selected_json_schema")):
                st.json(schema)

    # ------------------------------------------------------------------
    # 4. Text Statistics
    # ------------------------------------------------------------------
    stats = compute_text_stats(cleaned_text)
    with st.container(border=True):
        st.markdown(f"**{tr('text_statistics')}**")
        c1, c2, c3 = st.columns(3)
        c1.metric(tr("characters"), f"{stats['characters']:,}")
        c2.metric(tr("words"), f"{stats['words']:,}")
        c3.metric(tr("lines"), f"{stats['lines']:,}")

    # ------------------------------------------------------------------
    # 5. Extracted Text (collapsible, copyable, formatting preserved)
    # ------------------------------------------------------------------
    with st.expander(tr("extracted_text"), expanded=False):
        st.caption(tr("select_all_copy"))
        st.text_area(
            label=tr("extracted_content"),
            value=cleaned_text,
            height=300,
            key="extracted_text_display",
        )

    # ------------------------------------------------------------------
    # 6. AI Structuring
    # ------------------------------------------------------------------
    with st.container(border=True):
        st.markdown(f"**{tr('ai_structuring')}**")
        backend_status = get_backend_status()
        c1, c2 = st.columns(2)
        if backend_status["available"] and backend_status["name"] != "None":
            model_label = backend_status["model"] or backend_status["name"]
            c1.success(f"{tr('model_label')}: {model_label}")
            c2.metric(tr("status"), tr("connected"))
        else:
            c1.warning(tr("model_not_detected"))
            c2.metric(tr("status"), tr("unavailable"))
            st.info(tr("ai_unavailable_info"))
        if structured:
            with st.expander(tr("structured_json_output"), expanded=True):
                st.json(structured)
        else:
            st.info(tr("no_structured_data"))

    # ------------------------------------------------------------------
    # 7. Performance Metrics
    # ------------------------------------------------------------------
    with st.container(border=True):
        st.markdown(f"**{tr('performance_metrics')}**")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(tr("extraction_time"), f"{perf['extract_time']:.2f}s")
        c2.metric(tr("llm_inference_time"), f"{perf['llm_time']:.2f}s")
        c3.metric(tr("total_pipeline_time"), f"{perf['total_time']:.2f}s")
        c4.metric(tr("peak_cpu"), f"{perf['peak_cpu']:.0f}%")
        if perf["peak_memory_bytes"]:
            st.caption(f"{tr('memory_delta')}: {format_file_size(perf['peak_memory_bytes'])}")
