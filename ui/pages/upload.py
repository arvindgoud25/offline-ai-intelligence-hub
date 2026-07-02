import streamlit as st

from config import SUPPORTED_EXTENSIONS
from processing.detector import detect_file_type, is_supported
from ingestion.upload import save_uploaded_file, validate_file_size
from ingestion.extractor import extract_text
from processing.cleaner import clean
from processing.processor import process_text
from storage.database import insert_document
from storage.models import Document


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

    with st.status("Processing...", expanded=True) as status:
        st.write("Detecting file type...")
        file_type = detect_file_type(path)

        st.write("Extracting text...")
        try:
            raw_text = extract_text(path)
        except NotImplementedError:
            st.error("Text extraction is not yet implemented for this file type.")
            return
        except ImportError as exc:
            st.error(str(exc))
            return
        except RuntimeError as exc:
            st.error(str(exc))
            return
        except ValueError as exc:
            st.error(str(exc))
            return

        st.write("Cleaning text...")
        cleaned_text = clean(raw_text)

        st.write("Running AI model...")
        try:
            structured = process_text(cleaned_text)
        except NotImplementedError:
            structured = {}
            st.warning("AI processing is not yet implemented. Staged as placeholder.")

        st.write("Saving to database...")
        doc = Document(
            filename=uploaded_file.name,
            file_type=file_type,
            file_size=len(uploaded_file.getbuffer()),
            raw_text=raw_text,
            cleaned_text=cleaned_text,
            structured_data=structured,
        )
        doc_id = insert_document(doc)

        status.update(label="Complete!", state="complete")

    st.success(f"Document saved with ID: {doc_id}")

    with st.expander("View extracted text"):
        st.text(cleaned_text[:2000] + ("..." if len(cleaned_text) > 2000 else ""))
