import streamlit as st
from datetime import datetime
from typing import Any

# ── DEFAULT STATE ─────────────────────────────────────────────
_DEFAULTS = {
    "resume_text": None,
    "resume_filename": None,
    "job_description": "",
    "selected_role": "Software Engineer",
    "analysis_result": None,
    "improvement_result": None,
    "interview_result": None,
    "trigger_analysis": False,
    "trigger_improvement": False,
    "trigger_interview": False,
    "analysis_history": [],
}


def initialize_session_state():
    """Initialize all session state BEFORE widgets are created."""
    for key, value in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_session(key: str, default: Any = None) -> Any:
    return st.session_state.get(key, default)


def set_session(key: str, value: Any) -> None:
    """
    SAFE setter:
    Prevent overwriting widget-controlled keys after creation.
    """
    # ❌ DO NOT allow overriding widget-managed keys
    widget_keys = {"job_description", "role_selector", "uploaded_resume"}

    if key in widget_keys:
        return  # silently ignore to avoid crash

    st.session_state[key] = value


def add_to_history(entry: dict) -> None:
    entry["timestamp"] = datetime.now().strftime("%d %b %Y · %H:%M:%S")
    history = st.session_state.get("analysis_history", [])
    history.append(entry)
    st.session_state["analysis_history"] = history[-50:]


def clear_history() -> None:
    st.session_state["analysis_history"] = []