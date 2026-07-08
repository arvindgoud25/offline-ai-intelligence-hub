import json

import streamlit as st

from config import THEME_FILE

THEMES = {
    "system": "system",
    "light": "light",
    "dark": "dark",
}


def _load_theme() -> str:
    try:
        if THEME_FILE.exists():
            data = json.loads(THEME_FILE.read_text(encoding="utf-8"))
            theme = data.get("theme", "system")
            if theme in THEMES:
                return theme
    except (json.JSONDecodeError, OSError):
        pass
    return "system"


def _save_theme(theme: str) -> None:
    try:
        THEME_FILE.parent.mkdir(parents=True, exist_ok=True)
        THEME_FILE.write_text(
            json.dumps({"theme": theme}), encoding="utf-8"
        )
    except OSError:
        pass


def init_theme():
    if "theme" not in st.session_state:
        st.session_state.theme = _load_theme()


def set_theme(theme):
    st.session_state.theme = theme
    _save_theme(theme)


def get_theme():
    return st.session_state.theme
