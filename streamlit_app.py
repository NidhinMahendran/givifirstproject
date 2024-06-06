import streamlit as st
import numpy as np
import pandas as pd
from googleapiclient.discovery import build

# API Key
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

# Initialize session state variables
if 'index' not in st.session_state:
    st.session_state.index = 1

if 'channel_df' not in st.session_state:
    st.session_state.channel_df = pd.DataFrame(columns=['Channel ID', 'Channel Name', 'Channel Description'])
    st.session_state.channel_df.insert(0,'S.NO')

if 'json_responses' not in st.session_state:
    st.session_state.json_responses = []

def cache_storage(json):
    try:
        data = {
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

# You can add code for 'Channel Performance Analytics' in tabs[2] as needed
