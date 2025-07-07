"""
Quality evaluation page for the AI Judge app.
"""
import uuid
from datetime import datetime

import pandas as pd
import streamlit as st


def quality_eval():
    """This is the quality evaluation page."""
    st.subheader("Quality Evaluation")

    with st.form("quality_eval_form"):
        st.subheader("Create new quality evaluation")
        new_name = st.text_input("Quality evaluation name", "")

        col1, col2 = st.columns(2)
        with col1:
            candidate_id = st.selectbox(
                "Candidate", ["None"] + [ca["id"] for ca in st.session_state.candidates])
        with col2:
            judge_id = st.selectbox(
                "Judge", ["None"] + [ju["id"] for ju in st.session_state.judges])

        submitted = st.form_submit_button("Create")

        if submitted:
            # Generate unique ID and timestamp
            quality_eval_id = 'qe-' + str(uuid.uuid4())[:16]  # Short UUID
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if not new_name:
                st.error("Quality evaluation name is required")
            elif not candidate_id or candidate_id == "None":
                st.error("Candidate is required")
            elif not judge_id or judge_id == "None":
                st.error("Judge is required")
            else:
                new_quality_eval = {
                    "id": quality_eval_id,
                    "name": new_name,
                    "candidate_id": candidate_id,
                    "judge_id": judge_id,
                    "created_at": created_at,
                }
                st.session_state.quality_evals.append(new_quality_eval)
                st.success(
                    f"Quality evaluation '{new_name}' created successfully")

    if len(st.session_state.quality_evals) > 0:
        st.subheader("📋 Finished Quality Evaluations")
        df = pd.DataFrame(st.session_state.quality_evals)
        st.dataframe(df, use_container_width=True)

        # Show total count
        total = len(st.session_state.quality_evals)
        st.markdown(f"### ✅ Total Quality Evaluations: **{total}**")

        if st.button("🗑️ Clear All Quality Evaluations", type="secondary"):
            st.session_state.quality_evals = []
            st.rerun()
    else:
        st.info(
            "No quality evaluations created yet. Create your first quality evaluation using the form above.")
