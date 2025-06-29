import streamlit as st
import os
from Senti import extract_video_id, analyze_sentiment, bar_chart, plot_sentiment
from YoutubeCommentScrapper import (
    save_video_comments_to_csv,
    get_channel_info,
    youtube,
    get_channel_id,
    get_video_stats,
)

# ---------- Configuration ----------
st.set_page_config(
    page_title='YouTube Comment Analyzer - Ayush Sharma',
    page_icon='📺',
    layout="wide",
    initial_sidebar_state='expanded'
)

# ---------- Hide Streamlit Branding ----------
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.css-1d391kg {padding-top: 1rem;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.image("LOGO.png", width=200)
st.sidebar.title("🎯 YouTube Sentiment Analyzer")
st.sidebar.markdown("Analyze public video comments using NLP.")
youtube_link = st.sidebar.text_input("📥 Enter YouTube Video Link")

directory_path = os.getcwd()

def delete_non_matching_csv_files(directory_path, video_id):
    for file_name in os.listdir(directory_path):
        if not file_name.endswith('.csv'):
            continue
        if file_name == f'{video_id}.csv':
            continue
        os.remove(os.path.join(directory_path, file_name))

# ---------- Main App ----------
if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        channel_id = get_channel_id(video_id)

        st.sidebar.success(f"✅ Video ID: {video_id}")
        csv_file = save_video_comments_to_csv(video_id)
        delete_non_matching_csv_files(directory_path, video_id)
        st.sidebar.success("✅ Comments Saved")
        st.sidebar.download_button(
            label="⬇️ Download Comments CSV",
            data=open(csv_file, 'rb').read(),
            file_name=os.path.basename(csv_file),
            mime="text/csv"
        )

        # ---------- Channel Info ----------
        channel_info = get_channel_info(youtube, channel_id)
        st.markdown("## 📺 Channel Information")

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(channel_info['channel_logo_url'], width=200)
        with col2:
            st.subheader("Channel Name")
            st.title(channel_info['channel_title'])
            st.write(f"📅 Created On: **{channel_info['channel_created_date'][:10]}**")
            st.write(f"📈 Total Videos: **{channel_info['video_count']}**")
            st.write(f"👥 Subscribers: **{channel_info['subscriber_count']}**")

        st.markdown("---")

        # ---------- Video Statistics ----------
        stats = get_video_stats(video_id)
        st.markdown("## 📊 Video Statistics")
        col3, col4, col5 = st.columns(3)
        with col3:
            st.metric(label="👀 Total Views", value=stats["viewCount"])
        with col4:
            st.metric(label="👍 Likes", value=stats["likeCount"])
        with col5:
            st.metric(label="💬 Comments", value=stats["commentCount"])

        # ---------- Video Preview ----------
        st.markdown("---")
        st.markdown("## 🎬 Video Preview")
        st.video(youtube_link)

        # ---------- Sentiment Analysis ----------
        st.markdown("---")
        st.markdown("## 🧠 Sentiment Analysis Summary")

        results = analyze_sentiment(csv_file)
        col6, col7, col8 = st.columns(3)
        with col6:
            st.metric(label="😊 Positive", value=results['num_positive'])
        with col7:
            st.metric(label="😐 Neutral", value=results['num_neutral'])
        with col8:
            st.metric(label="😠 Negative", value=results['num_negative'])

        bar_chart(csv_file)
        plot_sentiment(csv_file)

        # ---------- Channel Description ----------
        st.markdown("---")
        st.markdown("## 📝 Channel Description")
        st.info(channel_info['channel_description'])

    else:
        st.error("⚠️ Invalid YouTube Link. Please enter a valid link.")
else:
    st.info("ℹ️ Please enter a public YouTube video link in the sidebar.")
