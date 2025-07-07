"""Home page for the AI Judge evals system."""
import streamlit as st


def home():
    """This is the home page."""
    st.header("Welcome to LLM Evals System")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 System Overview")
        st.write("""
        This evaluation system allows you to:
        - Manage candidate models for evaluation
        - Configure datasets for testing
        - Set up judge configurations
        - Run quality evaluations
        - Perform latency evaluations
        """)

    with col2:
        st.subheader("🚀 Quick Start")
        st.write("""
        1. **Configure Models**: Set up your candidate models
        2. **Prepare Data**: Upload or configure your evaluation datasets
        3. **Setup Judge**: Configure evaluation criteria and judges
        4. **Run Evaluations**: Execute quality and latency tests
        5. **Review Results**: Analyze the evaluation outcomes
        """)

    st.divider()

    # Quick stats or status
    st.subheader("📈 System Status")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("API Status", "Connected")
    with col2:
        st.metric("Candidates", len(st.session_state.candidates))
    with col3:
        st.metric("Judges", len(st.session_state.judges))
    with col4:
        st.metric("Quality Evaluations", len(st.session_state.quality_evals))
    with col5:
        st.metric("Latency Evaluations", len(st.session_state.latency_evals))
