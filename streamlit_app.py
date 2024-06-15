import streamlit as st
import numpy as np
import pandas as pd
import psycopg2
from googleapiclient.discovery import build
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

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

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


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
        data = {
            'S.NO': [st.session_state.index],
            'Channel ID': [json['items'][0]['snippet']['channelId']],
            'Channel Name': [json['items'][0]['snippet']['channelTitle']],
            'Channel Description': [json['items'][0]['snippet']['description']]
        }
        temp_df = pd.DataFrame(data)
        
        st.session_state.channel_df = pd.concat([st.session_state.channel_df, temp_df], ignore_index=True)
        
        response_dict = {
            str(json['items'][0]['snippet']['channelId']): json
        }
        
        st.session_state.json_responses.append(response_dict)
        st.session_state.index += 1
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
                st.success(f'Channel details for "{channel_name}" added.')
            else:
                st.error("Channel Name: Not provided")

with tabs[1]:
    st.write('Collected Channels List')
    st.dataframe(st.session_state.channel_df)
    submit = st.button('Migrate to SQL')
    if submit:
        st.write(st.session_state.json_responses)
        
        