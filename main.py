# main.py
import streamlit as st
import ui
import chatbot

# Set up the page UI using the function from ui.py
ui.setup_page()

# Initialize chat history in session state
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

# Display past messages using the function from ui.py
ui.display_chat_history(st.session_state.messages)

# Get user input using the function from ui.py
if prompt := ui.get_user_input():
    # Add user's message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant's response while streaming
    with st.chat_message("assistant"):
        try:
            # Get the stream from the chatbot module
            stream = chatbot.get_chat_response_stream(st.session_state.messages)
            
            # Stream the response to the UI
            response = st.write_stream(stream)
            
            # Add the complete response to the chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        except Exception as e:
            # Display an error message if something goes wrong
            error_message = f"Sorry, an error occurred: {e}"
            st.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})
