"""
Judge page for the AI Judge app.
"""
import uuid
from datetime import datetime

import pandas as pd
import streamlit as st


def judge():
    """This is the judge page."""
    st.subheader("Judge Management")

    with st.form("judge_form"):
        st.subheader("Create new judge")
        col1, col2 = st.columns(2)

        with col1:
            new_name = st.text_input("Judge name", "")
            model = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini", "o3-mini", "o3"])

        with col2:
            judge_type = st.selectbox("Type", ["LLM"])
            mode = st.selectbox("Mode", ["reference-free", "ground-truth"])

        system_prompt = st.text_area("System prompt", "")
        uploaded_file = None
        if mode == "ground-truth":
            uploaded_file = st.file_uploader("Upload expected response file", type=["csv", "json"])
        elif mode == "reference-free":
            uploaded_file = st.file_uploader("Upload rubric file", type=["csv", "json"])

        submitted = st.form_submit_button("Create")

        if submitted:
            # Generate unique ID and timestamp
            judge_id = 'ju-' + str(uuid.uuid4())[:16]  # Short UUID
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if not new_name:
                st.error("Judge name is required")
            elif not model:
                st.error("Model is required")
            elif not judge_type:
                st.error("Type is required")
            elif not mode:
                st.error("Mode is required")
            elif not system_prompt:
                st.error("System prompt is required")
            else:
                new_judge = {
                    "id": judge_id,
                    "name": new_name,
                    "model": model,
                    "type": judge_type,
                    "mode": mode,
                    "system_prompt": system_prompt,
                    "file": uploaded_file.name if uploaded_file else None,
                    "created_at": created_at,
                }
                st.session_state.judges.append(new_judge)
                st.success(f"Judge '{new_name}' created successfully")

    if len(st.session_state.judges) > 0:
        st.subheader("📋 Existing Judges")
        df = pd.DataFrame(st.session_state.judges)
        st.dataframe(df, use_container_width=True)

        # Show total count
        total = len(st.session_state.judges)
        st.markdown(f"### ✅ Total Judges: **{total}**")

        # Option to clear all judges
        if st.button("🗑️ Clear All Judges", type="secondary"):
            st.session_state.judges = []
            st.rerun()
    else:
        st.info(
            "No judges created yet. Create your first judge using the form above.")
