import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
from googleapiclient.discovery import build

api_key = 'AIzaSyDr8ByPJOb0Q5I3ZLB66-PWjW-FSR3o2oU'
youtube = build('youtube', 'v3', developerKey=api_key)

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

# Generate data
## Set seed for reproducibility
np.random.seed(42)

## Function to get channel details
def get_youtube_data(query, max_results=10):
    request = youtube.search().list(
        q=query,
        part='snippet',
        maxResults=max_results
    )
    response = request.execute()
    return response

# Initialize index and dataframe outside the function
if 'index' not in st.session_state:
    st.session_state.index = 0

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=['S.NO', 'Channel ID', 'Channel Name', 'Channel Description'])

def add_value_to_dataframe(df, index, channel_id, channel_name, channel_description):
    data = {
        'S.NO': [index],
        'Channel ID': [channel_id],
        'Channel Name': [channel_name],
        'Channel Description': [channel_description]
    }
    new_df = pd.DataFrame(data)
    df = pd.concat([df, new_df], ignore_index=True).sort_values(by=['S.NO'], ascending=[False])
    return df

def cache_storage(json, index, df):
    df = add_value_to_dataframe(
        df,
        index,
        json['items'][0]['snippet']['channelId'],
        json['items'][0]['snippet']['channelTitle'],
        json['items'][0]['snippet']['description']
    )

    # Update the session state
    st.session_state.df = df
    st.session_state.index += 1

# Tabs for app layout
tabs = st.tabs(['➕ Add New Channel', '📋 Collected Channels List', '📊 Channel Performance Analytics'])

with tabs[0]:
    wit
