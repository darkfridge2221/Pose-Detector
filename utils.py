from pytube import YouTube

#Function to download video from YouTube and return the file path
def download_youtube_video(link):
    yt = YouTube(link)
    video = yt.streams.get_highest_resolution()
    video_path = video.download(output_path=".")
    return video_path
