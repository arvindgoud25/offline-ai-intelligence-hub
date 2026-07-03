import time

import streamlit as st

from config import SUPPORTED_EXTENSIONS
from ingestion.extractor import extract_text
from ingestion.upload import save_uploaded_file, validate_file_size
from processing.classifier import classify_document, get_schema_for_type
from processing.cleaner import clean
from processing.detector import detect_file_type, is_supported
from llm.local_llm import get_backend_status
from processing.processor import process_text
from storage.database import insert_document
from storage.models import Document
from utils.helpers import compute_text_stats, format_file_size


def render() -> None:
    st.header("Upload Document")
    st.caption("Supported files: " + ", ".join(SUPPORTED_EXTENSIONS))

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=list(SUPPORTED_EXTENSIONS.keys()),
    )

    if not uploaded_file:
        st.info("Upload a file to begin processing.")
        return

    if not validate_file_size(uploaded_file):
        st.error("File exceeds the maximum upload size.")
        return

    path = save_uploaded_file(uploaded_file)

    if not is_supported(path):
        st.error(f"Unsupported file type: {path.suffix}")
        return

    start_time = time.perf_counter()

    with st.status("Processing...", expanded=True) as status:
        st.write("Saving uploaded file...")
        file_type = detect_file_type(path)
        file_size = len(uploaded_file.getbuffer())

        st.write("Extracting text...")
        try:
            raw_text = extract_text(path)
        except (NotImplementedError, ImportError, RuntimeError, ValueError) as exc:
            st.error(str(exc))
            return

        st.write("Cleaning text...")
        cleaned_text = clean(raw_text)

        st.write("Classifying document type...")
        doc_type, confidence = classify_document(cleaned_text)
        schema = get_schema_for_type(doc_type)

        st.write("Running AI model...")
        processing_status = "partial"
        try:
            structured = process_text(cleaned_text, doc_type=doc_type, schema=schema)
            if structured:
                processing_status = "complete"
        except Exception as exc:
            structured = {}
            processing_status = "failed"
            st.warning(f"AI structuring failed: {exc}")

        processing_time = time.perf_counter() - start_time

        st.write("Saving to database...")
        doc = Document(
            filename=uploaded_file.name,
            file_type=file_type,
            file_size=file_size,
            doc_type=doc_type,
            processing_status=processing_status,
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            structured_data=structured,
            processing_time=processing_time,
        )
        doc_id = insert_document(doc)

        status.update(label="Processing complete!", state="complete")

    st.success(f"Document saved with ID: {doc_id}")

    # ------------------------------------------------------------------
    # 1. Processing Pipeline
    # ------------------------------------------------------------------
    with st.container(border=True):
        st.markdown("**Processing Pipeline**")
        cols = st.columns(4)
        cols[0].markdown(":white_check_mark: File Uploaded")
        cols[1].markdown(":white_check_mark: Type Detected")
        cols[2].markdown(":white_check_mark: Text Extracted")
        if structured:
            cols[3].markdown(":white_check_mark: AI Structured")
        else:
            cols[3].markdown(":hourglass: Ready for AI Structuring")

    # ------------------------------------------------------------------
    # 2. Document Details
    # ------------------------------------------------------------------
    with st.container(border=True):
        st.markdown("**Document Details**")
        c1, c2, c3 = st.columns(3)
        c1.write(f":page_facing_up: {doc.filename}")
        c2.write(f":label: {file_type}")
        c3.write(f":floppy_disk: {format_file_size(file_size)}")
        c1.write(f":stopwatch: {processing_time:.2f}s")
        c2.write(f":white_check_mark: Status: Complete")
        c3.write(f":calendar: {doc.created_at[:10]}")

    # ------------------------------------------------------------------
    # 3. Document Classification
    # ------------------------------------------------------------------
    with st.container(border=True):
        st.markdown("**Document Classification**")
        st.info(f"**Detected type:** {doc_type}  _(confidence: {confidence:.0%})_")
        if schema:
            with st.expander("Selected JSON Schema"):
                st.json(schema)

    # ------------------------------------------------------------------
    # 4. Text Statistics
    # ------------------------------------------------------------------
    stats = compute_text_stats(cleaned_text)
    with st.container(border=True):
        st.markdown("**Text Statistics**")
        c1, c2, c3 = st.columns(3)
        c1.metric("Characters", f"{stats['characters']:,}")
        c2.metric("Words", f"{stats['words']:,}")
        c3.metric("Lines", f"{stats['lines']:,}")

    # ------------------------------------------------------------------
    # 5. Extracted Text (collapsible, copyable, formatting preserved)
    # ------------------------------------------------------------------
    with st.expander("Extracted Text", expanded=False):
        st.caption("Select all and copy (Ctrl+A, Ctrl+C)")
        st.text_area(
            label="Extracted content",
            value=cleaned_text,
            height=300,
            key="extracted_text_display",
        )

    # ------------------------------------------------------------------
    # 6. AI Structuring
    # ------------------------------------------------------------------
    with st.container(border=True):
        st.markdown("**AI Structuring**")
        backend_status = get_backend_status()
        c1, c2 = st.columns(2)
        if backend_status["available"] and backend_status["name"] != "None":
            model_label = backend_status["model"] or backend_status["name"]
            c1.success(f"Model: {model_label}")
            c2.metric("Status", "Connected")
        else:
            c1.warning("Model: Ollama not detected")
            c2.metric("Status", "Unavailable")
            st.info("Structured extraction unavailable. Local model not running.")
        if structured:
            with st.expander("Structured JSON Output", expanded=True):
                st.json(structured)
        else:
            st.info("No structured data extracted.")
