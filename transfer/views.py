from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from .utils import Spotify, YoutubeMusic
import spotipy


spotify = None
yt = None


class HomeView(View):
    template_name = 'transfer/home.html'

    def get(self, request):
        return render(request, self.template_name)


class PlaylistsView(View):
    template_name = 'transfer/playlist.html'

    def get(self, request):
        playlist = spotify.get_spotify_playlist(
            'https://open.spotify.com/playlist/37i9dQZF1DWWmsWPbM2pKT?si=383e81e2361343cd')

        return render(request, self.template_name, {'tracks': playlist['tracks']})


class LoginView(View):
    template_name = 'transfer/login.html'

    def get(self, request):

        return render(request, self.template_name)


def spotify_login(request):
    global spotify
    spotify = Spotify()

    return redirect('login')


def youtube_login(request):
    global yt
    yt = YoutubeMusic()

    return redirect('login')


def transfer_playlist(request):
    playlist = spotify.get_spotify_playlist(
        'https://open.spotify.com/playlist/37i9dQZF1DWWmsWPbM2pKT?si=383e81e2361343cd')
    tracks = yt.search_songs(playlist['tracks'])
    yt_playlist_id = yt.create_playlist(playlist['name'], 'Transfer from Spotify', 'PUBLIC')
    yt.add_playlist_items(yt_playlist_id, tracks)

    return redirect('home')
