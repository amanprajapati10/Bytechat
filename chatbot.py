# chatbot.py
import os
import re
import requests
import streamlit as st
from groq import Groq

# --- Groq Client Initialization ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    MODEL = 'llama3-8b-8192'
except Exception as e:
    st.error(f"Groq API key not found. Please check your secrets. {e}", icon="🚨")
    st.stop()

# --- Agent Tools ---

def perform_google_search(query):
    """
    Performs a Google search using the Serper.dev API and returns a summary.
    """
    try:
        # This will read the new key from your Streamlit secrets
        serper_api_key = st.secrets["SERPER_API_KEY"]
        url = "https://google.serper.dev/search"
        payload = { "q": query }
        headers = { 'X-API-KEY': serper_api_key, 'Content-Type': 'application/json' }

        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        search_data = response.json()

        # Check for a direct answer box (like a calculator or definition)
        if search_data.get("answerBox"):
            answer = search_data["answerBox"].get("snippet") or search_data["answerBox"].get("answer")
            if answer:
                return f"Here's a direct answer I found:\n\n> {answer}"

        # If no direct answer, summarize the first organic result
        if search_data.get("organic"):
            first_result = search_data["organic"][0]
            return (
                f"According to a web search, here is the top result for '{query}':\n\n"
                f"**{first_result['title']}**\n"
                f"{first_result['snippet']}\n"
                f"*Source: {first_result['link']}*"
            )
        
        return f"I searched for '{query}' but couldn't find a clear summary. You might want to try a different query."

    except KeyError:
        return "The Serper API key is not configured. Please add `SERPER_API_KEY` to your Streamlit secrets."
    except requests.exceptions.RequestException as e:
        return f"Sorry, I couldn't perform the web search. Error: {e}"

# --- Main Agent Logic ---

def get_chat_response_stream(messages):
    """
    Acts as a "router" to decide whether to use the search tool or the LLM.
    """
    latest_user_message = messages[-1]["content"]
    prompt = latest_user_message.lower()

    # Tool Router: Use the search tool for any question that needs current info
    tool_to_use = None
    query = ""

    # Keywords that suggest a need for a live web search
    search_keywords = ["what is", "who is", "search for", "latest", "current", "weather", "score", "news", "price of"]
    if any(keyword in prompt for keyword in search_keywords):
        tool_to_use = perform_google_search
        # Use the original user message as the query for the best results
        query = latest_user_message
    
    # If a tool is identified, use it
    if tool_to_use and query:
        def stream_tool_result():
            yield f"Searching the web for '{query}'...\n\n"
            result = tool_to_use(query)
            yield result
        return stream_tool_result()

    # If no tool is used, fall back to the LLM for conversation
    api_messages = [
        {
            "role": "system",
            "content": (
                "You are 'ByteAgent', Aman Prajapati is your founder. You are a helpful AI assistant with a powerful web search tool. "
                "You use your search tool to answer questions that require up-to-date or specific information. "
                "For all other general queries, like creative writing or conversation, you act as a knowledgeable and friendly AI."
            )
        }
    ] + messages

    def generate_llm_chunks():
        try:
            stream = client.chat.completions.create(model=MODEL, messages=api_messages, stream=True)
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            st.error(f"An API error occurred: {e}", icon="🚨")
            yield f"Sorry, an error occurred: {e}"

    return generate_llm_chunks()
