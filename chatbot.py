# chatbot.py
import os
import re
import requests # Import the requests library for making HTTP requests
import streamlit as st
from groq import Groq

# --- Groq Client Initialization ---
try:
    client = Groq(
        api_key=st.secrets["GROQ_API_KEY"]
    )
    MODEL = 'llama3-8b-8192'
except Exception as e:
    st.error(f"Error initializing Groq client: {e}", icon="🚨")
    st.stop()

# --- Agent Tools ---

def perform_web_search(query):
    """
    Performs a web search using the DuckDuckGo Instant Answer API.
    This is a simple API that doesn't require an API key.
    """
    url = f"https://api.duckduckgo.com/?q={query}&format=json&pretty=1"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()
        
        # Extract the most relevant information
        if data.get("AbstractText"):
            return data["AbstractText"]
        elif data.get("Heading"):
            return f"I found this information for '{data['Heading']}': {data.get('RelatedTopics', [{}])[0].get('Text', 'No further details.')}"
        elif data.get("Answer"):
            return data["Answer"]
        else:
            return "I couldn't find a direct answer. Please try rephrasing your search."

    except requests.exceptions.RequestException as e:
        return f"Sorry, I couldn't perform the web search. Error: {e}"

# --- Main Agent Logic ---

def get_chat_response_stream(messages):
    """
    Handles the core logic of the AI agent.
    It checks for tool use (web search) first, then falls back to the LLM.
    """
    latest_user_message = messages[-1]["content"]
    
    # Tool Use Check: Web Search
    # Looks for keywords that suggest a real-time information need.
    search_keywords = ["weather in", "score of", "latest news on", "search for", "what is the current"]
    
    # A simple regex to find the actual query after the keyword
    search_query_match = None
    for keyword in search_keywords:
        if keyword in latest_user_message.lower():
            # Extract the text that comes after the keyword
            match = re.search(rf'{re.escape(keyword)}\s*(.*)', latest_user_message, re.IGNORECASE)
            if match and match.group(1):
                search_query_match = match.group(1).strip()
                break

    if search_query_match:
        # A generator to stream the search result
        def stream_search_result():
            search_result = perform_web_search(search_query_match)
            yield f"Searching the web for '{search_query_match}'...\n\n"
            yield search_result
        
        return stream_search_result()

    # If no tool is used, proceed with a standard LLM call
    api_messages = [
        {
            "role": "system",
            "content": (
                "You are 'ByteAgent', a helpful and conversational AI assistant. "
                "You have the ability to perform live web searches for real-time information like weather, sports scores, and news. "
                "When you use your search tool, clearly state what you found. "
                "For all other queries, answer as a knowledgeable and friendly AI."
            )
        }
    ] + messages

    def generate_llm_chunks():
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=api_messages,
                stream=True,
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            st.error(f"An API error occurred: {e}", icon="🚨")
            yield f"Sorry, an error occurred: {e}"

    return generate_llm_chunks()
