"""
Entry page for the AI Judge app.
"""
import os

import openai
import streamlit as st
from dotenv import load_dotenv


def entry():
    """Entry page for API key input and validation."""
    st.title("🧪 LLM Evals System")

    # Load environment variables from .env file
    load_dotenv()

    # Check if we already have an API key in .env
    existing_key = os.getenv("OPENAI_API_KEY")

    col1, col2, col3 = st.columns([2, 3, 2])

    with col2:
        st.markdown("### OpenAI API Key Configuration")
        st.markdown(
            "Please provide your OpenAI API key to access the evaluation system.")

        # Show existing key option if available
        if existing_key:
            st.markdown("#### 🔑 Existing API Key Found")
            masked_key = f"{existing_key[:8]}...{existing_key[-4:]}" if len(
                existing_key) > 12 else "sk-***"
            st.info(f"Found existing key: `{masked_key}`")

            col_use, col_new = st.columns(2)

            with col_use:
                if st.button("✅ Use Existing Key", use_container_width=True):
                    if validate_api_key(existing_key):
                        st.session_state["api_key"] = existing_key
                        st.session_state["api_key_valid"] = True
                        st.success(
                            "✅ Existing API key validated successfully!")
                        st.rerun()
                    else:
                        st.error(
                            "❌ Existing API key is invalid. Please enter a new one.")

            with col_new:
                if st.button("🆕 Enter New Key", use_container_width=True):
                    st.session_state["show_new_key_input"] = True
                    st.rerun()

            st.divider()

        # Show new key input (always visible if no existing key, or if user clicked "Enter New Key")
        show_input = not existing_key or st.session_state.get(
            "show_new_key_input", False)

        if show_input:
            if existing_key:
                st.markdown("#### 🔄 Enter New API Key")
                st.markdown("This will overwrite the existing key.")
            else:
                st.markdown("#### 🔑 Enter API Key")

            # API key input
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Enter your OpenAI API key (sk-...)",
                placeholder="sk-..."
            )

            # Submit button
            if st.button("🚀 Connect", use_container_width=True):
                if api_key:
                    if validate_api_key(api_key):
                        st.session_state["api_key"] = api_key
                        st.session_state["api_key_valid"] = True

                        # Save the API key to .env file (this will overwrite existing)
                        save_api_key_to_env(api_key)

                        # Clear the show_new_key_input flag
                        if "show_new_key_input" in st.session_state:
                            del st.session_state["show_new_key_input"]

                        st.success(
                            "✅ API key validated and saved successfully!")
                        st.rerun()
                    else:
                        st.error(
                            "❌ Invalid API key. Please check your key and try again.")
                else:
                    st.error("❌ Please enter an API key.")

        st.divider()

        # Help section
        with st.expander("ℹ️ How to get your OpenAI API Key"):
            st.markdown("""
            1. Go to [OpenAI Platform](https://platform.openai.com/)
            2. Sign in to your account
            3. Navigate to **API Keys** section
            4. Click **Create new secret key**
            5. Copy the key and paste it above
            
            **Note**: Your API key will be stored securely in a .env file and in your session.
            """)


def validate_api_key(api_key: str) -> bool:
    """Validate OpenAI API key by making a simple API call."""
    try:
        client = openai.OpenAI(api_key=api_key)
        # Make a simple API call to validate the key
        response = client.models.list()
        print(response)
        return True
    except openai.AuthenticationError:
        return False
    except Exception as e:
        print(f"Error validating API key: {e}")
        return False


def save_api_key_to_env(api_key: str):
    """Save the API key to .env file."""
    env_path = ".env"

    # Read existing .env content if it exists
    existing_lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            existing_lines = f.readlines()

    # Check if OPENAI_API_KEY already exists and update it
    updated = False
    for i, line in enumerate(existing_lines):
        if line.strip().startswith("OPENAI_API_KEY="):
            existing_lines[i] = f"OPENAI_API_KEY={api_key}\n"
            updated = True
            break

    # If not found, add it
    if not updated:
        existing_lines.append(f"OPENAI_API_KEY={api_key}\n")

    # Write back to .env file
    with open(env_path, 'w') as f:
        f.writelines(existing_lines)

    print(f"API key saved to {env_path}")
