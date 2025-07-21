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
            ),
            "avatar": ui.BYTEAGENT_AVATAR # <--- Correct: Initial assistant message gets ByteAgent's avatar
        }
    ]

# Display past messages using the function from ui.py
ui.display_chat_history(st.session_state.messages)

# Get user input using the function from ui.py
if prompt := ui.get_user_input():
    # Add user's message to history with the correct avatar
    st.session_state.messages.append({"role": "user", "content": prompt, "avatar": ui.USER_AVATAR}) # <--- Correct: User message gets user's avatar

    # Streamlit reruns the app when session_state is updated or input changes.
    # The ui.display_chat_history function (called above) will now handle showing the new user message
    # with its avatar when the app reruns. So, we remove the redundant display here.
    # with st.chat_message("user"): # <--- REMOVED: This redundant display block
    #     st.markdown(prompt)       # <--- REMOVED: is now handled by ui.display_chat_history on rerun

    # Display assistant's response while streaming
    # Ensure the streaming message uses the correct avatar
    with st.chat_message("assistant", avatar=ui.BYTEAGENT_AVATAR): # <--- Correct: Pass ByteAgent avatar to the streaming message
        try:
            # Get the stream from the chatbot module
            stream = chatbot.get_chat_response_stream(st.session_state.messages)

            # Stream the response to the UI
            response = st.write_stream(stream)

            # Add the complete response to the chat history with the correct avatar
            st.session_state.messages.append({"role": "assistant", "content": response, "avatar": ui.BYTEAGENT_AVATAR}) # <--- Correct: Historical assistant message gets ByteAgent's avatar

        except Exception as e:
            # Display an error message if something goes wrong
            error_message = f"Sorry, an error occurred: {e}"
            st.error(error_message)
            # Add the error message to chat history with assistant's avatar
            st.session_state.messages.append({"role": "assistant", "content": error_message, "avatar": ui.BYTEAGENT_AVATAR}) # <--- Correct: Error message gets ByteAgent's avatar