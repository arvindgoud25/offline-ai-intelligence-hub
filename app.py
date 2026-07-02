import streamlit as st

from config import APP_TITLE, APP_ICON
from storage.database import init_db
from ui.components.sidebar import render_sidebar

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
)

init_db()
render_sidebar()

pages = {
    "Upload": "ui.pages.upload",
    "Search & Export": "ui.pages.search",
    "View Documents": "ui.pages.view",
}

choice = st.sidebar.radio("Navigation", list(pages.keys()))

module_path = pages[choice]
module = __import__(module_path, fromlist=["render"])
module.render()
