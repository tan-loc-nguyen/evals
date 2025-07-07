"""
State management for the AI Judge app.
"""
import streamlit as st


def init_session_state():
    """Initialize the session state with default values."""
    defaults = {
        "api_key": "",
        "api_key_valid": False,
        "current_page": "Home",
        "datasets": [],
        "candidates": [],
        "judges": [],
        "quality_evals": [],
        "latency_evals": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
