import streamlit as st

from i18n.translations import TRANSLATIONS

DEFAULT_LANGUAGE = "en"

LANGUAGES = {
    "en": "English",
    "hi": "हिन्दी",
    "te": "తెలుగు",
}


def init_language():
    if "language" not in st.session_state:
        st.session_state.language = DEFAULT_LANGUAGE


def get_language():
    init_language()
    return st.session_state.language


def set_language(language: str):
    if language in LANGUAGES:
        st.session_state.language = language


def tr(key: str) -> str:
    language = get_language()
    return TRANSLATIONS.get(language, TRANSLATIONS[DEFAULT_LANGUAGE]).get(key, key)
