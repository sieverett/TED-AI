import streamlit as st
import pandas as pd
from moviepy.editor import *

# Display the logo and the title
col1, col2 = st.columns([1, 3])
with col1:
    st.image("TED_logo.jpg", width=100)  # Adjust width as needed
with col2:
    st.title("My Video App")

def extract_audio(video_url, output_filename):
    # Load the video file
    video = VideoFileClip(video_url)
    
    # Extract audio
    audio = video.audio

    # Save the audio file
    audio.write_audiofile(output_filename)
    
    # Close the video file
    video.close()
    return output_filename

# Read CSV file
df = pd.read_csv("path_to_your_csv_file.csv")  # Replace with your CSV file path

# Extract names for the dropdown
names = df['Name'].tolist()

# Create a dropdown menu in the sidebar
selected_name = st.sidebar.selectbox("Select a Name", names)

# Display the selected name and the video
if selected_name:
    video_link = df[df['Name'] == selected_name]['VideoLink'].iloc[0]
    
    st.write(f"You selected: {selected_name}")
    st.video(video_link)

    # Button to extract and download audio
    if st.button('Extract Audio'):
        output_filename = f"{selected_name}_audio.mp3"
        file_path = extract_audio(video_link, output_filename)
        st.success(f"Audio extracted and saved as {output_filename}")

        # Download button
        with open(file_path, "rb") as file:
            st.download_button(
                label="Download Audio",
                data=file,
                file_name=output_filename,
                mime="audio/mpeg"
            )

# Text input for user's text (up to 100 words)
user_input = st.text_area("Enter your text (up to 100 words)", max_chars=1000)

# Word count check
word_count = len(user_input.split())
if word_count > 100:
    st.warning("Your text exceeds 100 words. Please shorten it.")