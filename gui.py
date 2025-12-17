import tkinter as tk
from PIL import Image, ImageTk
from yt_searcher import yt_search
import requests
from io import BytesIO
import os

# we will create a main class for the GUI of this app
class App(tk.Tk):

    # note that this will frame stack as we expect multiple windows
    def __init__(self):
        super().__init__()
        self.title("Youtube Search App by MarkIraCarey")
        self.geometry("612x1104")
        
        # Container frame to hold all pages
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Dictionary to hold all frames/pages
        self.frames = {}
        
        # Create all pages
        for PageClass in (HomePage, AboutPage, SearchPage, DownloadsPage):
            page_name = PageClass.__name__
            frame = PageClass(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Show login page first
        self.show_frame("HomePage")

    def show_frame(self, page_name, data=None):
        frame = self.frames[page_name]
        frame.tkraise()
        
        if data is not None and hasattr(frame, 'load_data'):
            frame.load_data(data)

        # Update window title
        self.title(f"Youtube Search App by MarkIraCarey - {page_name.replace('Page', '')}")


class HomePage(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # configure a grid for centering
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)

        # Main Content
        content_frame = tk.Frame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # title and background color
        tk.Label(content_frame, text="Welcome", 
                font=("Arial", 48, "bold")).pack(pady=(0, 20))
        
        tk.Label(content_frame, text="YouTube Search & Downloader by MarkIraCarey", 
                font=("Arial", 24)).pack(pady=(0, 30))

        # add an about button
        about_btn = tk.Button(content_frame, text="About this app",
                             font=("Arial", 20),
                             command=lambda: controller.show_frame("AboutPage"))
        about_btn.pack()

        # add the search button
        about_btn = tk.Button(content_frame, text="Search and Download a Video",
                             font=("Arial", 20),
                             command=lambda: controller.show_frame("SearchPage"))
        about_btn.pack()


class AboutPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self = tk.Frame(self)
        self.grid(row=1, column=0, sticky="nsew", padx=1, pady=1)

        description = """
        This is a YouTube downloader application
        built with Python and Tkinter.

        The main searching/downloading device is yt_dlp.
        For more information, please check thier github: 
        https://github.com/yt-dlp/yt-dlp
        
        Features:
        - Search YouTube videos
        - Download videos/audio
        - User-friendly interface
        """

        # Simple about page content
        tk.Label(self, text="About This App", 
                font=("Arial", 48, "bold")).pack(pady=50)
        
        tk.Label(self, text=description, 
                font=("Arial", 24)).pack(pady=10)
        
        # Back button
        back_btn = tk.Button(self, text="← Back to Home",
                           font=("Arial", 20),
                           command=lambda: controller.show_frame("HomePage"))
        back_btn.pack(pady=20)

        
class SearchPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self = tk.Frame(self)
        self.pack(expand=True, fill="both")
        self.grid_rowconfigure(0, weight=0)   
        self.grid_rowconfigure(1, weight=1)  
        self.grid_rowconfigure(2, weight=0)   
        self.grid_columnconfigure(0, weight=1)  

        # search text area
        tk.Label(self, text = "Search Bar:", font=("Arial", 24)).pack(padx = 10, pady = 10)
        entry = tk.Entry(self, width = 30, font=("Arial", 24))
        entry.pack(padx = 5, pady = 5)
        
        # Button to get the text
        def search_video():
            text = entry.get()
            
            # create an instance of the yt_searcher
            searcher = yt_search(query = text)

            # then append the results
            update_search(searcher.get_results())
            
        
        submit_button = tk.Button(self, text="Submit Search", font=("Arial", 20), command=search_video)
        submit_button.pack(pady=10)

        # create the downloads function
        def on_image_click(video_url, photo_url, title, photo):
            download_data = {
                'photo_url': photo_url,
                'title': title,
                'photo': photo,
                'video_url': video_url
            }
            # open up the new page
            controller.show_frame("DownloadsPage", download_data)


        # middle where it shows thumbnails and stuff
        canvasx = 590
        canvasy = 662

        # Create frame to hold canvas and scrollbar
        canvas_frame = tk.Frame(self)
        canvas_frame.pack(fill="both", expand=True)

        # Create canvas with scrollbar
        search_results = tk.Canvas(canvas_frame, bg="#929292", width=canvasx, height=canvasy)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=search_results.yview)

        # Configure canvas
        search_results.configure(yscrollcommand=scrollbar.set)
        search_results.config(scrollregion=(0, 0, 500, 500))

        # Pack them side by side
        search_results.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Store thumbnail objects for reference
        self.thumbnail_items = []
        self.video_urls = []
        self.titles = []
        self.channel_names = []
        self.image_references = []

        # firt create a method to create a small tkinter object for the canvas
        def create_thumbnail(canvas):
            thumbnail_urls = self.thumbnail_items
            titles = self.titles
            channels = self.channel_names
            videos = self.video_urls

            # track vertical position
            y_position = 10
            # get the images
            for url, title, channel, video in zip(thumbnail_urls, titles, channels, videos):
                # create the image
                try:
                    # download image
                    response = requests.get(url, timeout=5)

                    # get the metadata
                    img_data = BytesIO(response.content)  

                    # load in image, fit it to the canvas with a little padding
                    img = Image.open(img_data)

                    # keep all images the same size
                    img = img.resize((int(canvasx * 0.95), 315))

                    # convert to PhotoImage for tkinter
                    photo = ImageTk.PhotoImage(img)
                    
                    # add it to the canvas
                    image_id = canvas.create_image(18, y_position, anchor="nw", image=photo)

                    # add text below it
                    texts = " | " + channel + " | "
                    if len(title) > 40:
                        texts += title[0:50] + "..."
                    else:
                        texts += title

                    text_id = canvas.create_text(18, y_position + 321, anchor="nw", text=texts, 
                                                 font=("Arial", 20, "bold"), fill="white")

                    # keep reference so it doesn't get garbage collected
                    self.image_references.append(photo)

                    # make both the text and the image clickable
                    canvas.tag_bind(image_id, "<Button-1>", lambda event, v=video, u=url, t=title, p=img: on_image_click(v, u, t, p)) 
                    canvas.tag_bind(text_id, "<Button-1>", lambda event, v=video, u=url, t=title, p=img: on_image_click(v, u, t, p))

                    # move to next image
                    y_position += 400

                except Exception as e:
                    # create a colored rectangle as fallback
                    canvas.create_rectangle(18, y_position, int(canvasx * 0.95), 315, fill="gray")
                    canvas.create_text(105, y_position + (y_position//2), text="Image\nFailed", fill="white")

                    y_position += 400

            canvas.config(scrollregion=(0, 0, canvasx, y_position + 10))

        def update_search(search_results_list):
            # reset
            search_results.delete("all")  
            self.thumbnail_items.clear()
            self.titles.clear()
            self.channel_names.clear()
            self.image_references.clear()
            self.video_urls.clear()
            ''' 
            get the thumbnails and title for each result
            the title will be the name of the picture, then the thumbnail is the picture
            '''
            
            for result in search_results_list:
                self.thumbnail_items.append(result['thumbnail'])
                self.titles.append(result['title'])
                self.channel_names.append(result['channel'])
                self.video_urls.append(result['url'])

            create_thumbnail(search_results)

        # the back button
        back_btn = tk.Button(self, text="← Back to Home",
                        font=("Arial", 20),
                        command=lambda: controller.show_frame("HomePage"))
        back_btn.pack(pady=20)


class DownloadsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Create a background 
        self.bg_overlay = tk.Frame(self, bg="black")
        self.bg_overlay.place(relwidth=1, relheight=1)  
        
        # make a center frame 
        self.center_frame = tk.Frame(self, bg="gray", relief="raised", bd=3)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center", 
                               width=400, height=500)
        
        # Initialize empty data
        self.photo_url_link = None
        self.video_url_link = None
        self.title_video = None
        self.photo_video = None
        self.output_path = os.path.join(os.path.dirname(__file__), "Downloads_ytdlp")

        # Create widgets but don't populate yet
        self.create_widgets()

    def create_widgets(self):

        def download_audio():
            # create a yt_searcher 
            searcher = yt_search(url = self.video_url_link , title = self.title_video, path = self.output_path)

            # then download!
            print("Started Downloading")
            searcher.download_mp3()
            print("Ended Downloading")

        def download_video():
            # create a yt_searcher 
            searcher = yt_search(url = self.video_url_link , title = self.title_video, path = self.output_path)

            # then download!
            print("Started Downloading")
            searcher.download_mp4()
            print("Ended Downloading")


        # Create labels but store references
        self.image_label = tk.Label(self.center_frame, bg="black")
        self.image_label.pack()
        
        self.title_label = tk.Label(self.center_frame, text="TEST TITLE", 
                                    font=("Arial", 24), bg="black")
        self.title_label.pack(pady=10)
        
        tk.Label(self.center_frame, text="Download?", 
                font=("Arial", 20, "bold"), bg="black").pack(pady=20)
        
        # Create TWO separate frames for the buttons
        top_button_frame = tk.Frame(self.center_frame, bg="white")
        top_button_frame.pack(pady=10)
        
        # MP4 and MP3 buttons in top frame
        tk.Button(top_button_frame, text="MP3 Download", width=15, command=download_audio).pack(side="left", padx=5)
        tk.Button(top_button_frame, text="MP4 Download", width=15, command=download_video).pack(side="left", padx=5)
        
        # Back button in its own frame
        bottom_button_frame = tk.Frame(self.center_frame, bg="black")
        bottom_button_frame.pack(pady=10)
        
        tk.Button(bottom_button_frame, text="Back to Search Page",
                command=lambda: self.controller.show_frame("SearchPage"),
                width=32).pack()
    

    def load_data(self, data):
        self.photo_url_link = data['photo_url']
        self.title_video = data['title']
        self.photo_video = data['photo']
        self.video_url_link = data['video_url']
        
        # resize photo
        self.photo_video = self.photo_video.resize((350, 200))

        # store the photo
        self.display_photo = ImageTk.PhotoImage(self.photo_video)

        # check if the title is less than 30, if not add ...
        if len(self.title_video) > 30:
            text = self.title_video[0:30] + "..."
        else:
            text = self.title_video
        # Update widgets with actual data
        self.title_label.config(text=text)
        self.image_label.config(image=self.display_photo)

    
