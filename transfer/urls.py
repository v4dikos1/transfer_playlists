from django.urls import path

from .views import *

urlpatterns = [
    # path('playlists/', PlaylistsView.as_view(), name='playlists'),
    path('spotify/', spotify_login, name='spotify_login'),
    path('', LoginView.as_view(), name='login'),
    path('spotify-login/', spotify_login, name='spotify_login'),
    path('youtube-login/', youtube_login, name='youtube_login'),
    path('transfer/', transfer_playlist, name='transfer_playlist'),
    path('get-songs/', get_songs, name='get_songs'),
    path('get-playlists/', get_playlists, name='get_playlists'),
    path('songs/<str:playlist_id>/', TracksView.as_view(), name='songs')
]
