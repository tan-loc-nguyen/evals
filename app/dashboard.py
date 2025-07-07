"""Dashboard page with sidebar navigation for the AI Judge evals system."""
import streamlit as st

from app.pages.candidate import candidate
from app.pages.dataset import dataset
from app.pages.judge import judge
from app.pages.latency_eval import latency_eval
from app.pages.quality_eval import quality_eval
from app.pages.home import home


def dashboard():
    """Main dashboard with sidebar navigation."""
    st.title("🧪 LLM Evals System")

    # Sidebar navigation
    with st.sidebar:
        # Display current API key (masked)
        if st.session_state.get("api_key"):
            masked_key = st.session_state["api_key"][:8] + \
                "..." + st.session_state["api_key"][-4:]
            st.info(f"API Key: {masked_key}")

        # Logout button
        if st.button("Exit", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.divider()

        # Page navigation
        st.markdown("### 📂 Navigation")

        # Initialize current page if not set
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = "Home"

        # Navigation buttons
        pages = [
            ("🏠", "Home"),
            ("📊", "Dataset Management"),
            ("🤖", "Candidate Configuration"),
            ("⚖️", "Judge Configuration"),
            ("🎯", "Quality Evaluation"),
            ("⚡", "Latency Evaluation")
        ]

        for icon, page_name in pages:
            if st.button(
                f"{icon} {page_name}",
                key=f"nav_{page_name}",
                use_container_width=True,
                type="primary" if st.session_state["current_page"] == page_name else "secondary"
            ):
                st.session_state["current_page"] = page_name
                st.rerun()

        page = st.session_state["current_page"]

    # Route to appropriate page based on selection
    if page == "Home":
        home()
    elif page == "Candidate Configuration":
        candidate()
    elif page == "Dataset Management":
        dataset()
    elif page == "Judge Configuration":
        judge()
    elif page == "Quality Evaluation":
        quality_eval()
    elif page == "Latency Evaluation":
        latency_eval()
