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

    col1, col2, col3 = st.columns([3, 1, 4])

    with col1:
        # Create a dropdown menu in the sidebar
        selected_name = st.selectbox("Select a TED Presenter", names)
        selected_name_lower=selected_name.lower()

    with col2:
        # Button to extract and download audio
        if st.button(f'Chat with {selected_name}'):
            with st.spinner('Wait for it...'):
                segments_path=build_persona(selected_name_lower,video_link)
                description=f'{selected_name} is a TED speaker and has a lot of views on YouTube.'
                clone_voice(selected_name_lower,description,segments_path)
            st.success('Done!')

    # Text input for user's text (up to 100 words)
    user_input = st.text_area("Enter your text (up to 100 words)", max_chars=1000)

    # Word count check
    word_count = len(user_input.split())
    if word_count > 100:
        st.warning("Your text exceeds 100 words. Please shorten it.")
    elif word_count > 0:
        # Download button
        output_filepath=create_audio_from_clone(selected_name_lower,user_input,play_=True)
        with open(output_filepath, "rb") as file:
            st.download_button(
                label="Download Audio",
                data=file,
                file_name="audio.mp3",
                mime="audio/mpeg"
                )

if __name__ == "__main__":
    run()