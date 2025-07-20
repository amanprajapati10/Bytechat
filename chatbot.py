# chatbot.py
import os
import streamlit as st
from groq import Groq

# --- Groq Client Initialization ---
# This now securely reads the API key from Streamlit's secrets management.
try:
    client = Groq(
        api_key=st.secrets["GROQ_API_KEY"]
    )
    MODEL = 'llama3-8b-8192'
except Exception as e:
    # This will show an error on the page if the secret is not set.
    st.error("Groq API key not found. Please add it to your Streamlit secrets.", icon="🚨")
    st.info("Please follow the instructions in the app README to set up your API key.")
    st.stop()


def get_chat_response_stream(messages):
    """
    Gets a streaming response from the Groq API.
    This function now includes a generator to properly yield string content.
    """
    api_messages = [
        {"role": "system", "content": "You are bytechat, a helpful assistant."}
    ] + messages

    def generate_chunks():
        """
        A generator function that calls the API and yields the text content of each chunk.
        This is what st.write_stream needs.
        """
        try:
            # Call the Groq API to get a streaming response
            stream = client.chat.completions.create(
                model=MODEL,
                messages=api_messages,
                stream=True,
            )
            # Loop over the stream and yield just the content
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            # If an error occurs, yield the error message
            st.error(f"An API error occurred: {e}", icon="🚨")
            yield f"Sorry, an error occurred: {e}"

    return generate_chunks()

