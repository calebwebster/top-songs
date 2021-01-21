# Top Songs

#### Keep up with the hottest music!

Top Songs is a python application created using Tkinter that gets the top 100 songs of the week
from [Billboard](https://www.billboard.com/charts/hot-100) and displays them using a simple GUI.

> _"Might help you stay relevant."_

Top Songs uses the Spotify API through the python module _spotipy_ to play songs at the click of
a button. Simply click on a song's name to start playback in the currently running spotify player
(app or web). There are also buttons at the top of the program to launch both players. There are
also buttons for opening the song's position on the Billboard chart, the song's artist, and the
song's music video on [YouTube](https://www.youtube.com).

__NOTE:__ To run Top Songs, you will need the following python modules installed:

- spotipy
- youtube_search
- Python Imaging Library (PIL)
- BeautifulSoup (bs4)
- requests
- socket
- tkinter (installed by default)
- webbrowser (installed by default)
- os (installed by default)

So you may have to do this:

`pip install spotipy`

`pip install youtube-search`

`pip install Pillow`

`pip install beautifulsoup4`

`pip install requests`

`pip install socket`

If you plan to import Top Songs into your own code, and you know what environment variables are, download the folder
 _top_songs_ (__not__ the root folder, _TopSongs_), and import the class like this:

`from top_songs import TopSongs`

If you simply want to use the Top Songs app, download the entire directory _TopSongs_ and start the app from run.py:

`python run.py`

## Running the Program

Setting up Top Songs can be a bit tricky, but if you follow these steps, you should be right.

### Step 1: Creating Your Spotify App.
Head over to [Spotify for Developers](https://developer.spotify.com/dashboard) and log in. 

Click "Create an App", give it any name you like, click both the check boxes, and hit "Create".

Once your app has been created, go to EDIT SETTINGS > Redirect URIs and enter any site you want,
it can even be a fake one. I personally use https://www.pccasegear.com, because who doesn't like
looking at those graphics cards you'll never be able to afford. In any case, once you've entered
your site, hit ADD, then SAVE down the bottom.

### Step 2: Storing Your Credentials.
If you just downloaded the top_songs folder, skip to step 3.

If you downloaded the entire TopSongs repository, you will notice a file called "credentials.txt".

Open this file and enter your spotify app data in the following format:

Line 1: Client ID (random character string found underneath the title of your Spotify app).

Line 2: Client Secret (another random character string, found by clicking the SHOW CLIENT SECRET button).

Line 3: Redirect URI (the url you entered in your app settings in step 1).

Don't type anything else other than these three values on their corresponding lines. Doing so will cause the program
to crash.

Once done, close "credentials.txt".

If you completed this step, skip to step 4.

### Step 3: Setting Environment Variables.
Since you don't have "credentials.txt", you need to create environment variables to tell Top Songs
your Spotify app details.

Environment variables can be set in many ways, make sure you know how to set them so you can choose
the method that works best for you.

The environment variables you need to set are:

- __SPOTIPY_CLIENT_ID__ - random character string found underneath the title of your Spotify app.
- __SPOTIPY_CLIENT_SECRET__ - another random character string, found by clicking the SHOW CLIENT SECRET button.
- __SPOTIPY_REDIRECT_URI__ - the url you entered in your app settings in step 1.

### Step 4: Running the Program.
Run Top Songs, either by running "run.py", or, if you're using your own code, initializing a TopSongs object, and calling
the .run() method. The GUI should load, if not, you've forgotten one of the required modules, entered your credentials wrong,
or your internet connection is either terrible or non-existent. Test the Spotify API by clicking on one of the top songs. A 
web page should open and prompt you to "agree" to let Top Songs access and control your spotify account.

After pressing "Agree", you will be redirected to your chosen redirect url. You don't need to do anything on this site, just copy the
url in the browser. This has your secret inside it.

Click on the console, which should have opened when you started Top Songs. There will be a prompt asking you to "enter the url you were
directed to". Simply paste the url you copied from your browser into the console and press enter. Now that you've done this, I can tell 
you that in the blink of an eye I could have emptied all your playlists and filled them with 10000 copies of _"Take it All Away"_, or 
executed the greatest rickroll of all time, all with your permission. You'd better check your account, just in case.

After you've entered the url, spotipy will create a .cache file in the project directory. Do not delete this file. It contains an 
authentication token that will eventually expire, after which you will have to press "agree" and enter the url again.

### Step 5: Enjoy!
You're finished. Have fun playing through the top songs of the week, and please don't try to contact me if you have any problems with the 
program. 

Cheers!

Caleb Webster

## GUI Layout

Below is an example layout of a Top Songs song widget. The buttons are separated by pipe characters ("|")
#### 1 | Fireflies | Owl City | Music Video

In this example, each word is a button that, when clicked, performs a unique function:

- __1__ - opens [Billboard Chart](https://www.billboard.com/charts/hot-100) to _"Fireflies"_, which in this case would be first on the list.
- __Fireflies__ - starts playback of song _"Fireflies"_ on currently open Spotify player (prefers desktop app).
- __Owl City__ - Opens artist _"Owl City"_ in currently open player (or both, if both web and app are open)
- __Music Video__ - Searches for and opens the most relevant video for _"Fireflies Owl City"_ on YouTube, which is usually the song's music video.

## Files

- __top\_songs/main.py__ - GUI Application code.
- __credentials.txt__ - Stores your CLIENT_ID (1st line), CLIENT_SECRET (2nd line), and REDIRECT_URL (3rd line) (see step 3 & 4)
- __run.py__ - Makes running Top Songs app easier: `python run.py`.
