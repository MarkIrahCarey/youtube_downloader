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

def download_audio(url_link, title, output_dir=None):    
    try:
        if output_dir == None:
            raise Exception("No Valid Path")
        
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
    

def download_video(url_link, title, output_dir=None):    
    try:
        if output_dir == None:
            raise Exception("No Valid Path")
        
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        output_path = f"{output_dir}/{safe_title}"

        ydl_opts = {
            'ffmpeg_location': get_ffmpeg_location(),
            'format': 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]', 
            'outtmpl': f'{output_path}', 
            'merge_output_format': 'mp4', 
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_link])

            downloaded_file = f"{output_path}.mp4"

    except yt_dlp.utils.DownloadError as e:
        print(f"{e}")
        return
    except Exception as e:
        print(f"{e}")
        return

    # once successful, we need to convert the video into something compatable for all devices.
    # this is done through ffprobe and ffmpeg
    
    print("Converting")
    if os.path.exists(f'{output_path}.mp4'):   
        print("Start Conversion")
        new_output_path = f"{output_dir}/{safe_title}"

        ffmpeg_directory = ""
        
        if platform.system() == "Darwin":
            ffmpeg_directory = f"{get_ffmpeg_location()}/ffmpeg"
        elif platform.system() == "Windows":
            ffmpeg_directory = f'{get_ffmpeg_location()}/ffmpeg.exe'

        command = [
            ffmpeg_directory,
            '-i', f'{output_path}.mp4',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'veryfast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-movflags', '+faststart',
            f'{new_output_path}_fixed.mp4',
            '-y'
        ]

        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Successfully converted {output_path} to {new_output_path}")
        except subprocess.CalledProcessError as e:
            print('FFmpeg command failed:')
            print(e.stderr.decode())
        except FileNotFoundError:
            print("FFmpeg executable not found. Make sure it's installed and in your system's PATH.")

        # then delete the old one
        os.remove(f"{output_path}.mp4")


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
        download_audio(self.url, self.title, self.path)

    def download_mp4(self):
        download_video(self.url, self.title, self.path)


