"""Main entry point for the AI Judge evals system."""
import streamlit as st
from app.dashboard import dashboard
from app.entry import entry
from app.state import init_session_state

def main():
    """Main function to handle app routing."""
    # Initialize session state
    init_session_state()
    
    # Configure Streamlit page
    st.set_page_config(
        page_title="AI Judge Evals System",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Check if API key is provided and valid
    if not st.session_state.get("api_key") or not st.session_state.get("api_key_valid"):
        entry()
    else:
        dashboard()

if __name__ == "__main__":
    main()
