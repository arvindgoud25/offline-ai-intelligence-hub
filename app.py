import streamlit as st

from config import APP_ICON, APP_TITLE, LLM_BACKEND, OLLAMA_MODEL
from i18n.translator import init_language, tr
from llm.local_llm import load_model
from storage.database import init_db
from ui.components.sidebar import render_sidebar

init_language()

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
)

init_db()
load_model(LLM_BACKEND, OLLAMA_MODEL)
render_sidebar()

pages = {
    tr("upload"): "ui.pages.upload",
    tr("search_export"): "ui.pages.search",
    tr("view_documents"): "ui.pages.view",
    tr("analytics"): "ui.pages.analytics",
}

choice = st.sidebar.radio(
    tr("navigation"),
    list(pages.keys()),
)

module_path = pages[choice]
module = __import__(module_path, fromlist=["render"])
module.render()
