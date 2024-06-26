import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.exc import OperationalError
from datetime import datetime

# API Key
api_key = 'AIzaSyDr8ByPJOb0Q5I3ZLB66-PWjW-FSR3o2oU'
youtube = build('youtube', 'v3', developerKey=api_key)

Base = declarative_base()

class Channel(Base):
    __tablename__ = 'channel'
    channel_id = Column(String(255), primary_key=True)
    channel_name = Column(String(255))
    channel_type = Column(String(255))
    channel_views = Column(Integer)
    channel_description = Column(Text)
    channel_status = Column(String(255))
    playlists = relationship("Playlist", back_populates="channel")
    videos = relationship("Video", back_populates="channel")

class Playlist(Base):
    __tablename__ = 'playlist'
    playlist_id = Column(String(255), primary_key=True)
    channel_id = Column(String(255), ForeignKey('channel.channel_id'))
    playlist_name = Column(String(255))
    channel = relationship("Channel", back_populates="playlists")
    videos = relationship("Video", back_populates="playlist")

class Video(Base):
    __tablename__ = 'video'
    video_id = Column(String(255), primary_key=True)
    channel_id = Column(String(255), ForeignKey('channel.channel_id'))
    playlist_id = Column(String(255), ForeignKey('playlist.playlist_id'))
    video_name = Column(String(255))
    video_description = Column(Text)
    published_date = Column(DateTime(timezone=True))
    view_count = Column(Integer)
    like_count = Column(Integer)
    dislike_count = Column(Integer)
    favorite_count = Column(Integer)
    comment_count = Column(Integer)
    duration = Column(Integer)
    thumbnail = Column(String(255))
    caption_status = Column(String(255))
    channel = relationship("Channel", back_populates="videos")
    playlist = relationship("Playlist", back_populates="videos")
    comments = relationship("Comment", back_populates="video")

class Comment(Base):
    __tablename__ = 'comment'
    comment_id = Column(String(255), primary_key=True)
    video_id = Column(String(255), ForeignKey('video.video_id'))
    comment_text = Column(Text)
    comment_author = Column(String(255))
    comment_published_date = Column(DateTime(timezone=True))
    video = relationship("Video", back_populates="comments")

# Database connection
DATABASE_URL = "postgresql://user:password@localhost:5432/guvi_project"

def check_db_connection():
    try:
        engine = create_engine(DATABASE_URL)
        engine.connect()
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session
    except OperationalError as e:
        st.error(f"Database connection failed: {e}")
        return None

session = check_db_connection()
if not session:
    st.stop()

# Page title
st.set_page_config(page_title='YouTube Data Harvesting & Warehousing', page_icon='https://img.icons8.com/ios-filled/50/youtuber.png')
st.markdown(
    """
    <h1>
        <img src="https://img.icons8.com/ios-filled/50/youtuber.png" width="30" style="vertical-align: middle;"> 
        YouTube Data Harvesting & Warehousing
    </h1>
    """, 
    unsafe_allow_html=True
)

# Initialize session state variables
if 'index' not in st.session_state:
    st.session_state.index = 1

if 'channel_df' not in st.session_state:
    st.session_state.channel_df = pd.DataFrame(columns=['S.NO', 'Channel ID', 'Channel Name', 'Channel Description'])

if 'json_responses' not in st.session_state:
    st.session_state.json_responses = []

def cache_storage(json):
    try:
        for channel_id, channel_data in json.items():
            channel_name = channel_data['items'][0]['snippet']['channelTitle']
            channel_description = channel_data['items'][0]['snippet']['description']
            
            data = {
                'S.NO': [st.session_state.index],
                'Channel ID': [channel_id],
                'Channel Name': [channel_name],
                'Channel Description': [channel_description]
            }
            temp_df = pd.DataFrame(data)
            
            st.session_state.channel_df = pd.concat([st.session_state.channel_df, temp_df], ignore_index=True)
            
            response_dict = {
                str(channel_id): channel_data
            }
            
            st.session_state.json_responses.append(response_dict)
            st.session_state.index += 1
            
            # Add to SQL database
            new_channel = Channel(
                channel_id=channel_id,
                channel_name=channel_name,
                channel_description=channel_description,
                channel_type='Unknown',  # Assuming this field is not available in the API response
                channel_views=0,  # Assuming this field is not available in the API response
                channel_status='Active'  # Assuming a default status
            )
            session.add(new_channel)
            session.commit()

            # Store video details
            cache_video_storage(channel_data, channel_id)
        
    except (IndexError, KeyError) as e:
        st.error(f"Error processing the response: {e}")

def cache_video_storage(channel_data, channel_id):
    try:
        for item in channel_data['items']:
            video_id = item['id']['videoId']
            snippet = item['snippet']
            video_name = snippet['title']
            video_description = snippet['description']
            published_date = datetime.strptime(snippet['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
            thumbnail = snippet['thumbnails']['default']['url']

            # Add to SQL database
            new_video = Video(
                video_id=video_id,
                channel_id=channel_id,
                video_name=video_name,
                video_description=video_description,
                published_date=published_date,
                view_count=0,  # Assuming initial view count
                like_count=0,  # Assuming initial like count
                dislike_count=0,  # Assuming initial dislike count
                favorite_count=0,  # Assuming initial favorite count
                comment_count=0,  # Assuming initial comment count
                duration=0,  # Assuming initial duration
                thumbnail=thumbnail,
                caption_status='Unknown'  # Assuming initial caption status
            )
            session.add(new_video)
        session.commit()
    except (IndexError, KeyError) as e:
        st.error(f"Error processing the response: {e}")

def cache_comment_storage(video_id, comment_data):
    try:
        for item in comment_data:
            comment_id = item['id']
            comment_text = item['snippet']['textDisplay']
            comment_author = item['snippet']['authorDisplayName']
            comment_published_date = datetime.strptime(item['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')

            # Add to SQL database
            new_comment = Comment(
                comment_id=comment_id,
                video_id=video_id,
                comment_text=comment_text,
                comment_author=comment_author,
                comment_published_date=comment_published_date
            )
            session.add(new_comment)
        session.commit()
    except (IndexError, KeyError) as e:
        st.error(f"Error processing the response: {e}")

def get_youtube_data(query, max_results=10):
    request = youtube.search().list(
        q=query,
        part='snippet',
        maxResults=max_results
    )
    response = request.execute()
    return response

def get_video_comments(video_id, max_results=100):
    request = youtube.commentThreads().list(
        videoId=video_id,
        part='snippet',
        maxResults=max_results
    )
    response = request.execute()
    return response['items']

def fetch_channels():
    channels = session.query(Channel).all()
    return pd.DataFrame([(channel.channel_id, channel.channel_name, channel.channel_description) for channel in channels], 
                        columns=['Channel ID', 'Channel Name', 'Channel Description'])

def fetch_videos():
    videos = session.query(Video).all()
    return pd.DataFrame([(video.video_id, video.video_name, video.video_description, video.published_date, video.view_count, video.like_count, video.dislike_count, video.favorite_count, video.comment_count, video.duration, video.thumbnail, video.caption_status) for video in videos], 
                        columns=['Video ID', 'Video Name', 'Video Description', 'Published Date', 'View Count', 'Like Count', 'Dislike Count', 'Favorite Count', 'Comment Count', 'Duration', 'Thumbnail', 'Caption Status'])

def fetch_comments():
    comments = session.query(Comment).all()
    return pd.DataFrame([(comment.comment_id, comment.video_id, comment.comment_text, comment.comment_author, comment.comment_published_date) for comment in comments], 
                        columns=['Comment ID', 'Video ID', 'Comment Text', 'Comment Author', 'Comment Published Date'])

# Tabs for app layout
tabs = st.tabs(['➕ Add New Channel', '📋 Collected Channels List', '📊 Channel Performance Analytics'])

with tabs[0]:
    with st.form('addition'):
        channel_name = st.text_input('Channel Name')
        submit = st.form_submit_button('Submit')

        if submit:
            if channel_name:
                get_channeldetails = get_youtube_data(channel_name)                
                cache_storage(get_channeldetails)
                st.success(f'Channel "{channel_name}" added Successfully.')
            else:
                st.error("Channel Name: Not provided")

with tabs[1]:
    st.write('Collected Channels List')
    st.dataframe(st.session_state.channel_df)
    submit = st.button('Migrate to SQL')
    if submit:
        st.write("Migrating data to SQL...")
        for response in st.session_state.json_responses:
            for channel_id, json in response.items():
                for video in json['items']:
                    video_id = video['id']['videoId']
                    comments = get_video_comments(video_id)
                    cache_comment_storage(video_id, comments)
        st.success("Data migrated successfully.")

with tabs[2]:
    st.write('### Channel Details')
    channel_df = fetch_channels()
    st.dataframe(channel_df)

    st.write('### Video Details')
    video_df = fetch_videos()
    st.dataframe(video_df)

    st.write('### Comment Details')
    comment_df = fetch_comments()
    st.dataframe(comment_df)
