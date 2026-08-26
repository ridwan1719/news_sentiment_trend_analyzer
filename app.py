import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from textblob import TextBlob
from dotenv import load_dotenv
from datetime import datetime
import os
import warnings

warnings.filterwarnings("ignore")

load_dotenv()

NEWS_API_KEY = st.secrets["NEWS_API_KEY"]

st.set_page_config(
    page_title="Sentiment Trend Analysis",
    layout="wide"
)

st.title("Get Yourself Updated on What World Thinks About Your Interest")

st.markdown("""
    Real-time Update of News Sentiment
"""
)

default_topics = ["AI", "Ethereum", "US Economy", "JPMorgan Chase", "Morgan Stanley", "Crypto Currency", "Bitcoin", "EV", "NVidia", "OpenAI", "Anthropic"]

if "topics" not in st.session_state:
    st.session_state.topics = default_topics

st.sidebar.header("Dashboard Control")

new_topic = st.sidebar.text_input("Add your topic")

if st.sidebar.button("Add Topic"):
    if new_topic and new_topic not in st.session_state.topics:
        st.session_state.topics.append(new_topic)


selected_topic = st.sidebar.selectbox("Select a topic", st.session_state.topics)

article_limit = st.sidebar.slider("Select number of articles to analyze", min_value=10, max_value=50, 
                                  value=30, step=10)

url = (
    f"https://newsapi.org/v2/everything?"
    f"q={selected_topic}&"
    f"pageSize={article_limit}&"
    f"sortBy=publishedAt&"
    f"language=en&"
    f"apiKey={NEWS_API_KEY}"
)

response = requests.get(url)

data = response.json()

articles = data.get("articles", [])

news_data = []

for article in articles:
    title = article["title"]
    analysis = TextBlob(title)
    polarity = analysis.sentiment.polarity

    if polarity > 0:
        sentiment = "Positive"
    elif polarity < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    news_data.append({
        "title": title, 
        "Source": article["source"]["name"],
        "Published At": article["publishedAt"][:10],
        "Sentiment": sentiment,
        "polarity": polarity,
        "URL": article["url"]
    })

df = pd.DataFrame(news_data)

positive_count = len(df[df["Sentiment"] == "Positive"])
negative_count = len(df[df["Sentiment"] == "Negative"])
neutral_count = len(df[df["Sentiment"] == "Neutral"])

col1, col2, col3 = st.columns(3)

col1.metric("Positive Articles", positive_count)
col2.metric("Negative Articles", negative_count)    
col3.metric("Neutral Articles", neutral_count)


fig = px.pie(df, names="Sentiment", title=f"Sentiment Percentage for '{selected_topic}'")
st.plotly_chart(fig, use_container_width=True)

hist_fig = px.histogram(df, x="polarity", color="Sentiment", title=f"Sentiment Polarity Distribution for '{selected_topic}'")
st.plotly_chart(hist_fig, use_container_width=True)

for index, row in df.iterrows():
    st.subheader(f"Title: {row['title']}")
    st.write(f"Source: {row['Source']}")
    st.write(f"Published At: {row['Published At']}")
    st.write(f"Sentiment: {row['Sentiment']}")
    st.write(f"Polarity: {row['polarity']}")
    st.write(f"[Read More]({row['URL']})")
    st.markdown("---")
