"""

    This script is meant to run as a cronjob or scheduled task to gradually download large numbers of YouTube videos
    over a long time period. Change the path variables to match how and where you want videos to be downloaded.
    
"""

print("Starting script")

# Imported required modules
from collections import namedtuple
import datetime
import os
import random
# import requests
import subprocess
import sys
from urllib.parse import urljoin

time = datetime.datetime.now()
print(f"The time is {time}")

# Defining static variables
channellist = "/mnt/S_Drive/yt-dlp/channellist" # The file that contains the list of channels to download
loggingdirectory = "/mnt/S_Drive/yt-dlp/logging" # Where the logs will be stored 
downloaddirectory = "/mnt/S_Drive/yt-dlp/" # Where the videos will be downloaded to
ytbinary = "/usr/bin/yt-dlp" # Where the yt-dlp binary is stored

# Defining functions
print("Defining internal functions")
def selectrandomchannel(channels):
    print("Selecting a random channel to work on")
    randomchannel = random.choice(channels)
    print(f"Selected working channel: {randomchannel.name}")
    return(randomchannel)

def fetchvideolist(channel):
    print(f"Fetching videos from {channel.name}")
    getcommand = f"yt-dlp --skip-download --get-id --get-title --flat-playlist '{channel.url}'"
    videos = subprocess.run(getcommand, shell=True, capture_output=True, text=True)
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
                print(f"{video} is a title")
                iftitle = video
            else:
                print(f"{video} is an extension, creating entry with title")
                extension = f"watch?v={video}"
                ifurl = urljoin(baseurl, extension)
                result = ytvideo(iftitle, ifurl)
                print(f"Appending: {result.title} / {result.url}")
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
    channel = ytchannel(rawchannel.replace("https://www.youtube.com/@", "").replace("/videos", ""), rawchannel)
    print(f"Appending channel object == {channel.name} / {channel.url}")
    channels.append(channel)

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
        os.mkdir(f"{downloaddirectory}{channel.name}")
    else:
        print(f"{channel.name} folder already exists in directory, nothing to do")

# This while loop ensures that a video will always be chosen
randomvideo = None
while randomvideo == None:
    # First check if there are any channels to work with
    if len(channels) == 0:
        print("The channel list is empty, there are no videos from any channel to download")
        break
    else:
        print("The channel list is not empty, continuing")
    
    # Pick a random channel and remove it from the channel list
    selectedchannel = selectrandomchannel(channels)
    channels.remove(selectedchannel)

    # Fetch all the videos in the channel
    videolist = fetchvideolist(selectedchannel)

    # Get list of videos already downloaded
    print("Fetching all the videos in the channel folder")
    existingvideos = os.listdir(f"/mnt/S_Drive/yt-dlp/{selectedchannel.name}")

    # Select a random video
    randomvideo = selectrandomvideo(existingvideos, videolist)

# Finishing up and downloading
print(f"Downloading {randomvideo.title}")
print(f"Command: yt-dlp -o '/mnt/S_Drive/yt-dlp/{selectedchannel.name}/{randomvideo.title}.%(ext)s' '{randomvideo.url}'")
dlcommand = f"yt-dlp -o '/mnt/S_Drive/yt-dlp/{selectedchannel.name}/{randomvideo.title}.%(ext)s' '{randomvideo.url}'"
subprocess.run(dlcommand, shell=True, capture_output=True, text=True)
