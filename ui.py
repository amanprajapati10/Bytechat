# ui.py
import streamlit as st

def setup_page():
    """
    Sets up the page title and initial configuration.
    """
    st.set_page_config(page_title="ByteChat", page_icon="💬")
    st.title("👽 ByteChat")
    st.caption("A streaming chatbot with a modular structure")

def display_chat_history(messages):
    """
    Displays the chat history on the page.
    """
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def get_user_input():
    """
    Gets user input from the chat input field.
    Returns the prompt or None.
    """
    return st.chat_input("What would you like to ask?")
