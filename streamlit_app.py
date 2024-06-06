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


def cache_storage(json, index, channel_df):
    data = {
        'S.NO': [index],
        'Channel ID': [json['items'][0]['snippet']['channelId']],
        'Channel Name': [json['items'][0]['snippet']['channelTitle']],
        'Channel description': [json['items'][0]['snippet']['description']]
    }
    temp_df = pd.DataFrame(data)
    if len(temp_df) > 0:
        df = pd.merge(channel_df, temp_df)
    else:
        df = pd.concat([channel_df, temp_df]).sort_values(by=['S.NO'], ascending=[False])
    st.write(f'dataframe : {df}')
    index += 1


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
index = 0
channel_df = pd.DataFrame(columns=['S.NO', 'Channel ID', 'Channel Name', 'Channel description'])

# Tabs for app layout
tabs = st.tabs(['➕ Add New Channel', '📋 Collected Channels List', '📊 Channel Performance Analytics'])

with tabs[0]:
    with st.form('addition'):
        channel_name = st.text_input('Channel Name')
        submit = st.form_submit_button('Submit')

        if submit:
            if channel_name:
                get_channeldetails = get_youtube_data(channel_name)
                cache_storage(get_channeldetails, index, channel_df)
                st.write(f'channel details : {channel_name}')
            else:
                st.write("Channel Name: Not provided")

with tabs[1]:
    st.write('Collected Channels List')
    st.dataframe(channel_df)

# You can add code for 'Channel Performance Analytics' in tabs[2] as needed
