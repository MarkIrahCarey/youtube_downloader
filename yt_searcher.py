import yt_dlp
import os
import platform
import subprocess

def get_ffmpeg_location():
    system = platform.system()
    base = os.path.join(os.path.dirname(__file__), "ffmpeg")

    if system == "Darwin":
        return os.path.join(base, "mac")
    elif system == "Windows":
        return os.path.join(base, "win")
    elif system == "Linux":
        return os.path.join(base, "linux")
    else:
        raise RuntimeError("Unsupported OS")
    
def search_youtube(query, max_results=10):
    # Search YouTube and return the first result's info.
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': 'in_playlist'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            init_entries = info.get('entries', [])
            entries = extract_video_info(init_entries)
            return entries if entries else None
    except Exception as e:
        print(f"Error searching for {query}: {e}")
        return None

def extract_video_info(data_list):
    result = []
    for item in data_list:
        # Get thumbnail URL, since this is also a dictionary
        thumbnails = item.get('thumbnails', [])
        thumbnail_url = thumbnails[0].get('url') if thumbnails else None
        
        # append into dictionary of one search tiem
        result.append({
            'url': item.get('url'),
            'title': item.get('title'),
            'channel': item.get('channel'),
            'thumbnail': thumbnail_url
        })
    
    # return the list of dictionaries
    return result

def download_audio(url_link, output_dir=None):    
    try:
        if output_dir == None:
            raise Exception("No Valid Path")
        
        title = get_video_title(url_link)

        output_path = f"{output_dir}/{title}"

        # Download audio from a YouTube URL using yt-dlp
        ydl_opts = {
            'ffmpeg_location': get_ffmpeg_location(), 
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,  
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_link])

    except yt_dlp.utils.DownloadError as e:
        print(f"{e}")
        return
    except Exception as e:
        print(f"{e}")
        return
    
def download_video(url_link, output_dir=None):    
    try:
        if output_dir is None:
            raise Exception("No Valid Path")
        
        title = get_video_title(url_link)
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        output_path = f"{output_dir}/{safe_title}"

        ydl_opts = {
            'ffmpeg_location': get_ffmpeg_location(),
            'format': 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]', 
            'outtmpl': f'{output_path}.%(ext)s',
            'merge_output_format': 'mp4', 
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_link])
        
        print(f"✓ Downloaded: {safe_title}.mp4")
        
    except yt_dlp.utils.DownloadError as e:
        print(f"{e}")
    except Exception as e:
        print(f"{e}")

def download_playlist(url_link, output_dir=None, audio_only=False):
    try:
        if output_dir is None:
            raise Exception("No Valid Path")
        
        # check if its a playlist
        def is_playlist(url):
            playlist_indicators = [
                "list=",  
                "playlist",  
                "/playlist/",  
                "&list=" 
            ]

            return any(indicator in url.lower() for indicator in playlist_indicators)
            
        if not is_playlist(url_link): raise Exception("Not a playlist")

        if audio_only:
            format_str = 'bestaudio/best'
            postprocessors = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            format_str = 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]'
            postprocessors = []
        
        ydl_opts = {
            'ffmpeg_location': get_ffmpeg_location(), 
            'format': format_str,
            'outtmpl': f'{output_dir}/%(playlist_title)s/%(title)s.%(ext)s',
            'postprocessors': postprocessors,
            'quiet': False,
            'ignoreerrors': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_link])
        
    except Exception as e:
        print(f"Error: {e}")

def get_video_title(url_link):
    try:
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_link, download=False)
            title = info.get('title', 'Unknown_Title')
            return title
    except Exception as e:
        print(f"Error getting title: {e}")
        return 'Unknown_Title'


class yt_search():
    def __init__(self, query=None, url=None, title=None, path=None):
        self.query = query
        self.url = url
        self.title = title
        self.path = path
        
        if query:
            self.results = search_youtube(query)
        else:
            self.results = None
        

    def get_results(self):
        return self.results
    
    def download_mp3(self):
        download_audio(self.url, self.path)

    def download_mp4(self):
        download_video(self.url, self.path)

    def download_link_to_mp3(self):
        download_audio(self.url, self.path)

    def download_link_to_mp4(self):
        download_video(self.url, self.path)

    def download_playlist_link_to_mp3(self):
        if self.url:
            download_playlist(self.url, self.path, audio_only=True)

    def download_playlist_link_to_mp4(self):
        if self.url:
            download_playlist(self.url, self.path, audio_only=False)
        


