# main.py
import streamlit as st
import ui
import chatbot

# Set up the page UI
ui.setup_page()

# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! I'm ByteAgent. I can answer your questions and search the web for real-time information. "
                "Feel free to ask me anything!"
            )
        }
    ]

# Display the chat history on each rerun
ui.display_chat_history(st.session_state.messages)

# Handle user input
if prompt := ui.get_user_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Rerun to display the user's message immediately
    st.rerun()

# Generate a new response if the last message is from the user
if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        try:
            stream = chatbot.get_chat_response_stream(st.session_state.messages)
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        except Exception as e:
            error_message = f"Sorry, an error occurred: {e}"
            st.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})

