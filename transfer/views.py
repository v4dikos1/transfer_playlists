from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from .utils import Spotify


class HomeView(View):
    template_name = 'transfer/home.html'

    def get(self, request):
        return render(request, self.template_name)


class PlaylistView(View):
    template_name = 'transfer/playlist.html'

    def get(self, request):
        spotify = Spotify()
        playlist = spotify.get_spotify_playlist(
            'https://open.spotify.com/playlist/0ko5GwC8PASMZUi1p4IvE8?si=2e64e42cd1fe4f1b')

        return render(request, self.template_name, {'tracks': playlist['tracks']})

