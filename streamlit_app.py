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


# Tabs for app layout
tabs = st.tabs(['➕ Add New Channel', '📋 Collected Channels List', '📊 Channel Performance Analytics'])

recent_ticket_number = int(max(st.session_state.df.ID).split('-')[1])

with tabs[0]:
    with st.form('addition'):
        channel_name = st.text_input('Channel Name')
        submit = st.form_submit_button('Submit')

    if submit:
        if channel_name:
            st.write(f"Channel Name: {channel_name}")
        else:
            st.write("Channel Name: Not provided")
            
        get_channeldetails = get_youtube_data(channel_name)
        
        print(f'channel details : {get_channeldetails}')
        
        today_date = datetime.now().strftime('%Y-%m-%d')
        df2 = pd.DataFrame([{'ID': f'TICKET-{recent_ticket_number+1}',
                            'channel_name': channel_name,
                            'Date Submitted': today_date
                            }])
        st.write('')
        st.dataframe(df2, use_container_width=True, hide_index=True)
        st.session_state.df = pd.concat([st.session_state.df, df2], axis=0)
        
with tabs[1]:
  with st.form('addition'):
    channel_name = st.text_input('Channel Name')


with tabs[2]:
  with st.form('addition'):
    channel_name = st.text_input('Channel Name')

