"""
Latency evaluation page for the AI Judge app.
"""
import uuid
from datetime import datetime

import pandas as pd
import streamlit as st


def latency_eval():
    """This is the latency evaluation page."""
    st.subheader("Latency Evaluation")

    with st.form("latency_eval_form"):
        st.subheader("Create new latency evaluation")
        new_name = st.text_input("Latency evaluation name", "")
        col1, col2 = st.columns(2)
        with col1:
            candidate_id = st.selectbox(
                "Candidate", ["None"] + [ca["id"] for ca in st.session_state.candidates])
        with col2:
            num_of_runs = st.number_input(
                "Number of runs", min_value=1, max_value=100)
        submitted = st.form_submit_button("Create")

        if submitted:
            # Generate unique ID and timestamp
            latency_eval_id = 'le-' + str(uuid.uuid4())[:16]  # Short UUID
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if not new_name:
                st.error("Latency evaluation name is required")
            elif not candidate_id or candidate_id == "None":
                st.error("Candidate is required")
            elif num_of_runs < 1 or num_of_runs > 100:
                st.error("Number of runs must be between 1 and 100")
            else:
                new_latency_eval = {
                    "id": latency_eval_id,
                    "name": new_name,
                    "candidate_id": candidate_id,
                    "num_of_runs": num_of_runs,
                    "created_at": created_at,
                }
                st.session_state.latency_evals.append(new_latency_eval)
                st.success(
                    f"Latency evaluation '{new_name}' created successfully")

    if len(st.session_state.latency_evals) > 0:
        st.subheader("📋 Finished Latency Evaluations")
        df = pd.DataFrame(st.session_state.latency_evals)
        st.dataframe(df, use_container_width=True)

        # Show total count
        total = len(st.session_state.latency_evals)
        st.markdown(f"### ✅ Total Latency Evaluations: **{total}**")

        if st.button("🗑️ Clear All Latency Evaluations", type="secondary"):
            st.session_state.latency_evals = []
            st.rerun()
    else:
        st.info(
            "No latency evaluations created yet. Create your first latency evaluation using the form above.")
