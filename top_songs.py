#! py -3.7
"""
Top Songs
2021
This tkinter application uses a GUI to get and display the top songs
from www.billboard.com with links to the music videos on youtube.
"""

import os
from tkinter import *
from tkinter import ttk
import requests
import webbrowser
from bs4 import BeautifulSoup
from youtube_search import YoutubeSearch
from PIL import ImageTk, Image
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials


class TopSongs:
    """Top Songs Tkinter Application."""
    
    DEFAULT_NUM_SONGS = 10
    LARGE_FONT = ('Goldman', 22)
    SMALL_FONT = ('Sansation', 12)
    SCROLL_SPEED = 30
    
    def __init__(self):
        self.num_songs = self.DEFAULT_NUM_SONGS
        self.top_songs = []
        self.sp_api = Spotify(client_credentials_manager=SpotifyClientCredentials())
        self.songs = self.get_top_songs()
        self.launcher = 'app'
        self.root = Tk()
        self.root.title('Top Songs')
        self.images = {
            'refresh': ImageTk.PhotoImage(Image.open('refresh.png')),
            'youtube': ImageTk.PhotoImage(Image.open('youtube.png').resize((30, 30)))
        }
        self.widgets = {}
        self.create_ui()
        
    def create_ui(self):
        """Create static buttons and sections and add them to the GUI."""
        # Create widgets.
        top_frame = LabelFrame(self.root, bd=3, relief=SUNKEN)
        title = Label(top_frame, text='Top Songs', font=self.LARGE_FONT)
        num_songs = Entry(top_frame, width=3, bd=3, font=self.SMALL_FONT)
        refresh_btn = Button(top_frame, bd=3, image=self.images['refresh'], command=self.refresh)
        launcher_btn = Button(top_frame, bd=3, text='Spotify App', font=self.SMALL_FONT, command=self.switch_launcher)
        bottom_frame = LabelFrame(self.root, relief=SUNKEN)
        hover_label = Label(bottom_frame, text='', font=self.SMALL_FONT, anchor=W)
        # Pack em' in.
        top_frame.grid(row=0, column=0, padx=5, pady=5, sticky=W+E)
        title.grid(row=0, column=0, padx=75)
        num_songs.grid(row=0, column=1, padx=0)
        num_songs.insert(0, self.DEFAULT_NUM_SONGS)
        refresh_btn.grid(row=0, column=2, padx=15)
        launcher_btn.grid(row=0, column=3, padx=15)
        bottom_frame.grid(row=2, column=0, padx=5, pady=5, sticky=W+E)
        hover_label.grid(row=0, column=0)
        # Add widgets to dict.
        self.widgets['top_frame'] = top_frame
        self.widgets['title'] = title
        self.widgets['num_songs'] = num_songs
        self.widgets['refresh_btn'] = refresh_btn
        self.widgets['launcher_btn'] = launcher_btn
        self.widgets['bottom_frame'] = bottom_frame
        self.widgets['hover_label'] = hover_label
        self.widgets['song_frames'] = []
        
        self.create_scrollable_frame()
        self.create_song_widgets()
    
    def create_scrollable_frame(self, remove=False):
        """Create or refresh scrollable frame to hold songs."""
        if remove:
            self.widgets['middle_frame_outer'].grid_forget()
            self.widgets['canvas'].grid_forget()
            self.widgets['scrollbar'].grid_forget()
            self.widgets['middle_frame_inner'].grid_forget()
            
        middle_frame_outer = LabelFrame(self.root, bd=3, relief=SUNKEN)
        # Behold, the process for creating a simple scrolling widget in Tkinter.
        canvas = Canvas(middle_frame_outer, height=441)
        scrollbar = ttk.Scrollbar(middle_frame_outer, orient=VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda event: canvas.configure(scrollregion=canvas.bbox('all')))
        middle_frame_inner = Frame(canvas)
        self.root.bind_all('<MouseWheel>', self.scroll)
        canvas.create_window((0, 0), window=middle_frame_inner, anchor=N + W)

        middle_frame_outer.grid(row=1, column=0, padx=5, pady=5, sticky=W + E)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.widgets['middle_frame_outer'] = middle_frame_outer
        self.widgets['canvas'] = canvas
        self.widgets['scrollbar'] = scrollbar
        self.widgets['middle_frame_inner'] = middle_frame_inner
    
    def create_song_widgets(self, remove=False):
        """Create buttons and labels for each song."""
        # If specified, remove all song widgets.
        if remove:
            for widget in self.widgets['song_frames']:
                widget.grid_forget()
            self.widgets['song_frames'].clear()
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
            name_btn = Button(song_frame, width=max_name_length, bd=0, text=shortened_name, padx=10, anchor=W, font=self.SMALL_FONT)
            artist_btn = Button(song_frame, width=max_artist_length + 5, bd=0, text=shortened_artist, padx=10, anchor=W, font=self.SMALL_FONT)
            youtube_btn = Button(song_frame, bd=0, image=self.images['youtube'])
            # Add data (dict key) and index (song i) to buttons.
            name_btn.data = 'song_uri'
            artist_btn.data = 'artist_uri'
            youtube_btn.data = 'yt_url'
            name_btn.index = x
            artist_btn.index = x
            youtube_btn.index = x
            # Bind open functions to buttons.
            name_btn.bind('<ButtonRelease-1>', self.song_btn_release)
            artist_btn.bind('<ButtonRelease-1>', self.song_btn_release)
            youtube_btn.bind('<ButtonRelease-1>', self.yt_btn_release)
            # Add buttons and frame to bottom frame.
            song_frame.grid(row=x, column=0, padx=6, pady=3, sticky=W+E)
            name_btn.grid(row=0, column=0)
            artist_btn.grid(row=0, column=1)
            youtube_btn.grid(row=0, column=3, padx=10)
            # Attach hover message to buttons.
            name_btn.message = song['name']
            artist_btn.message = song['artist']
            youtube_btn.message = f'{song["name"]} Music Video'
            # Bind hover event to buttons to display info    .
            name_btn.bind('<Enter>', self.button_hover)
            artist_btn.bind('<Enter>', self.button_hover)
            youtube_btn.bind('<Enter>', self.button_hover)
            # Bind leave event to buttons to clear info panel.
            name_btn.bind('<Leave>', self.button_leave)
            artist_btn.bind('<Leave>', self.button_leave)
            youtube_btn.bind('<Leave>', self.button_leave)
            
            self.widgets['song_frames'].append(song_frame)
    
    def song_btn_release(self, event):
        """LMB release event for song button."""
        button = event.widget
        x, y = event.x, event.y
        # Check if mouse is on button
        if 0 < x < button.winfo_width() and 0 < y < button.winfo_height():
            self.open_spotify_uri(button)
    
    def yt_btn_release(self, event):
        """LMB release event for youtube button."""
        button = event.widget
        x, y = event.x, event.y
        # Check if mouse is on button
        if 0 < x < button.winfo_width() and 0 < y < button.winfo_height():
            self.open_music_video(button)
    
    def switch_launcher(self):
        """Toggle song open method between website and app."""
        button = self.widgets['launcher_btn']
        top_frame = self.widgets['top_frame']
        if self.launcher == 'app':
            self.launcher = 'website'
            btn_text = 'Spotify Website'
        else:
            self.launcher = 'app'
            btn_text = 'Spotify App'
        # Re-create button with new text
        button.grid_forget()
        button = Button(top_frame, bd=3, text=btn_text, font=self.SMALL_FONT, command=self.switch_launcher)
        button.grid(row=0, column=3, padx=15)
        self.widgets['launcher_btn'] = button

    def scroll(self, event):
        """Scroll through songs."""
        canvas = self.widgets['canvas']
        canvas.yview_scroll(-1 * (event.delta // self.SCROLL_SPEED), 'units')
    
    def refresh(self):
        """Set number of songs to number entered, get songs, and re-create song buttons."""
        try:
            self.num_songs = int(self.widgets['num_songs'].get())
        except ValueError:
            self.widgets['num_songs'].delete(0, END)
            self.widgets['num_songs'].insert(0, self.num_songs)
        self.songs = self.get_top_songs()
        # All song buttons and scroll frame must be removed
        # and re-created, otherwise scroll bar won't update.
        self.create_scrollable_frame(remove=True)
        self.create_song_widgets(remove=True)

    def button_hover(self, event):
        """Update hover_label with message."""
        button = event.widget
        hover_label = self.widgets['hover_label']
        hover_label.config(text=button.message)
    
    def button_leave(self, event):
        """Remove text from hover_label."""
        assert event
        hover_label = self.widgets['hover_label']
        hover_label.config(text='')
    
    def get_top_songs(self):
        """Request and return a number of the top songs from billboard.com."""
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
        for number, song in enumerate(soup.find_all('li', class_='chart-list__element')[:self.num_songs], 1):
            name = song.find('span', class_='chart-element__information__song').text
            artist = song.find('span', class_='chart-element__information__artist').text.replace('Featuring', 'ft.').replace(' x ', ', ').replace(' & ', ', ').replace(' X ', ', ')
            songs.append({'number': number, 'name': name, 'artist': artist})
        return songs
    
    @staticmethod
    def get_real_artist(artist):
        """Return an artist string with featured artists removed."""
        if ' ft.' in artist:
            return artist[:artist.find(' ft.')]
        return artist
        
    def open_music_video(self, button):
        """
        If a song's music video url has already been stored, open it.
        If not, search for the song id and build and open the url.
        :param button: button that was pressed
        """
        url = 'https://www.youtube.com'
        # Button stores data key and song index.
        key = button.data
        i = button.index
        song = self.songs[i]
        try:
            url = song[key]
        except KeyError:
            print('Retrieving URL...')
            song_name = song['name']
            artist = song['artist']
            real_artist = self.get_real_artist(artist)
            # Search for song using youtube_search and sift through dict to find desired data.
            results = YoutubeSearch(f'{song_name} {real_artist}', max_results=1).to_dict()
            video_id = results[0]['id']
            url = f'https://www.youtube.com/watch?v={video_id}'
            song['yt_url'] = url
        finally:
            webbrowser.open(url)
    
    def open_spotify_uri(self, button):
        """
        If a song's URIs are already stored, open the desired one.
        If not, search for the song's URIs using spotipy
        and open the desired one, either in website or app.
        :param button: button that was pressed
        """
        uri = ':'
        # Button stores data key and song index.
        key = button.data
        i = button.index
        song = self.songs[i]
        try:
            uri = song[key]
        except KeyError:
            song_name = song['name']
            artist = song['artist']
            real_artist = self.get_real_artist(artist)
            # Send request to Spotify's API and sift through dict to find desired data.
            result = self.sp_api.search(q=f'{song_name} {real_artist}', type='track', limit=1)
            song['song_uri'] = result['tracks']['items'][0]['uri']
            song['artist_uri'] = result['tracks']['items'][0]['artists'][0]['uri']
            uri = self.songs[i][key]
        finally:
            if self.launcher == 'app':
                os.system(f'spotify --uri={uri}')
            else:
                uri_type, uri_id = uri.split(':')[1], uri.split(':')[2]
                webbrowser.open(f'https://open.spotify.com/{uri_type}/{uri_id}')
    
    def run(self):
        """Start app."""
        self.root.mainloop()


if __name__ == '__main__':
    TopSongs().run()
