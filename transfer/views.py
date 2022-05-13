import json

from django.db.models.functions import window
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView

from users.models import CustomUser
from .utils import Spotify, YoutubeMusic

auth = ''
yt_auth = ''


class HomeView(View):
    template_name = 'transfer/home.html'

    def get(self, request):
        return render(request, self.template_name)


class PlaylistsView(View):
    template_name = 'transfer/main.html'

    def get(self, request):
        spotify = Spotify()
        username, token = get_spotify_user()
        spotify.auth_with_token(username, token)

        playlist = spotify.get_spotify_playlist(
            'https://open.spotify.com/playlist/37i9dQZF1DWWmsWPbM2pKT?si=383e81e2361343cd')

        return render(request, self.template_name, {'tracks': playlist['tracks']})


class LoginView(View):
    template_name = 'transfer/home.html'

    def get(self, request):
        if auth != '':
            spotify = Spotify()
            username, token = get_spotify_user()
            spotify.auth_with_token(username, token)

            playlists = spotify.get_user_playlists(username)

            return render(request, self.template_name, {'auth': auth,
                                                        'yt_auth': yt_auth,
                                                        'playlists': playlists})

        else:
            return render(request, self.template_name, {'auth': auth
                                                        })


class TracksView(View):
    template_name = 'transfer/main.html'

    def get(self, request, **kwargs):
        spotify = Spotify()
        username, token = get_spotify_user()

        spotify.auth_with_token(username, token)

        playlist = self.kwargs['playlist_id']

        playlist = spotify.get_spotify_playlist(playlist)

        result = render(request, self.template_name, {'auth': auth,
                                                      'yt_auth': yt_auth,
                                                      'tracks': playlist['tracks']})

        return result


def transfer_playlist(request):
    spotify = Spotify()
    yt = YoutubeMusic()
    username, token = get_spotify_user()
    spotify.auth_with_token(username, token)

    if spotify is not None:
        playlist = spotify.get_spotify_playlist(
            'https://open.spotify.com/playlist/37i9dQZF1DWWmsWPbM2pKT?si=383e81e2361343cd')
        tracks = yt.search_songs(playlist['tracks'])
        yt_playlist_id = yt.create_playlist(playlist['name'], 'Transfer from Spotify', 'PUBLIC')
        yt.add_playlist_items(yt_playlist_id, tracks)

        return redirect('home')

    else:
        return redirect('login')


def get_playlists(request):
    if request.method == 'POST':
        playlist = request.POST.get('stringJSON')

        return HttpResponseRedirect(reverse_lazy('songs', kwargs={'playlist_id': playlist}), status=200)


def get_songs(request):
    if request.method == 'POST':
        playlist = json.loads(request.POST.get('stringJSON'))

        spotify = Spotify()
        yt = YoutubeMusic()

        username, token = get_spotify_user()
        spotify.auth_with_token(username, token)

        if spotify is not None:
            tracks = yt.search_songs(playlist)
            yt_playlist_id = yt.create_playlist('Retrowave', 'Transfer from Spotify', 'PUBLIC')
            yt.add_playlist_items(yt_playlist_id, tracks)

        return JsonResponse({'data': playlist}, status=200)

    return redirect('home')


def spotify_login(request):
    global auth

    spotify = Spotify()
    spotify.auth()

    try:
        user = CustomUser.objects.get(username=spotify.username, token=spotify.token)
    except CustomUser.DoesNotExist:
        user = CustomUser(username=spotify.username, token=spotify.token)
        user.save()

    auth = user.token

    return redirect('login')


def get_spotify_user():
    global auth

    username = CustomUser.objects.get(token=auth).username
    token = CustomUser.objects.get(token=auth).token

    return username, token


def youtube_login(request):
    global yt_auth

    yt = YoutubeMusic()
    yt_auth = yt

    return redirect('login')
