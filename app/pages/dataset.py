"""
Dataset page for the AI Judge app.
"""
import uuid
from datetime import datetime

import pandas as pd
import streamlit as st


def dataset():
    """This is the dataset page."""
    st.subheader("Dataset Management")

    with st.form("dataset_form"):
        st.subheader("Create new dataset")
        new_name = st.text_input("Dataset name", "")
        system_prompt = st.text_area("System prompt", "")
        user_prompt = st.text_area("User prompt", "")
        uploaded_file = st.file_uploader(
            "Upload user input file", type=["csv", "json"])
        submitted = st.form_submit_button("Create")

        if submitted:
            if not new_name:
                st.error("Dataset name is required")
            elif not system_prompt:
                st.error("System prompt is required")
            elif not user_prompt:
                st.error("User prompt is required")
            else:
                # Generate unique ID and timestamp
                dataset_id = 'ds-' + str(uuid.uuid4())[:16]  # Short UUID
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                new_dataset = {
                    "id": dataset_id,
                    "name": new_name,
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt,
                    "user_input_file": uploaded_file.name if uploaded_file else None,
                    "created_at": created_at,
                }

                # Add to the list of datasets
                st.session_state.datasets.append(new_dataset)

                st.success(f"Dataset '{new_name}' created successfully with ID: {dataset_id}")

    # Display existing datasets
    if len(st.session_state.datasets) > 0:
        st.subheader("Existing Datasets")

        # Convert list to DataFrame for display
        df = pd.DataFrame(st.session_state.datasets)
        
        # Reorder columns to show ID first
        column_order = ["id", "name", "system_prompt", "user_prompt", "user_input_file", "created_at"]
        df = df[column_order]
        
        st.dataframe(df, use_container_width=True)

        # Show total count
        total = len(st.session_state.datasets)
        st.markdown(f"### ✅ Total Datasets: **{total}**")

        # Option to clear all datasets
        if st.button("🗑️ Clear All Datasets", type="secondary"):
            st.session_state.datasets = []
            st.rerun()
    else:
        st.info(
            "No datasets created yet. Create your first dataset using the form above.")
