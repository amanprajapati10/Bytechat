# ui.py
import streamlit as st

# --- Define your chosen emoji icons here ---
BYTEAGENT_AVATAR = "🤖" # Icon for the assistant (ByteAgent)
USER_AVATAR = "🧑"     # Icon for the user (you)
# ------------------------------------------

def setup_page():
    """
    Sets up the page title and initial configuration.
    """
    st.set_page_config(page_title="ByteChat", page_icon="💬")
    st.title("👽 ByteChat")
    st.caption("A streaming chatbot with a modular structure")

def display_chat_history(messages):
    """
    Displays the chat history on the page with custom avatars.
    """
    for message in messages:
        # Determine the correct avatar based on the role
        # If the message role is 'assistant', use BYTEAGENT_AVATAR, otherwise use USER_AVATAR
        avatar_to_use = BYTEAGENT_AVATAR if message["role"] == "assistant" else USER_AVATAR
        
        with st.chat_message(message["role"], avatar=avatar_to_use): # Use 'avatar' parameter here
            st.markdown(message["content"])

def get_user_input():
    """
    Gets user input from the chat input field.
    Returns the prompt or None.
    """
    return st.chat_input("What would you like to ask?")