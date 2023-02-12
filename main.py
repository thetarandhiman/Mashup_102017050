import urllib.request
import re
from pytube import YouTube
import os
import youtube_dl 
from youtube_search import YoutubeSearch  
import subprocess   
import moviepy.editor as mp 
import moviepy.video.io.ffmpeg_tools as ffmpeg_tools 
from moviepy.editor import *
import sys
import streamlit as st
import zipfile
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
form = st.form(key='my_form')

name = form.text_input(label='Enter singer name') 
output_file = form.text_input(label='Enter output file name')
num_videos =  form.text_input(label='Enter number of videos')
audio_duration = form.text_input(label='Enter cut duration in seconds')
email = form.text_input(label='Enter your email-id')
submit_button = form.form_submit_button(label='Submit')

PASSWORD = st.secrets["TARANPREET"] # your password

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

    # Call zipAudio function
    zipAudio(output_file)

''' Zip the audio file '''
def zipAudio(outputfile):
    if not os.path.exists("audios"):
        os.mkdir("audios")
    zip_file = "audios/" + output_file + ".zip"
    with ZipFile(zip_file, 'w') as zipObj:
        zipObj.write(output_file)
    print("Audio file zipped.")

    # Call sendEmail function
    sendEmail(email, output_file)

'''Call mashup function'''
# mashup()

def sendEmail(email, result_file) : 
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "tdhiman_be20@thapar.edu"  
    receiver_email = email  # Enter receiver address

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Your Mashup Audio File!"

    # Add body to email
    message.attach(MIMEText("Your mashup has been created. Please find the attached zip file.", "plain"))

    # Open PDF file in bynary
    zip_file = "audios/" + output_file + ".zip"
    
    part = MIMEBase('application', "octet-stream")
    part.set_payload( open(zip_file,"rb").read() )
    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)
    
    # Add header with pdf name
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={output_file+'.zip'}",
    )
    
    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, PASSWORD)
        server.sendmail(sender_email, receiver_email, text)

if submit_button:
    # Check if all the fields are filled
    if name == '' or output_file == '' or num_videos == '' or cut_duration == '' or email == '':
        st.warning('Please enter all the fields!')
    # Check for validity of inputs
    elif not name.isalpha():
        st.warning('Please enter a valid name!')
    elif not num_videos.isdigit():
        st.warning('Please enter a valid number of videos!')
    elif not cut_duration.isdigit():
        st.warning('Please enter a valid duration!')
    elif not email.endswith('@gmail.com'):
        st.warning('Please enter a valid email!')
    else:
        st.success('Mashup created successfully!')
        st.balloons() # Show balloons on success
        st.write('Please check your email for the audio file.')
        # Call main function
        mashup(name, output_file, num_videos, cut_duration, email)