import csv
import re
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import plotly.express as px
import plotly.graph_objects as go
from colorama import Fore, Style
from typing import Dict
import streamlit as st

# Download required lexicon
nltk.download('vader_lexicon')

# ---------- Extract Video ID ----------
def extract_video_id(youtube_link: str) -> str:
    video_id_regex = r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(video_id_regex, youtube_link)
    return match.group(1) if match else None

# ---------- Analyze Sentiment ----------
def analyze_sentiment(csv_file: str) -> Dict[str, int]:
    sid = SentimentIntensityAnalyzer()
    comments = []

    with open(csv_file, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        comments = [row['Comment'] for row in reader]

    num_neutral, num_positive, num_negative = 0, 0, 0

    for comment in comments:
        score = sid.polarity_scores(comment)['compound']
        if score == 0.0:
            num_neutral += 1
        elif score > 0.0:
            num_positive += 1
        else:
            num_negative += 1

    return {
        'num_neutral': num_neutral,
        'num_positive': num_positive,
        'num_negative': num_negative
    }

# ---------- Bar Chart ----------
def bar_chart(csv_file: str) -> None:
    results = analyze_sentiment(csv_file)
    df = pd.DataFrame({
        'Sentiment': ['Positive', 'Negative', 'Neutral'],
        'Number of Comments': [
            results['num_positive'],
            results['num_negative'],
            results['num_neutral']
        ]
    })

    fig = px.bar(
        df,
        x='Sentiment',
        y='Number of Comments',
        color='Sentiment',
        color_discrete_sequence=['green', 'red', 'gray'],
        title='Sentiment Analysis - Bar Chart'
    )
    fig.update_layout(title_font_size=20)
    st.plotly_chart(fig, use_container_width=True)

# ---------- Pie Chart ----------
def plot_sentiment(csv_file: str) -> None:
    results = analyze_sentiment(csv_file)
    fig = go.Figure(data=[go.Pie(
        labels=['Neutral', 'Positive', 'Negative'],
        values=[results['num_neutral'], results['num_positive'], results['num_negative']],
        marker=dict(colors=['yellow', 'green', 'red']),
        textinfo='label+percent'
    )])
    fig.update_layout(
        title='Sentiment Distribution - Pie Chart',
        title_font_size=20
    )
    st.plotly_chart(fig)

# ---------- Scatterplot (Optional Use) ----------
def create_scatterplot(csv_file: str, x_column: str, y_column: str) -> None:
    data = pd.read_csv(csv_file)
    fig = px.scatter(data, x=x_column, y=y_column, color='Category')
    fig.update_layout(
        title='Custom Scatter Plot',
        xaxis_title=x_column,
        yaxis_title=y_column
    )
    st.plotly_chart(fig)

# ---------- Print Sentiment (Terminal Only) ----------
def print_sentiment(csv_file: str) -> None:
    results = analyze_sentiment(csv_file)
    if results['num_positive'] > results['num_negative']:
        sentiment, color = 'POSITIVE', Fore.GREEN
    elif results['num_negative'] > results['num_positive']:
        sentiment, color = 'NEGATIVE', Fore.RED
    else:
        sentiment, color = 'NEUTRAL', Fore.YELLOW

    print('\n' + Style.BRIGHT + color + sentiment.center(50, ' ') + Style.RESET_ALL)
