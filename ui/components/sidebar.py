import streamlit as st

from config import APP_ICON, APP_TITLE
from i18n.translator import (
    LANGUAGES,
    get_language,
    init_language,
    set_language,
    tr,
)
from llm.local_llm import get_backend_status


def render_sidebar() -> None:
    init_language()

    st.sidebar.markdown(f"# {APP_ICON} {APP_TITLE}")

    # Language Selector
    selected = st.sidebar.selectbox(
        tr("language"),
        options=list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(get_language()),
        format_func=lambda code: LANGUAGES[code],
    )

    set_language(selected)

    st.sidebar.markdown("---")

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
