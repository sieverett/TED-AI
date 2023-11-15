import streamlit as st
import pandas as pd
from moviepy.editor import *
from streamlit.logger import get_logger
import os
import sys

# sys.path.append('/workspaces/hello/scripts')

from utils import (build_persona, clone_voice, create_audio_from_clone, capitalize_names)

LOGGER = get_logger(__name__)

LOGGER.info(os.getcwd())
cloned_path='' # global variable for cloned voice path

def run():
    # Display the logo and the title

    st.set_page_config(
        page_title="SelfActualize.AI",
        page_icon="sa_small.png",
        layout="wide")
     
    st.title("TED Talks!")

    # Read CSV file
    df = pd.read_csv("TED_playlist_info.csv")  # Replace with your CSV file path
    # Extract names for the dropdown
    names = capitalize_names(df['presenter'].tolist())

    names = [n for n in names if ' And ' not in n]

    col1,col2=st.columns([2,4])
    
    # Create a dropdown menu in the sidebar
    with col1:
        selected_name = st.selectbox("Select a TED Presenter", names)


    # Button to extract and download audio
    selected_name_lower=selected_name.lower()
    video_link=df[df.presenter==selected_name_lower].link.values[0]
    if st.button('Click to Build Persona'):
        with st.spinner('Wait for it...'):
            segments_path=build_persona(selected_name_lower,video_link)
            description=f'{selected_name} is a TED speaker and has a lot of views on YouTube.'
            clone_voice(selected_name_lower,description,segments_path)
        st.success(f"{selected_name}'s voice clone complete!")

    # display video
    link_dict = {k: v for k, v in zip(df.presenter, df.link)}
    
    if selected_name_lower:
        video_link = link_dict[selected_name_lower]
        st.video(video_link)


if __name__ == "__main__":
    run()