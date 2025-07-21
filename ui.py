# ui.py
import streamlit as st
USER_AVATAR = "🧑"

def setup_page():
    st.set_page_config(page_title="ByteChat", page_icon="💬")
    st.title("👽 ByteChat")
    st.caption("A streaming chatbot with a modular structure")

def display_chat_history(messages):
    for message in messages:
        if message["role"] == "user":
            # For the user, create the message with their custom avatar
            with st.chat_message(message["role"], avatar=USER_AVATAR):
                st.markdown(message["content"])
        else:
            # For the assistant, create the message without a custom avatar
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

def get_user_input():
    return st.chat_input("What would you like to ask?")
