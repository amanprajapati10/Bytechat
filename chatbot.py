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

def get_weather(city):
    """Gets the current weather for a given city using the Open-Meteo API."""
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_response = requests.get(geo_url, timeout=5)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        if not geo_data.get("results"):
            return f"Sorry, I couldn't find the city '{city}'. Please check the spelling."

        location = geo_data["results"][0]
        lat, lon = location["latitude"], location["longitude"]

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_response = requests.get(weather_url, timeout=5)
        weather_response.raise_for_status()
        weather_data = weather_response.json()["current_weather"]
        
        return (
            f"The current weather in {location['name']}, {location.get('country', '')} is:\n"
            f"- **Temperature:** {weather_data['temperature']}°C\n"
            f"- **Wind Speed:** {weather_data['windspeed']} km/h"
        )
    except requests.exceptions.RequestException as e:
        return f"Sorry, I couldn't fetch the weather. Error: {e}"

def get_news(topic):
    """Gets the latest news on a topic using The News API."""
    try:
        news_api_key = st.secrets["NEWS_API_KEY"]
        url = f"https://api.thenewsapi.com/v1/news/top?api_token={news_api_key}&search={topic}&limit=3"
        news_response = requests.get(url, timeout=5)
        news_response.raise_for_status()
        news_data = news_response.json()

        if not news_data.get("data"):
            return f"I couldn't find any recent news about '{topic}'."
        
        articles = news_data["data"]
        headlines = [f"- {article['title']}" for article in articles]
        return f"Here are the top headlines about '{topic}':\n" + "\n".join(headlines)

    except KeyError:
        return "The News API key is not configured. Please add `NEWS_API_KEY` to your Streamlit secrets."
    except requests.exceptions.RequestException as e:
        return f"Sorry, I couldn't fetch the news. Error: {e}"

def get_cricket_score():
    """Gets live cricket scores using the CricAPI."""
    try:
        cricket_api_key = st.secrets["CRICKET_API_KEY"]
        url = f"https://api.cricapi.com/v1/cricScore?apikey={cricket_api_key}"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()

        if not data.get("data"):
            return "No live cricket matches found at the moment."
        
        live_matches = [match for match in data["data"] if "running" in match.get("status", "").lower()]
        if not live_matches:
            return "There are no live cricket matches happening right now."

        # Format the scores for all live matches
        score_summaries = []
        for match in live_matches:
            summary = f"**{match.get('t1', 'Team 1')} vs {match.get('t2', 'Team 2')}**\n"
            summary += f"*{match.get('status', 'No status available')}*\n"
            if match.get('t1s'):
                summary += f"- {match.get('t1', 'Team 1')}: {match.get('t1s', '')}\n"
            if match.get('t2s'):
                summary += f"- {match.get('t2', 'Team 2')}: {match.get('t2s', '')}\n"
            score_summaries.append(summary)
        
        return "Here are the current live scores:\n\n" + "\n".join(score_summaries)

    except KeyError:
        return "The Cricket API key is not configured. Please add `CRICKET_API_KEY` to your Streamlit secrets."
    except requests.exceptions.RequestException as e:
        return f"Sorry, I couldn't fetch the cricket scores. Error: {e}"

# --- Main Agent Logic ---

def get_chat_response_stream(messages):
    """
    Acts as a "router" to decide whether to use a tool or the LLM.
    """
    latest_user_message = messages[-1]["content"]
    prompt = latest_user_message.lower()

    # Tool Router: Decide which tool to use, if any
    tool_to_use = None
    query = ""

    if "weather in" in prompt:
        tool_to_use = get_weather
        query = prompt.split("weather in", 1)[1].strip()
    elif "news about" in prompt:
        tool_to_use = get_news
        query = prompt.split("news about", 1)[1].strip()
    elif "cricket score" in prompt or "live score" in prompt:
        tool_to_use = get_cricket_score
        # This tool doesn't need a specific query, it gets all live matches
    
    # If a tool is identified, use it
    if tool_to_use:
        def stream_tool_result():
            # Pass the query only if the tool needs it
            if tool_to_use in [get_weather, get_news]:
                yield f"Using my {tool_to_use.__name__} tool for '{query}'...\n\n"
                result = tool_to_use(query)
            else:
                yield f"Using my {tool_to_use.__name__} tool...\n\n"
                result = tool_to_use()
            yield result
        return stream_tool_result()

    # If no tool is used, fall back to the LLM
    api_messages = [
        {
            "role": "system",
            "content": (
                "You are 'ByteAgent', Aman Prajapati is your founder. You are a helpful AI assistant with multiple tools. "
                "You can get live weather, news, and cricket scores. "
                "For all other general queries, you act as a knowledgeable and friendly AI."
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
            st.error(f"An API error occurred: {e}", icon="�")
            yield f"Sorry, an error occurred: {e}"

    return generate_llm_chunks()
