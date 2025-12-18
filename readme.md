# Youtube Downloader by MarkIrahCarey

This is a personal project stemed from another project for my masters in Data Science. 

## Features
- Search YouTube videos
- Download videos/audio
- User-friendly interface

## Libraries used
- `os`, `platform`, `subprocess`, `requests`
- `tkinter`, `PIL`

The main base of the code however is `yt_dlp`
you can view more of it here:
https://github.com/yt-dlp/yt-dlp

**If you do not have the libraires installed, please run this line here**

`pip3 install Pillow requests yt-dlp`

**or if you are in windows, this should also work**

`python -m pip install pillow requests yt-dlp`

## Other Planned Features

- Ability to download in other resolutions (360p, 480p, 720p, etc.)
- Ability to change the directory of downloads
- Add Linux support (maybe, I do not have Linux)
- Download Playlist feature
- Add a workaround for age-restricted videos
- Give a way to tell the user how long before a download is finished (unsure if this is possible)
