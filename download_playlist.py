from pytube import YouTube
from pytube import Playlist
import os
import moviepy.editor as mp
import re
import threading

class PlaylistDownloader:

    def __init__(self, playlist_url, output_dir="", threads=16):
        self.playlist = Playlist(playlist_url)
        self.videos_urls = []
        self.output_directory = output_dir
        self.jobs = []
        self.paths = []
        self.mp3_paths = []
        self.errors = []
        self.sema = threading.Semaphore(value=threads)

    def get_videos_url(self):
        for url in self.playlist:
            self.videos_urls.append(url)

    def get_videos_paths(self):
        for file in os.listdir(folder):
            if re.search('mp4', file):
                self.paths.append(os.path.join(folder, file))
                self.mp3_paths.append(os.path.join(folder, os.path.splitext(file)[0] + '.mp3'))

    def download_video(self, url):
        self.sema.acquire()
        print(f"Start downloading: {url}")
        try:
            YouTube(url).streams.filter(only_audio=True).first().download(self.output_directory)
            print(f"Done for: {url}")

        except:
            self.errors.append(url)
        self.sema.release()

    def change_mp4_to_mp3(self, mp4_path, mp3_path):
        self.sema.acquire()
        new_file = mp.AudioFileClip(mp4_path)
        new_file.write_audiofile(mp3_path)
        os.remove(mp4_path)
        self.sema.release()

    def download_videos(self):
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        for url in self.videos_urls:
            process = threading.Thread(target=self.download_video, args=(url,))
            self.jobs.append(process)
        for process in self.jobs:
            process.start()
        for process in self.jobs:
            process.join()
        self.jobs = []
        new_line = "\n"
        print(f"Unable to download: {new_line.join(self.errors)}")

    def convert_videos(self):
        for index, mp4_path in enumerate(self.paths):
            process = threading.Thread(target=self.change_mp4_to_mp3, args=(mp4_path, self.mp3_paths[index],))
            self.jobs.append(process)
        for process in self.jobs:
            process.start()
        for process in self.jobs:
            process.join()
        self.jobs = []

    def run_downloading(self):
        self.get_videos_url()
        self.download_videos()
        self.get_videos_paths()
        self.convert_videos()

