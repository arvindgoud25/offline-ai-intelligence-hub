import streamlit as st

THEMES = {
    "System": "system",
    "Light": "light",
    "Dark": "dark",
}


def init_theme():
    if "theme" not in st.session_state:
        st.session_state.theme = "system"


def set_theme(theme):
    st.session_state.theme = theme


def get_theme():
    return st.session_state.theme
