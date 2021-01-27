"""Run Top Songs app."""

from top_songs import TopSongsApp
import os

if __name__ == '__main__':
    os.chdir('top_songs')
    TopSongsApp().run()
