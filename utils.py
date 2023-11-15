import os
import streamlit as st
from pathlib import Path
from datetime import datetime
from youtubesearchpython.__future__ import VideosSearch
from yt_dlp import YoutubeDL
from pydub import AudioSegment
from mutagen.mp3 import MP3
from tqdm import tqdm
from dotenv import load_dotenv
from elevenlabs import clone, Voice, voices
from elevenlabs import generate, play, save, set_api_key
from youtubesearchpython import *
from tqdm import tqdm
import pandas as pd
import argparse
from typing import List
import csv
import json
from argparse import ArgumentParser
from pathlib import Path
from pydub import AudioSegment 

# pip install youtube-search-python
from youtubesearchpython import VideosSearch

# pip install youtube-transcript-api
from youtube_transcript_api import YouTubeTranscriptApi

def capitalize_names(names):
    names=[" ".join([i.capitalize() for i in g.split(" ")]) for g in names if g!='na']
    return names

def get_youtube_video_ids(keyword: str, limit: int = 10) -> List[str]:
    """
    Returns list of video ids we find for the given 'keyword'
    """
    video_search = VideosSearch(keyword, limit=limit)
    results = video_search.result()['result']
    return [r['id'] for r in results]


def get_youtube_video_transcript(video_id: str) -> str:
    """"
    Returns transcript of the given 'video_id'
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, languages=['en-US', 'en']
        )
        utterances = [p['text'] for p in transcript]
        return ' '.join(utterances)

    except Exception as e:
        pass


def save_transcripts(transcripts: List[str], keyword: str, path: Path):
    """
    Stores locally in file the transcripts with associated keyword
    """
    output = [{'keyword': keyword, 'text': t} for t in transcripts if t is not None]

    # check if path points to a csv or a json file
    if path.suffix == '.csv':
        # save as csv
        keys = output[0].keys()
        with open(path, 'w', newline='')  as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(output)

    else:
        # save as json
        with open(path, 'w') as output_file:
            json.dump(output, output_file)


def make_file_structure(coach,root_dir='.') -> None:
    global transcripts_path, audio_path, segments_path, coach_dir, cloned_path
    coach_dir = f'{root_dir}/personas/{coach}'
    os.makedirs(coach_dir, exist_ok=True)
    # for transcripts
    transcripts_path = coach_dir + '/transcripts/'
    os.makedirs(transcripts_path, exist_ok=True)
    # for audio 
    audio_path = coach_dir + '/audio/'
    os.makedirs(audio_path, exist_ok=True)
    # for audio segments
    segments_path= coach_dir+'/audio/segments'
    os.makedirs(segments_path, exist_ok=True)
    # for cloned speech audio
    cloned_path = coach_dir + '/cloned/'
    os.makedirs(cloned_path, exist_ok=True)

async def fetch_links(coach,limit = 3):
    videosSearch = VideosSearch('ONLY ' + coach + ' statement', limit = limit)
    videosResult = await videosSearch.next()
    links = [i['link'] for i in videosResult['result']]
    return links

def get_youtube_video_transcripts(coach, links, transcripts_path):
    # video_ids=get_youtube_video_ids(coach+' gives advice and coaching', limit = 10)
    video_ids= [i.split('v=')[1] for i in links]
    transcripts = [get_youtube_video_transcript(id) for id in video_ids]
    save_transcripts(transcripts, coach, Path(transcripts_path+f'transcripts.txt'))

def download_transcript(coach, link):
    # remove playlist links
    video_id=link.split('&list=')[0].split('v=')[1]
    transcript=get_youtube_video_transcript(video_id)
    save_transcripts(transcript, coach, Path(transcripts_path+f'transcripts.txt'))

def download_audio(link):
    """
    link: a youtube url
    """
    print('full link:',link)
    print('shortened link:',link.split('&list=')[0])
    link=link.split('&list=')[0]
    datetime_str = datetime.now().strftime("%Y%m%d")
    mp3_file = f"audio_sample_{datetime_str}"
    ydl_opts = { 
    'outtmpl': f'{coach_dir}/audio/{mp3_file}',
    'format': 'bestaudio/best',
    'map':'0:a',
    'no-playlist': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '1200',
    }],
    }
    YoutubeDL(ydl_opts).download([link])

def extract_samples(n_samples = 3, sample_length = 45):
    """
    given a path to an audio file, extract n_samples of length sample_length
    """
    audio_file_paths=[audio_path+i for i in os.listdir(audio_path) if '.mp3' in i]
    for sample_number,audio_file_path in enumerate(audio_file_paths):
        print(audio_file_path)
        # Load the mp3 file
        audio = MP3(audio_file_path)
        # Get the length in seconds
        length_in_milliseconds = audio.info.length * 1000
        print(f"Length of the audio file in seconds: {length_in_milliseconds}")
        # Load the audio file with pydub
        audio = AudioSegment.from_mp3(audio_file_path)
        increment=sample_length*1000 # seconds to milliseconds
        start_time = length_in_milliseconds / 2
        l=[]
        for i in range(n_samples):
            end_time = start_time+increment
            l.append((start_time,end_time))
            start_time=end_time
        for i,(start_time,end_time) in tqdm(enumerate(l)):
            # Extract the segment
            segment = audio[start_time:end_time]
            # Save the segment
            segment.export(f"{segments_path}/sample_{sample_number}_{i}.mp3", format="mp3")
    return segments_path

# %%
# run results
async def build_data_store(coach):
    make_file_structure(coach)
    links = await fetch_links(coach)
    get_youtube_video_transcripts(coach, links, transcripts_path)
    download_audio(links)
    extract_samples()

def build_persona(presenter,link):
    make_file_structure(presenter,root_dir='TED')
    download_transcript(presenter, link)
    download_audio(link)
    segments_path=extract_samples(n_samples = 1, sample_length = 300)
    return segments_path

def build_top_n_ted_personas(top_n=3):
    TED_sub=pd.DataFrame(pd.read_csv('TED/TED_playlist_info.csv'))
    for i in TED_sub.head(top_n)[['presenter','link']].iterrows():
        presenter=i[1]['presenter']
        link=[i[1]['link'].split('&list')[0]]
        print('Building persona data for', presenter)
        build_persona(presenter,link)

def list_personas(list_n):
    df=pd.read_csv('TED/TED_playlist_text.csv')
    dict_={p:l for p,l in zip(df.presenter[:list_n],df.link[:list_n])}
    return dict_

def list_cloned_voices():
    set_api_key(st.secrets["ELEVENLABS_API_KEY"])
    result=voices()
    voice_dict={i.name:i.voice_id for i in [v for v in result.voices] if i.category=='cloned'}
    return voice_dict

def clone_voice(presenter,description,segments_path):
    set_api_key(st.secrets["ELEVENLABS_API_KEY"])
    voice = clone(
      name = presenter,
      description=description,
      files = [f"{segments_path}/sample_0_0.mp3"]  
   )

def create_audio_from_clone(presenter,text,play_=False):
    voice_dict=list_cloned_voices()
    voice_id=voice_dict[presenter]
    v1=Voice.from_id(voice_id) # voice.voice_id
    audio=generate(text=text, voice=v1, model="eleven_turbo_v2")
    datetime_str = datetime.now().strftime("%Y%m%d")
    cloned_audio_save_path=f'TED/personas/{presenter}/cloned/audio_cloned_{datetime_str}.wav'
    save(audio,cloned_audio_save_path)
    if play_:
        play(audio)
    return cloned_audio_save_path

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--list_personas", help="List TED presenters? - True or False")
#     parser.add_argument("--list_cloned_voices", help="List cloned voices? - True or False")
#     parser.add_argument("--presenter", help="Name of TED presenter to clone - First and Last Name lower case")
#     parser.add_argument("--text", help="A sentence to be spoken by cloned voice")
#     args = parser.parse_args()

#     if args.list_personas=='True':
#         personas=list_personas(list_n=99)
#         [print(p) for p in personas.keys() if p!='na']
#         sys.exit()

#     if args.list_cloned_voices=='True':
#         list_cloned_voices()
#         sys.exit()

#     if args.presenter is None:
#         print('ERROR: Please enter a presenter name.')
#         sys.exit()
#     elif args.text is None:
#         print(f'ERROR: text needed.  Add some text for {args.presenter} to utter.')
#         sys.exit()
#     else:
#         presenter=args.presenter
#         personas=list_personas(list_n=20)
#         list_cloned_voices() # updates voice_dict
#         link=personas[presenter]
#         build_persona(presenter,link)
#         description=f'{presenter} is a TED speaker and has a lot of views on YouTube.'
#         clone_voice(presenter,description,segments_path)
#         create_audio_from_clone(presenter,args.text,play_=True)
