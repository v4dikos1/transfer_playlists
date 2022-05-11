from django.urls import path
from .views import *


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('playlists/', PlaylistsView.as_view(), name='playlists'),
    path('spotify/', spotify_login, name='spotify_login'),
    path('login/', LoginView.as_view(), name='login'),
    path('spotify-login/', spotify_login, name='spotify_login'),
    path('youtube-login/', youtube_login, name='youtube_login'),
    path('transfer/', transfer_playlist, name='transfer_playlist')
]
