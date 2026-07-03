import streamlit as st

from config import APP_TITLE, APP_ICON
from llm.local_llm import get_backend_status


def render_sidebar() -> None:
    st.sidebar.markdown(f"# {APP_ICON} {APP_TITLE}")
    st.sidebar.markdown("---")

    status = get_backend_status()
    if status["available"] and status["name"] != "None":
        model_label = status["model"] or status["name"]
        st.sidebar.markdown(f"**Model:** {model_label} :green[Connected]")
    else:
        st.sidebar.markdown(
            "**Model:** :orange[Unavailable]  \n"
            "Install [Ollama](https://ollama.com) and run `ollama pull llama3.2`"
        )
    st.sidebar.markdown("---")
