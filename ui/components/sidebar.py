import streamlit as st

from config import APP_ICON, APP_TITLE, LLM_BACKEND
from i18n.translator import (
    LANGUAGES,
    get_language,
    init_language,
    set_language,
    tr,
)
from llm.local_llm import get_backend_status
from ui.theme import get_theme, init_theme, set_theme


def render_sidebar() -> None:
    # Initialize language and theme
    init_language()
    init_theme()

    st.sidebar.markdown(f"# {APP_ICON} {APP_TITLE}")

    # -----------------------------
    # Language Selector
    # -----------------------------
    selected = st.sidebar.selectbox(
        tr("language"),
        options=list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(get_language()),
        format_func=lambda code: LANGUAGES[code],
    )
    set_language(selected)

    st.sidebar.markdown("---")

    # -----------------------------
    # Theme Selector
    # -----------------------------
    theme_options = ["system", "light", "dark"]

    selected_theme = st.sidebar.selectbox(
        tr("theme"),
        options=theme_options,
        index=theme_options.index(get_theme()),
        format_func=lambda x: x.capitalize(),
    )
    set_theme(selected_theme)

    st.sidebar.markdown("---")

    # -----------------------------
    # Ollama Status
    # -----------------------------
    if LLM_BACKEND == "ollama":
        status = get_backend_status()

        if status["available"] and status["name"] != "None":
            model_label = status["model"] or status["name"]
            st.sidebar.markdown(
                f"**{tr('model')}:** {model_label} :green[{tr('connected')}]"
            )
        else:
            st.sidebar.markdown(f"**{tr('model')}:** :orange[{tr('unavailable')}]")
            st.sidebar.info(tr("install_ollama"))

        st.sidebar.markdown("---")
