import streamlit as st

from config import APP_TITLE, APP_ICON


def render_sidebar() -> None:
    st.sidebar.markdown(f"# {APP_ICON} {APP_TITLE}")
    st.sidebar.markdown("---")
