import difflib
import html
import os

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic

from transfer.vars import client_id, redirect_uri, client_secret

path = os.path.dirname(os.path.realpath(__file__)) + os.sep
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


class Spotify:

    def __init__(self):
        self.client_secret = client_secret
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.sp, self.username, self.token = None, None, None

    def auth(self):
        self.sp, self.username, self.token = self.authorisation()

    def auth_with_token(self, username, token):
        self.sp, self.username, self.token = self.authorisation_with_token(username, token)

    def build_results(self, tracks):
        results = []
        for track in tracks['items']:
            if track['track'] is not None:
                duration = track["track"]["duration_ms"]
                minutes = int((duration / 1000) // 60)
                sec = int(duration / 1000 - 60 * minutes)
                results.append({
                    'artist': ' '.join([artist['name'] for artist in track['track']['artists']]),
                    'name': track['track']['name'],
                    'album': track['track']['album']['name'],
                    'duration': f'{minutes}:{sec}'
                })

        return results

    def get_spotify_playlist(self, url):
        url_parts = url.split('/')
        playlist_id = url_parts[4].split('?')[0]
        if len(playlist_id) != 22:
            raise Exception('Bad playlist id: ' + playlist_id)

        results = self.sp.playlist(playlist_id)
        name = results['name']
        tracks = self.build_results(results['tracks'])

        count = 1
        more = len(results['tracks']['items']) == 100
        while more:
            items = self.sp.playlist_items(playlist_id, offset=count * 100, limit=100)
            print('requested from ' + str(count * 100))
            tracks += self.build_results(items)
            more = len(items["items"]) == 100
            count = count + 1

        return {'tracks': tracks, 'name': name, 'description': html.unescape(results['description'])}

    def get_playlist(self, playlist_id):
        """
        Метод считывает плейлист по id и возвращает json-файл со всем данными о плейлисте.
        :param playlist_id: id плейлиста
        :return:
        """
        # playlist = {'playlist_name': [{'track_name': 'name', 'artist_name': 'name'}, {...}, ]
        playlist_name = self.sp.playlist(playlist_id=playlist_id)['name']
        quantity = self.sp.playlist_items(playlist_id=playlist_id)['total']
        tracks = {playlist_name: []}

        if quantity >= 100:
            for i in range(quantity // 100):
                playlist_tracks = self.sp.playlist_items(playlist_id=playlist_id, limit=100, offset=i * 100)['items']

                for j in range(len(playlist_tracks)):
                    tracks[playlist_name].append({'track_name': playlist_tracks[j]['track']['name'],
                                                  'artist_name': playlist_tracks[j]['track']['artists'][0]['name']})

            playlist_tracks = self.sp.playlist_items(playlist_id=playlist_id, limit=100,
                                                     offset=quantity - quantity // 100 * 100)['items']

        playlist_tracks = self.sp.playlist_items(playlist_id=playlist_id, limit=100,
                                                 offset=quantity // 100 * 100)['items']

        for j in range(quantity - quantity // 100 * 100):
            tracks[playlist_name].append({'track_name': playlist_tracks[j]['track']['name'],
                                          'artist_name': playlist_tracks[j]['track']['artists'][0]['name']})

        return tracks

    def get_user_playlists(self, user=''):
        if user == '':
            user = self.username

        pl = []
        # print(self.sp.user_playlists(user))
        for i in range(self.sp.user_playlists(user)['total']):
            pl.append({'name': self.sp.user_playlists(user)['items'][i]['name'],
                       'id': self.sp.user_playlists(user)['items'][i]['id'],
                       'img': self.sp.user_playlists(user)['items'][i]['images'][0]['url']})

        return pl

    def get_track_id(self, query):
        track_id = self.sp.search(q=query, limit=1, type='track')
        return track_id['tracks']['items'][0]['id'].split()

    def authorisation(self):
        scope = (
            'user-library-read, playlist-read-private, playlist-modify-private, playlist-modify-public, '
            'user-read-private, user-library-modify, user-library-read')
        sp_oauth = SpotifyOAuth(self.client_id, self.client_secret, self.redirect_uri, scope=scope)

        code = sp_oauth.get_auth_response(open_browser=True)
        token = sp_oauth.get_access_token(code, as_dict=False)

        sp = spotipy.Spotify(auth=token)
        print(sp.current_user())
        username = sp.current_user()['id']
        print(username)

        return sp, username, token

    def authorisation_with_token(self, username, token):
        sp = spotipy.Spotify(auth=token)
        username = username

        return sp, username, token

    def transfer_playlists(self, playlist):
        playlist_name = list(playlist.keys())[0]
        create_spotify_playlist = self.sp.user_playlist_create(self.username, playlist_name)

        new_spotify_playlist_id = create_spotify_playlist['id']
        number_of_tracks = range(len(playlist[playlist_name]))
        tracks = []
        banned_tracks = []

        query = ''
        for i in number_of_tracks:
            try:
                artist_name = playlist[playlist_name][i]['artist']
                track_name = playlist[playlist_name][i]['name']
                query = ' '.join([artist_name, track_name])
                tracks += (self.get_track_id(query))
                print(query)
            except IndexError:
                banned_tracks.append(query)

        tracks_number = len(tracks)
        if tracks_number <= 100:
            self.sp.playlist_add_items(playlist_id=new_spotify_playlist_id, items=tracks)
        else:
            ind = 0
            for i in range(tracks_number // 100):
                self.sp.playlist_add_items(playlist_id=new_spotify_playlist_id, items=tracks[i * 100:(i + 1) * 100])
                ind = i

            if tracks_number % 100 != 0:
                self.sp.playlist_add_items(playlist_id=new_spotify_playlist_id, items=tracks[(ind + 1) * 100:])

        # for i in range(len(tracks)):
        #     self.sp.playlist_add_items(playlist_id=new_spotify_playlist_id, items=tracks[i])


class YoutubeMusic:
    def __init__(self):
        self.yt_music = YTMusic('transfer/headers_auth.json')

    def create_playlist(self, name, info, privacy="PRIVATE"):
        return self.yt_music.create_playlist(name, info, privacy)

    def add_playlist_items(self, playlist_id, video_ids):
        self.yt_music.add_playlist_items(playlist_id, video_ids, duplicates=True)

    def get_playlist_id(self, name):
        pl = self.yt_music.get_library_playlists()
        try:
            playlist = next(x for x in pl if x['title'].find(name) != -1)['playlistId']
            return playlist
        except:
            raise Exception("Playlist title not found in playlists")

    def setup(self):
        self.yt_music = YTMusic().setup(filepath='headers_auth.json', headers_raw="""accept: */*
accept-encoding: gzip, deflate, br
accept-language: ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7
authorization: SAPISIDHASH 1649916342_13c00b7203887059e1642c058983171432f310f9
content-length: 2040
content-type: application/json
cookie: YSC=U4URT0xAvJg; VISITOR_INFO1_LIVE=KdmTLt5QwAM; _gcl_au=1.1.177957342.1649916255; SID=JQi-7NIgEBgrkOlF-aBnIYl3e4saJSwo4JIbnVRUVb5MXa3tosA0e3_81-if5uLptTXVWA.; __Secure-1PSID=JQi-7NIgEBgrkOlF-aBnIYl3e4saJSwo4JIbnVRUVb5MXa3tnI9YFIjmtPp4_-JzjYt-QA.; __Secure-3PSID=JQi-7NIgEBgrkOlF-aBnIYl3e4saJSwo4JIbnVRUVb5MXa3tWcJQvE8713Kpn-ZaDnnVwA.; HSID=AvdTXwaq_CNKxk9Wj; SSID=Aga75fNtdq5fulv72; APISID=GLo2IN7LXAfG4-B_/AkouWqkYvP-Tjg3N9; SAPISID=n51Ui_Xo9NExJNmG/AsWuNH8bXpJMEe9I4; __Secure-1PAPISID=n51Ui_Xo9NExJNmG/AsWuNH8bXpJMEe9I4; __Secure-3PAPISID=n51Ui_Xo9NExJNmG/AsWuNH8bXpJMEe9I4; LOGIN_INFO=AFmmF2swRgIhAKrLzjBhsS1JqYmFweb3hYKZCW06x669Gesd8dvYkAzMAiEAtRbjCCw49yq57JsM6kTkMyHyy-8T1a2DH11CXgmPmlw:QUQ3MjNmeDhxODZHQXQ4emVJMmNBb1FYYUdWS1U4MHhIR0lxUGRYU0daY09TMUxuTzRyZm9CU3FDSHlsTzlPUXMzeVNWRkRCNnpGTnVkajBYWjhKZHRlekVLMkk1VFJxYkw3NXljdy1XOU9KZFNDdUhMaGJibHkyODNaU2daZnNyc2dDWG5henlvWkJILUQtdFV0dHZhbkVXcnc3aTlCWmNn; SIDCC=AJi4QfEDU5zqoJBau9tDjwqAVd1vlC_ecwVF9pRP10H8YyKkQZkG-_ue7UAuFRDPtlO5Sdsk; __Secure-3PSIDCC=AJi4QfGScnGiMO7A_eLI_QwkPES-_1bYtZObmuI9G8WaDLWp_SR44KT2J-jvPPbxHMzyYfhJKg; PREF=tz=Asia.Krasnoyarsk&f6=40000000&f4=4000000&library_tab_browse_id=FEmusic_liked_playlists
origin: https://music.youtube.com
referer: https://music.youtube.com/library/playlists
sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="100", "Microsoft Edge";v="100"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
sec-fetch-dest: empty
sec-fetch-mode: same-origin
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.39
x-goog-authuser: 0
x-goog-visitor-id: CgtLZG1UTHQ1UXdBTSj58t6SBg%3D%3D
x-origin: https://music.youtube.com
x-youtube-client-name: 67
x-youtube-client-version: 1.20220411.01.00""")

    def search_songs(self, tracks):
        video_ids = []
        songs = list(tracks)
        not_found = list()
        for i, song in enumerate(songs):
            query = song['name'] + ' ' + song['artist']
            query = query.replace(" &", "")
            result = self.yt_music.search(query)

            if len(result) == 0:
                not_found.append(query)
            else:
                target_song = self.get_best_fit_song_id(result, song)
                if target_song is None:
                    not_found.append(query)
                else:
                    video_ids.append(target_song)

            if i > 0 and i % 10 == 0:
                print(str(i) + ' searched')

        with open(path + 'noresults_youtube.txt', 'w', encoding="utf-8") as f:
            f.write("\n".join(not_found))
            f.close()

        return video_ids

    def get_best_fit_song_id(self, results, song):
        match_score = {}
        title_score = {}
        for res in results:
            try:
                if res['resultType'] not in ['song', 'video']:
                    continue

                duration_items = res['duration'].split(':')
                spotify_duration_items = song['duration'].split(':')
                duration = int(duration_items[0]) * 60 + int(duration_items[1])
                spotify_duration = int(spotify_duration_items[0]) * 60 + int(spotify_duration_items[1])
                duration_match = 1 - abs(duration - spotify_duration) * 2 / spotify_duration

                title = res['title']
                if res['resultType'] == 'video':
                    title_split = title.split('-')
                    if len(title_split) == 2:
                        title = title_split[1]

                title_score[res['videoId']] = difflib.SequenceMatcher(a=title.lower(), b=song['name'].lower()).ratio()

                scores = [duration_match * 5, title_score[res['videoId']],
                          difflib.SequenceMatcher(a=res['artists'][0]['name'].lower(),
                                                  b=song['artist'].lower()).ratio()]

                if res['resultType'] == 'song' and 'album' in res:
                    scores.append(
                        difflib.SequenceMatcher(a=res['album']['name'].lower(), b=song['album'].lower()).ratio())

                match_score[res['videoId']] = sum(scores) / (len(scores) + 1) * \
                                              max(1, int(res['resultType'] == 'song') * 1.5)
            except:
                print(f'Ошибка {res}')

        if len(match_score) == 0:
            return None

        max_score = max(match_score, key=match_score.get)
        return max_score

    def playlist_to_transfer(self, playlist):
        playlist = self.yt_music.get_playlist(playlist)
        tracks = playlist['tracks']
        print(tracks)

        tracks_to_transfer = {playlist['title']: []}
        for i in range(playlist['trackCount']):
            if tracks[i] is not None:
                name = tracks[i]['title']
                artist = tracks[i]['artists'][0]['name']
                if tracks[i]['album'] is not None:
                    album = tracks[i]['album']['name']
                duration = tracks[i]['duration']

                tracks_to_transfer[playlist['title']].append(
                    {'name': name,
                     'artist': artist,
                     'album': album,
                     'duration': duration}
                )

        return tracks_to_transfer
