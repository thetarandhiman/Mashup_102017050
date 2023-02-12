import sys 
import os 
import youtube_dl 
from youtube_search import YoutubeSearch  
import urllib.request       
from pytube import YouTube  
import subprocess   
import moviepy.editor as mp 
import moviepy.video.io.ffmpeg_tools as ffmpeg_tools 
from moviepy.editor import * 
import shutil 

'''mashup function'''
def mashup():
    if len(sys.argv) != 5:
        print("Wrong number of arguments.")
        print("Usages: python <program.py> <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        print("Example: python 101556.py “Sharry Maan” 20 20 101556-output.mp3")
        exit(0)
    
    # Check if the number of videos is an integer
    try:
        int(sys.argv[2])
    except ValueError:
        print("Number of videos should be an integer.")
        exit(0)

    # Check if the audio duration is an integer
    try:
        int(sys.argv[3])
    except ValueError:
        print("Audio duration should be an integer.")
        exit(0)

    # Check if the output file name is mp3
    if sys.argv[4][-4:] != ".mp3":
        print("Output file name should be mp3.")
        exit(0)

    # Get the arguments
    singer = sys.argv[1]
    num_videos = sys.argv[2]
    audio_duration = sys.argv[3]
    output_file = sys.argv[4]
    # Call search video function
    search_video(singer, num_videos, audio_duration, output_file)

'''search_video function'''
def search_video(singer, num_videos, audio_duration, output_file):
    # Search videos using Youtube API
    results = YoutubeSearch(singer, max_results=int(num_videos)).to_dict() 
    links = list()
    for i in range(int(num_videos)):
        links.append(results[i])
    if not links:
        print("No videos found for the singer.")
        exit(0)
    if len(links) < 10:
        print("Number of videos should be greater than 10.")
        exit(0)
            
    # Call download_video function
    download_video(links, singer, num_videos, audio_duration, output_file)

'''download_video function'''
def download_video(links, singer, num_videos, audio_duration, output_file):
    if not os.path.exists(singer):
        os.mkdir(singer)
    # Download videos using youtube_dl
    for link in links:
        yt = YouTube(link['url_suffix'])
        # if yt.length < 600 and yt.length > 20:
        yt.streams.filter().first().download(singer) 
        print("Video {} downloaded.".format(link['url_suffix']))
    # Call convert_video function
    convert_video(singer, num_videos, audio_duration, output_file)

'''convert_video function'''
def convert_video(singer, num_videos, audio_duration, output_file):
    if not os.path.exists(singer+"_audio"):
        os.mkdir(singer+"_audio")
    # Convert all the videos to audio
    for filename in os.listdir(singer):
        clip = mp.VideoFileClip(os.path.join(singer, filename))
        clip.audio.write_audiofile(os.path.join(singer+"_audio", filename[:-4]+".mp3"))
        print("Video {} converted to audio.".format(filename))    
    # Call cut_audio function
    cut_audio(singer, num_videos, audio_duration, output_file)

'''Cut_audio function'''
def cut_audio(singer, num_videos, audio_duration, output_file):
    if not os.path.exists(singer+"_audio_cut"):
        os.mkdir(singer+"_audio_cut")
    # Cut audio files
    for filename in os.listdir(singer+"_audio"):
        clip = mp.AudioFileClip(os.path.join(singer+"_audio", filename))
        clip = clip.subclip(0, int(audio_duration))
        clip.write_audiofile(os.path.join(singer+"_audio_cut", filename))
        print("Audio {} cut.".format(filename))

    # Call merge_audio function
    merge_audio(singer, num_videos, audio_duration, output_file)


'''Merge_audio function'''
def merge_audio(singer, num_videos, audio_duration, output_file):
    if not os.path.exists(output_file):
        open(output_file, 'w').close()
    # Merge audio files
    audio_files = []
    for filename in os.listdir(singer+"_audio_cut"):
        audio_files.append(os.path.join(singer+"_audio_cut", filename))
    final_clip = concatenate_audioclips([AudioFileClip(f) for f in audio_files])
    final_clip.write_audiofile(output_file)
    print("Audio files merged.")

'''Call mashup function'''
mashup()