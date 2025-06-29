import csv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit as st
from Senti import extract_video_id
import warnings

warnings.filterwarnings('ignore')

# ---------- Initialize YouTube API Client ----------
DEVELOPER_KEY = st.secrets["API_KEY"]
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

youtube = build(
    YOUTUBE_API_SERVICE_NAME,
    YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY
)

# ---------- Get Channel ID ----------
def get_channel_id(video_id: str) -> str:
    response = youtube.videos().list(part='snippet', id=video_id).execute()
    return response['items'][0]['snippet']['channelId']

# ---------- Save Video Comments to CSV ----------
def save_video_comments_to_csv(video_id: str) -> str:
    comments = []
    results = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText'
    ).execute()

    while results:
        for item in results['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            username = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            comments.append([username, comment])
        if 'nextPageToken' in results:
            results = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                textFormat='plainText',
                pageToken=results['nextPageToken']
            ).execute()
        else:
            break

    filename = f"{video_id}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Username', 'Comment'])
        writer.writerows(comments)

    return filename

# ---------- Get Video Stats ----------
def get_video_stats(video_id: str) -> dict:
    try:
        response = youtube.videos().list(
            part='statistics',
            id=video_id
        ).execute()
        return response['items'][0]['statistics']
    except HttpError as error:
        print(f'Error fetching video stats: {error}')
        return {}

# ---------- Get Channel Info ----------
def get_channel_info(youtube, channel_id: str) -> dict:
    try:
        response = youtube.channels().list(
            part='snippet,statistics,brandingSettings',
            id=channel_id
        ).execute()

        info = response['items'][0]
        snippet = info['snippet']
        stats = info['statistics']

        return {
            'channel_title': snippet['title'],
            'video_count': stats['videoCount'],
            'channel_logo_url': snippet['thumbnails']['high']['url'],
            'channel_created_date': snippet['publishedAt'],
            'subscriber_count': stats['subscriberCount'],
            'channel_description': snippet['description']
        }

    except HttpError as error:
        print(f'Error fetching channel info: {error}')
        return {}
