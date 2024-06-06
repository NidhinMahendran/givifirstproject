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
index = 0


## Function to get channel details
def get_youtube_data(query, max_results=10):
    request = youtube.search().list(
        q=query,
        part='snippet',
        maxResults=max_results
    )
    response = request.execute()
    return response


def cache_storage(json):
    data = {
            'S.NO': index,
            'Channel ID': json['items']['snippet']['channelId'],
            'Channel Name': json['items']['snippet']['channelTitle'],
            'Channel description': json['items']['snippet']['description']
        }
    temp_df = pd.DataFrame(data)
    df = temp_df.sort_values(by=['S.NO'], ascending=[False, False])
    st.write(f'dataframe : {df}')
    index=+1


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
                st.write(f'channel details : {channel_name}')
            
            else:
                st.write("Channel Name: Not provided")

