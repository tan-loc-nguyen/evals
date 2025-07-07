"""
Candidate page for the AI Judge app.
"""
import json
import uuid
from datetime import datetime

import pandas as pd
import streamlit as st


def candidate():
    """This is the candidate page."""
    st.subheader("Candidate Management")

    # Initialize candidate storage if not already
    if "candidates" not in st.session_state:
        st.session_state.candidates = []

    with st.form("candidate_form"):
        st.subheader("Create new candidate")

        col1, col2 = st.columns(2)

        with col1:
            new_name = st.text_input("Candidate name", "")
            model = st.selectbox(
                "Model", ["gpt-4o", "gpt-4o-mini", "o3-mini", "o3"])
            dataset_id = st.selectbox(
                "Dataset", ["None"] + [ds["id"] for ds in st.session_state.datasets])
            metadata_input = st.text_area(
                "Metadata (JSON format)", "{\n  \"team\": \"alpha\",\n  \"feature\": \"trip-plan\"\n}", height=100)

        with col2:
            temperature = st.slider("Temperature", 0.0, 2.0, 1.0)
            top_p = st.slider("Top P", 0.0, 1.0, 1.0)
            seed = st.number_input("Seed", min_value=0,
                                   max_value=1000000, value=42)

        submitted = st.form_submit_button("Create")

        if submitted:
            # Generate unique ID and timestamp
            candidate_id = 'ca-' + str(uuid.uuid4())[:16]  # Short UUID
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Validate input
            if not new_name:
                st.error("Candidate name is required")
            elif not model:
                st.error("Model is required")
            else:
                try:
                    metadata = json.loads(metadata_input)
                    new_candidate = {
                        "id": candidate_id,
                        "name": new_name,
                        "model": model,
                        "temperature": temperature,
                        "top_p": top_p,
                        "seed": seed,
                        "metadata": metadata,
                        "dataset_id": dataset_id if dataset_id != "None" else None,
                        "created_at": created_at,
                    }
                    st.session_state.candidates.append(new_candidate)
                    st.success(f"Candidate '{new_name}' created successfully")

                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON in metadata: {str(e)}")

    if len(st.session_state.candidates) > 0:
        st.subheader("📋 Existing Candidates")
        df = pd.DataFrame(st.session_state.candidates)
        st.dataframe(df, use_container_width=True)

        # Show total count
        total = len(st.session_state.candidates)
        st.markdown(f"### ✅ Total Candidates: **{total}**")

        # Option to clear all datasets
        if st.button("🗑️ Clear All Candidates", type="secondary"):
            st.session_state.candidates = []
            st.rerun()
    else:
        st.info(
            "No candidates created yet. Create your first candidate using the form above.")
