"""

    This script is meant to run as a cronjob or scheduled task to gradually download large numbers of YouTube videos
    over a long time period. Change the path variables to match how and where you want videos to be downloaded.
    
"""

# Imported required modules
from collections import namedtuple
import datetime
from dotenv import load_dotenv
import os
import random
import socket
import subprocess
import sys
from urllib.parse import urljoin

# Checking to see if the .env file exists
envtest = os.path.exists(f"{os.path.dirname(os.path.abspath(__file__))}/.env")
if envtest == False:
    sys.exit(1)

# Defining static variables
load_dotenv()
channellist = os.getenv("CHANNELLIST")
loggingdirectory = os.getenv("LOGDIRECTORY")
downloaddirectory = os.getenv("DLDIRECTORY")
ytbinary = os.getenv("BINARY")

time = datetime.datetime.now()

# Setting up log file path with the current date
logname = time.strftime("%Y-%m-%d_%H-%M-%S.log")
logpath = os.path.join(loggingdirectory, logname)

# Redirecting print output to the log file
logfile = open(logpath, "a")
sys.stdout = logfile

# Making sure the directories have an ending slash
if loggingdirectory[-1] != "/":
    loggingdirectory += "/"

if downloaddirectory[-1] != "/":
    downloaddirectory += "/"

# Outputting environment to log
print("Starting log")
print(f"Hostname == {socket.gethostname()}")
print(f"Time == {time}")
print(f"channellist == {channellist}")
print(f"loggingdirectory == {loggingdirectory}")
print(f"downloaddirectory == {downloaddirectory}")
print(f"ytbinary == {ytbinary}")

# Defining functions
print("Defining internal functions")
def selectrandomchannel(channels):
    print("Selecting a random channel to work on")
    randomchannel = random.choice(channels)
    print(f"Selected working channel == {randomchannel.name}")
    return(randomchannel)

def fetchvideolist(channel):
    print(f"Fetching videos from {channel.name}")
    getcommand = f"yt-dlp --skip-download --get-id --get-title --flat-playlist '{channel.url}'"
    try:
        videos = subprocess.run(getcommand, shell=True, capture_output=True, text=True)
    except:
        print("Something went wrong when fetching the channel video list")
        sys.exit(1)
    
    class ytvideo:
        def __init__(self, title, url):
            self.title = title
            self.url = url
    print("Organizing the videos into a useful format")
    results = []
    if videos.returncode == 0:
        count = 1
        baseurl = "https://youtube.com"
        for video in videos.stdout.splitlines():

            if count % 2 != 0:
                # print(f"{video} is a title")
                iftitle = video
            else:
                # print(f"{video} is an extension, creating entry with title")
                extension = f"watch?v={video}"
                ifurl = urljoin(baseurl, extension)
                result = ytvideo(iftitle, ifurl)
                # print(f"Appending: {result.title} / {result.url}")
                results.append(result)
            count += 1
    return results

def selectrandomvideo(existingvideos, videolist):
    # Select a video 
    print("Comparing the videos in the channel with the videos already downloaded")
    if not videolist or set(existingvideos) == set(video.title for video in videolist):
        print("All videos in the channel have already been downloaded")
        return None
    else:
        while videolist:
            index = random.randint(0, len(videolist) - 1)
            selectvideo = videolist[index]
            if selectvideo.title in existingvideos:
                videolist.pop(index)
            else:
                result = selectvideo
                break  # Break out of the loop once a video is selected
        print(f"Selected {result.title} to download")
        return result  # Return the selected video

# Verifying the environment
cmdtest = os.path.exists(ytbinary)
dirtest = os.path.exists(downloaddirectory)
listtest = os.path.exists(channellist)
logtest = os.path.exists(loggingdirectory)
if cmdtest == False or dirtest == False or listtest == False or logtest == False:
    print("Something went wrong when verifying the environment")
    # logfile.close()
    sys.exit(1)
else:
    print("Environment looks good, proceeding")

# Fetches the contents of the channel list file
print("Importing channel list")
with open(channellist, "r") as file:
    contents = file.read()
rawchannels = contents.splitlines()
channels = []
class ytchannel:
    def __init__(self, name, url):
        self.name = name
        self.url = url
for rawchannel in rawchannels:
    channel = ytchannel(rawchannel.replace("https://www.youtube.com/@", "").replace("/podcasts", "").replace("/shorts", "").replace("/streams", "").replace("/videos", ""), rawchannel)
    print(f"Appending channel object == {channel.name} / {channel.url}")
    channels.append(channel)

# First check if there are any channels to work with
if len(channels) == 0:
    print("The channel list is empty, there are no videos from any channel to download")
    # logfile.close()
    sys.exit(0)
else:
    print("The channel list is not empty, continuing")

# Get the contents of the directory minus the channel list and logging folder
print(f"Generating list of channel folders from {downloaddirectory}")
directorylist = os.listdir(downloaddirectory)
def filterfunc(item):
    return item not in ["channellist", "logging"]
existingdirectories = list(filter(filterfunc, directorylist))
print(f"Existing directories in the download folder == {existingdirectories}")

# Create new directories for channels that don't have one
print("Creating new channel folders")
for channel in channels:
    if channel.name not in existingdirectories:
        print(f"Creating directory for {channel.name}")
        try:
            os.mkdir(f"{downloaddirectory}{channel.name}")
        except:
            print("Something went wrong when creating new directories, there may be an issue with permissions")
            # logfile.close()
            sys.exit(1)
    else:
        print(f"{channel.name} folder already exists in directory, nothing to do")

# This while loop ensures that a video will always be chosen
randomvideo = None
while randomvideo == None:
    if not channels:
        print("There are no more channels to download from, exiting")
        print("Script complete")
        # logfile.close()
        sys.exit(0)
    else:
        print("There are channels still in the list to download from")
    
    # Pick a random channel and remove it from the channel list
    selectedchannel = selectrandomchannel(channels)
    channels.remove(selectedchannel)

    # Fetch all the videos in the channel
    videolist = fetchvideolist(selectedchannel)

    # Get list of videos already downloaded
    print("Fetching all the videos in the channel folder")
    existingvideos = []
    existingfiles = os.listdir(f"{downloaddirectory}{selectedchannel.name}")
    for file in existingfiles:
        existingvideos.append(os.path.splitext(file))

    # Select a random video
    randomvideo = selectrandomvideo(existingvideos, videolist)

# Finishing up and downloading
print(f"Downloading {randomvideo.title}")
print(f"Command == yt-dlp -o '{downloaddirectory}{selectedchannel.name}/{randomvideo.title}.%(ext)s' '{randomvideo.url}'")
dlcommand = f"yt-dlp -o '{downloaddirectory}{selectedchannel.name}/{randomvideo.title}.%(ext)s' '{randomvideo.url}'"
try:
    subprocess.run(dlcommand, shell=True, capture_output=True, text=True)
except:
    print("Something went wrong when attempting to download the video")

# Finishing up
# logfile.close()
print("Script complete")
