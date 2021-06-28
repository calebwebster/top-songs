"""
Top Songs
2021
This application uses a GUI to list the top songs of the week from www.billboard.com.

Features:
Launches web and desktop Spotify apps.
Plays requested songs.
Opens song artists in launcher.
Plays song music videos on Youtube.
Github: https://www.github.com/CalebWebsterJCU/TopSongs

See README.md for info regarding application setup.
"""

from youtube_search import YoutubeSearch
from spotipy.oauth2 import SpotifyOAuth
from PIL import ImageTk, Image as Img
from tkinter import messagebox
from bs4 import BeautifulSoup
from spotipy import Spotify
from tkinter import ttk
from tkinter import *
import webbrowser
import requests
import socket
import os

NUM_SONGS = 100
LARGE_FONT = ('Goldman', 22)
MEDIUM_FONT = ('Goldman', 10)
SMALL_FONT = ('Sansation', 12)
SCROLL_SPEED = 1
CREDENTIALS_FILE = 'credentials.txt'


class TopSongsApp:
    """
    A class to store methods for the Top Songs Application.
    
    Attributes:
        sp_api : Spotify
            spotify api connection object used to play songs
        songs : list[dict]
            list of songs read from www.billboard.com
        root : Tk
            Tkinter base window on which to build ui
        images : dict[str: ImageTk]
            loaded images used for youtube buttons and scroll top button
        widgets : dict[str: Widget]
            dictionary of widgets (widget name mapped to widget object)
    
    Methods:
        get_spotify_creds():
            Read spotify credentials from environment variables or CREDENTIALS_FILE
        get_top_songs(n):
            Request and return a number of top songs from www.billboard.com
        create_ui(self):
            Create static buttons and sections and add them to the GUI.
        create_scrollable_frame(self):
            Create Scrollable region to contain song widgets.
        create_song_widgets(self):
            Create buttons and labels for each song.
        open_project_github(event):
            Open the TopSongs directory in GitHub.
        open_developer_github(event):
            Open developer's Github page.
        open_desktop_player():
            Open the Spotify Desktop Player using Windows command prompt.
        open_desktop_player():
            Open the Spotify Desktop Player using Windows command prompt.
        open_web_player():
            Open the Spotify Web Player in the default browser.
        scroll_to_top(self):
            Scroll to top of scrollable songs frame.
        scroll(self, event):
            Scroll through songs.
        number_btn_release(self, event):
            Open Billboard song chart upon releasing song number button.
        song_btn_release(self, event):
            Start song playback upon releasing song name button
        artist_btn_release(self, event):
            Open artist in currently open player upon releasing artist button.
        yt_btn_release(self, event):
            Open song's music video upon releasing youtube button.
        button_hover(self, event):
            Upon hovering over a widget, update status label with widget's message.
        button_leave(self, event):
            Upon leaving a widget, clear status label.
        open_song_chart(self, button):
            Open Billboard chart with button's song selected.
        get_song_data(self, song):
            Get a song's track and artist URIs from Spotify's API via spotipy.
        spotify_launchers_are_running(self):
            Check whether Spotify app or web players (or both) are running.
        open_artist(self, button):
            Open an artist in the currently open Spotify player.
        play_song(self, button):
            Play a song in the currently open Spotify player.
        open_music_video(self, button):
            Open a song's music video on YouTube in the default browser.
        get_real_artist(artist):
            Return an artist string with featured artists removed.
        run(self):
            Start TopSongs app.
    """
    
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None):
        """
        Create attributes for TopSongs object, connect spotipy, get songs, initialize Tkinter.
        
        :param client_id: Client ID of your Spotify app (default=None)
        :param client_secret: Client Secret of your Spotify app (default=None)
        :param redirect_uri: Redirect URI of your Spotify app (default=None)
        
        The above parameters are optional, if they are left blank the program will set them from
        environment variables or by reading CREDENTIALS_FILE (see get_spotify_creds()). Whichever
        of these three ways you choose, these three variables must be set and correct to run TopSongs.
        
        NOTE: providing TopSongs with your credentials allows the program to access your spotify account.
        
        the variable scope dictates which parts of your information TopSongs can access. The scope is set
        to "user-read-currently-playing user-modify-playback-state user-read-playback-state", which means
        that TopSongs can only start/stop playback, see what you're playing, and what device you're playing
        on.
        """
        scope = 'user-read-currently-playing user-modify-playback-state user-read-playback-state'
        if client_id and client_secret and redirect_uri:
            cid, secret, uri = client_id, client_secret, redirect_uri
        else:
            cid, secret, uri = self.get_spotify_creds()
        auth_manager = SpotifyOAuth(
            scope=scope,
            client_id=cid,
            client_secret=secret,
            redirect_uri=uri
        )
        self.sp_api = Spotify(auth_manager=auth_manager)
        self.songs = self.get_top_songs(NUM_SONGS)
        self.root = Tk()
        self.root.title('Top Songs')
        self.root.resizable(False, False)
        self.root.iconbitmap("top_songs/icon.ico")
        self.images = {
            'youtube': ImageTk.PhotoImage(Img.open('top_songs/youtube.png')),
            'up_arrow': ImageTk.PhotoImage(Img.open('top_songs/up_arrow.png')),
        }
        self.widgets = {}
        self.create_ui()
    
    @staticmethod
    def get_spotify_creds():
        """
        Read spotify credentials from environment variables or CREDENTIALS_FILE.
        
        :except KeyError: if one or more env variables are missing, read from file
        
        Environment variable names:
        SPOTIPY_CLIENT_ID
        SPOTIPY_CLIENT_secret
        SPOTIPY_REDIRECT_URI
        
        Credentials file format:
        Line 1: Client Id
        Line 2: Client Secret
        Line 3: Redirect Uri
        """
        try:
            client_id = os.environ['SPOTIPY_CLIENT_ID']
            client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
            redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']
        except KeyError:
            with open(CREDENTIALS_FILE, 'r') as file_in:
                client_id = file_in.readline().strip()
                client_secret = file_in.readline().strip()
                redirect_uri = file_in.readline().strip()
                
        return client_id, client_secret, redirect_uri
    
    @staticmethod
    def get_top_songs(n):
        """
        Request and return a number of top songs from www.billboard.com.
        
        :param int n: number of songs to return
        :return: top songs
        :rtype: list[dict]
        
        songs are extracted from HTML parsed by beautifulsoup4 and are
        stored as dictionaries with the format:
        {
            "number": number,
            "name": name,
            "artist": artist
        }
        NOTE: making n smaller does not reduce network load or processing time.
        You just get less songs.
        """
        top_100 = requests.get('https://www.billboard.com/charts/hot-100')
        try:
            top_100.raise_for_status()
        except requests.HTTPError:
            return []
        html = top_100.text
        top_100.close()
        # Parse HTML.
        soup = BeautifulSoup(html, 'html.parser')
        songs = []
        for number, song in enumerate(soup.find_all('li', class_='chart-list__element')[:n], 1):
            name = song.find('span', class_='chart-element__information__song').text
            artist = song.find('span', class_='chart-element__information__artist').text.replace('Featuring', 'ft.').replace(' x ', ', ').replace(' & ', ', ').replace(' X ', ', ')
            songs.append({'number': number, 'name': name, 'artist': artist})
        return songs
    
    def create_ui(self):
        """
        Create static buttons and sections and add them to the GUI.
        
        Process for creating widgets:
        Step 1. Create widget objects (LabelFrame, Label, Button)
        Step 2. Pack widgets to the screen (widget.grid(), widget.pack())
        Step 3. Add widgets to self.widgets dict
        Step 4. Add message attributes to widgets to show in status bar
        Step 5. Add necessary bindings to widgets
        """
        # Create widgets.
        top_frame = LabelFrame(self.root, bd=3, relief=SUNKEN)
        title_btn = Label(top_frame, bd=0, text='Top Songs', font=LARGE_FONT)
        subtitle_btn = Label(top_frame, bd=0, text='by Caleb Webster', font=MEDIUM_FONT)
        app_btn = Button(top_frame, width=4, bd=3, text='App', font=SMALL_FONT, command=self.open_desktop_player)
        web_btn = Button(top_frame, width=4, bd=3, text='Web', font=SMALL_FONT, command=self.open_web_player)
        scroll_top_btn = Button(top_frame, bd=3, image=self.images['up_arrow'], command=self.scroll_to_top)
        bottom_frame = LabelFrame(self.root, relief=SUNKEN)
        hover_label = Label(bottom_frame, text='', font=SMALL_FONT, anchor=W, width=59)
        # Pack em' in.
        top_frame.grid(row=0, column=0, padx=5, pady=5, sticky=W + E)
        title_btn.grid(row=0, column=0, padx=15)
        subtitle_btn.grid(row=0, column=1, pady=(15, 0))
        app_btn.grid(row=0, column=2, padx=(35, 0))
        web_btn.grid(row=0, column=3)
        scroll_top_btn.grid(row=0, column=4, padx=(31, 0))
        bottom_frame.grid(row=2, column=0, padx=5, pady=5, sticky=W + E)
        hover_label.grid(row=0, column=0)
        # Add widgets to dict.
        self.widgets['top_frame'] = top_frame
        self.widgets['title_btn'] = title_btn
        self.widgets['subtitle_btn'] = subtitle_btn
        self.widgets['app_btn'] = app_btn
        self.widgets['web_btn'] = web_btn
        self.widgets['bottom_frame'] = bottom_frame
        self.widgets['hover_label'] = hover_label
        self.widgets['song_frames'] = []
        # Bind status messages to buttons.
        title_btn.message = 'https://www.github.com/CalebWebsterJCU/TopSongs'
        subtitle_btn.message = 'https://www.github.com/CalebWebsterJCU'
        app_btn.message = 'Open Spotify Desktop Player'
        web_btn.message = 'Open Spotify Web Player'
        scroll_top_btn.message = 'Scroll to Top'
        # Bindings for labels.
        title_btn.bind('<ButtonRelease-1>', self.open_project_github)
        subtitle_btn.bind('<ButtonRelease-1>', self.open_developer_github)
        # Bind hover event to buttons to display info.
        title_btn.bind('<Enter>', self.button_hover)
        subtitle_btn.bind('<Enter>', self.button_hover)
        app_btn.bind('<Enter>', self.button_hover)
        web_btn.bind('<Enter>', self.button_hover)
        scroll_top_btn.bind('<Enter>', self.button_hover)
        # Bind leave event to buttons to clear info panel.
        title_btn.bind('<Leave>', self.button_leave)
        subtitle_btn.bind('<Leave>', self.button_leave)
        app_btn.bind('<Leave>', self.button_leave)
        web_btn.bind('<Leave>', self.button_leave)
        scroll_top_btn.bind('<Leave>', self.button_leave)
        
        self.create_scrollable_frame()
        self.create_song_widgets()
    
    def create_scrollable_frame(self):
        """Create Scrollable region to contain song widgets."""
        middle_frame_outer = LabelFrame(self.root, bd=3, relief=SUNKEN)
        # Behold, the process for creating a simple scrolling widget in Tkinter.
        canvas = Canvas(middle_frame_outer, height=480)
        scrollbar = ttk.Scrollbar(middle_frame_outer, orient=VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda event: canvas.configure(scrollregion=canvas.bbox('all')))
        middle_frame_inner = Frame(canvas)
        middle_frame_inner.bind('<MouseWheel>', self.scroll)
        scrollbar.bind('<MouseWheel>', self.scroll)
        canvas.create_window((0, 0), window=middle_frame_inner, anchor=N + W)
        canvas.yview("moveto", 0)
        
        middle_frame_outer.grid(row=1, column=0, padx=5, pady=5, sticky=W + E)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.widgets['middle_frame_outer'] = middle_frame_outer
        self.widgets['canvas'] = canvas
        self.widgets['scrollbar'] = scrollbar
        self.widgets['middle_frame_inner'] = middle_frame_inner
    
    def create_song_widgets(self):
        """Create buttons and labels for each song."""
        max_name_length = 20
        max_artist_length = 15
        # Add song widgets to bottom frame.
        middle_frame_inner = self.widgets['middle_frame_inner']
        for x in range(len(self.songs)):
            song = self.songs[x]
            # Shorten song and artist name if they exceed the maximum values.
            shortened_name = song['name'][:max_name_length + 1] + '...' if len(song['name']) > max_name_length else song['name']
            shortened_artist = song['artist'][:max_name_length + 1] + '...' if len(song['artist']) > max_name_length else song['artist']
            # Create inner frame and buttons for song name, artist, album cover, and music video.
            song_frame = LabelFrame(middle_frame_inner, bd=3, relief=RAISED)
            number_btn = Label(song_frame, width=3, text=str(song['number']) + '.', font=SMALL_FONT)
            name_btn = Label(song_frame, width=max_name_length, text=shortened_name, padx=10, anchor=W, font=SMALL_FONT)
            artist_btn = Label(song_frame, width=max_artist_length + 5, text=shortened_artist, padx=10, anchor=W, font=SMALL_FONT)
            youtube_btn = Label(song_frame, image=self.images['youtube'])
            # Add data (dict key) and index (song i) to buttons.
            name_btn.data = 'song_uri'
            artist_btn.data = 'artist_uri'
            youtube_btn.data = 'yt_url'
            number_btn.index = x
            name_btn.index = x
            artist_btn.index = x
            youtube_btn.index = x
            # Bind open functions to buttons.
            number_btn.bind('<ButtonRelease-1>', self.number_btn_release)
            name_btn.bind('<ButtonRelease-1>', self.song_btn_release)
            artist_btn.bind('<ButtonRelease-1>', self.artist_btn_release)
            youtube_btn.bind('<ButtonRelease-1>', self.yt_btn_release)
            # Add buttons and frame to bottom frame.
            song_frame.grid(row=x, column=0, padx=6, pady=3, sticky=W + E)
            number_btn.grid(row=0, column=0)
            name_btn.grid(row=0, column=1)
            artist_btn.grid(row=0, column=2)
            youtube_btn.grid(row=0, column=3, padx=10)
            # Attach hover message to buttons.
            number_btn.message = song['number']
            name_btn.message = song['name']
            artist_btn.message = song['artist']
            youtube_btn.message = f'{song["name"]} Music Video'
            # Bind hover event to buttons to display info.
            number_btn.bind('<Enter>', self.button_hover)
            name_btn.bind('<Enter>', self.button_hover)
            artist_btn.bind('<Enter>', self.button_hover)
            youtube_btn.bind('<Enter>', self.button_hover)
            # Bind leave event to buttons to clear info panel.
            number_btn.bind('<Leave>', self.button_leave)
            name_btn.bind('<Leave>', self.button_leave)
            artist_btn.bind('<Leave>', self.button_leave)
            youtube_btn.bind('<Leave>', self.button_leave)
            # Bind scroll event to buttons and container.
            song_frame.bind('<MouseWheel>', self.scroll)
            number_btn.bind('<MouseWheel>', self.scroll)
            name_btn.bind('<MouseWheel>', self.scroll)
            artist_btn.bind('<MouseWheel>', self.scroll)
            youtube_btn.bind('<MouseWheel>', self.scroll)
            
            self.widgets['song_frames'].append(song_frame)
    
    @staticmethod
    def open_project_github(event):
        """Open the TopSongs directory in GitHub."""
        button = event.widget
        x, y = event.x, event.y
        # Check if mouse is on button
        if 0 < x < button.winfo_width() and 0 < y < button.winfo_height():
            webbrowser.open('https://www.github.com/CalebWebsterJCU/TopSongs')
    
    @staticmethod
    def open_developer_github(event):
        """Open developer's Github page."""
        button = event.widget
        x, y = event.x, event.y
        # Check if mouse is on button
        if 0 < x < button.winfo_width() and 0 < y < button.winfo_height():
            webbrowser.open('https://www.github.com/CalebWebsterJCU')
    
    @staticmethod
    def open_desktop_player():
        """Open the Spotify Desktop Player using Windows command prompt."""
        os.system('spotify')
    
    @staticmethod
    def open_web_player():
        """Open the Spotify Web Player in the default browser."""
        webbrowser.open('https://open.spotify.com')
    
    def scroll_to_top(self):
        """Scroll to top of scrollable songs frame."""
        canvas = self.widgets['canvas']
        canvas.yview_scroll(-len(self.songs), 'units')
    
    def scroll(self, event):
        """Scroll through songs."""
        canvas = self.widgets['canvas']
        # Event.delta will be either 120 or -120.
        # By finding the sign of event.delta, the
        # program can scroll the opposite direction.
        sign = event.delta // abs(event.delta)
        canvas.yview_scroll(-sign * SCROLL_SPEED, 'units')
    
    def number_btn_release(self, event):
        """Open Billboard song chart upon releasing song number button."""
        button = event.widget
        x, y = event.x, event.y
        # Check if mouse is on button
        if 0 < x < button.winfo_width() and 0 < y < button.winfo_height():
            self.open_song_chart(button)
    
    def song_btn_release(self, event):
        """
        Start song playback upon releasing song name button.
        
        Playback will start in currently running Spotify player.
        If both web and app players are running, app is preferred.
        """
        button = event.widget
        x, y = event.x, event.y
        # Check if mouse is on button
        if 0 < x < button.winfo_width() and 0 < y < button.winfo_height():
            self.play_song(button)
    
    def artist_btn_release(self, event):
        """Open artist in currently open player upon releasing artist button."""
        button = event.widget
        x, y = event.x, event.y
        # Check if mouse is on button
        if 0 < x < button.winfo_width() and 0 < y < button.winfo_height():
            self.open_artist(button)
    
    def yt_btn_release(self, event):
        """Open song's music video upon releasing youtube button."""
        button = event.widget
        x, y = event.x, event.y
        # Check if mouse is on button
        if 0 < x < button.winfo_width() and 0 < y < button.winfo_height():
            self.open_music_video(button)
    
    def button_hover(self, event):
        """Upon hovering over a widget, update status label with widget's message."""
        button = event.widget
        hover_label = self.widgets['hover_label']
        hover_label.config(text=button.message)
    
    def button_leave(self, event):
        """Upon leaving a widget, clear status label."""
        assert event
        hover_label = self.widgets['hover_label']
        hover_label.config(text='')
    
    def open_song_chart(self, button):
        """
        Open Billboard chart with button's song selected.
        
        :param button: button that was pressed.
        
        Song buttons store their song's index, which is used to find the correct song.
        """
        song = self.songs[button.index]
        song_number = song['number']
        webbrowser.open(f'https://www.billboard.com/charts/hot-100?rank={song_number}')
    
    def get_song_data(self, song):
        """
        Get a song's track and artist URIs from Spotify's API via spotipy.
        
        :param dict song: song data dictionary
        :returns: song URI, artist URI
        :rtype: str, str
        
        NOTE: Artist URI returned is the first artist listed (TopSongs can
        ony open one artist at this time).
        """
        song_name = song['name']
        artist = song['artist']
        real_artist = self.get_real_artist(artist)
        # Send request to Spotify's API and sift through dict to find desired data.
        result = self.sp_api.search(q=f'{song_name} {real_artist}', type='track', limit=1)
        uri = result['tracks']['items'][0]['uri']
        artist_uri = result['tracks']['items'][0]['artists'][0]['uri']  # First listed artist
        return uri, artist_uri
    
    def spotify_launchers_are_running(self):
        """
        Check whether Spotify app or web players (or both) are running.
        
        :return: tuple (bool, bool) for app, web player running
        
        This function uses the socket module to get your PC's name.
        """
        app = False
        web = False
        pc_name = socket.gethostname()
        devices = self.sp_api.devices()['devices']
        print(devices)
        for device in devices:
            if device['name'] == pc_name:
                app = True
            if 'Web Player' in device['name']:
                web = True
        return app, web
    
    def open_artist(self, button):
        """
        Open an artist in the currently open Spotify player.
        
        :param button: button that was pressed
        
        If a artist's URI is already stored, open it in the browser,
        desktop app, or both. If not, get and store song's data, then
        open artist's URI.
        """
        # Button stores data key and song index.
        i = button.index
        song = self.songs[i]
    
        if 'artist_uri' in song:
            uri = song['artist_uri']
        else:
            song['uri'], song['artist_uri'] = self.get_song_data(song)
            uri = self.songs[i]['artist_uri']
        
        app, web = self.spotify_launchers_are_running()
        
        if app:
            os.system(f'spotify --uri={uri}')
        if web:
            uri_type, uri_id = uri.split(':')[1], uri.split(':')[2]
            webbrowser.open(f'https://open.spotify.com/{uri_type}/{uri_id}')
        
    def play_song(self, button):
        """
        Play a song in the currently open Spotify player.
        
        :param button: button that was pressed
        
        If a song's URI is already stored, play it. get and store song's
        data, then play song's URI.
        """
        # Button stores data key and song index.
        i = button.index
        song = self.songs[i]
        
        if 'uri' in song:
            uri = song['uri']
        else:
            song['uri'], song['artist_uri'] = self.get_song_data(song)
            uri = self.songs[i]['uri']
        
        devices = self.sp_api.devices()['devices']
        if len(devices) > 0:
            device_id = devices[0]['id']  # Play on first device
            self.sp_api.start_playback(uris=[uri], device_id=device_id)
        else:
            messagebox.showinfo('No Player', 'No Spotify player running! Use the App/Web buttons to launch Spotify. You may have to wait a second before hitting play.')
    
    def open_music_video(self, button):
        """
        Open a song's music video on YouTube in the default browser.
        
        :param button: button that was pressed
        
        If a song's music video url is already stored, open it. If not, search
        for the song on www.youtube.com, get and store the first video result,
        then open the music video.
        """
        # Button stores data key and song index.
        key = button.data
        i = button.index
        song = self.songs[i]
        
        if key in song:
            url = song[key]
        else:
            song_name = song['name']
            artist = song['artist']
            real_artist = self.get_real_artist(artist)
            # Search for song using youtube_search and sift through dict to find desired data.
            results = YoutubeSearch(f'{song_name} {real_artist}', max_results=1).to_dict()
            video_id = results[0]['id']
            url = f'https://www.youtube.com/watch?v={video_id}'
            song['yt_url'] = url
        
        webbrowser.open(url)
    
    @staticmethod
    def get_real_artist(artist):
        """Return an artist string with featured artists removed."""
        if ' ft.' in artist:
            return artist[:artist.find(' ft.')]
        return artist
    
    def run(self):
        """Start TopSongs app."""
        self.root.mainloop()


if __name__ == '__main__':
    TopSongsApp().run()
