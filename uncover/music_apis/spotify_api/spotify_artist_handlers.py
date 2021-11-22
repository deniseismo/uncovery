import time

import spotipy
import tekore as tk
from flask import current_app

from uncover import cache
from uncover.music_apis.spotify_api.spotify_client_api import get_spotify_tekore_client, get_spotify


@cache.memoize(timeout=3600)
def spotify_get_artist_name(artist_name):
    """
    gets Spotify's version of a given artist name
    :param artist_name: original/given artist name
    :return: Spotify version of artist's name (e.g. Chinese names → English names, transliterated Russian, etc)
    """
    if not artist_name:
        return None
    client_id = current_app.config['SPOTIPY_CLIENT_ID']
    client_secret = current_app.config['SPOTIPY_CLIENT_SECRET']

    app_token = tk.request_client_token(client_id, client_secret)
    spotify_tekore_client = get_spotify_tekore_client()
    try:
        with spotify_tekore_client.token_as(app_token):
            artists_found, = spotify_tekore_client.search(
                query=artist_name,
                types=('artist',),
                limit=10
            )
            if not artists_found:
                return None
            if not artists_found.items:
                return None
            try:
                artist_name_on_spotify = artists_found.items[0].name
                for artist_found in artists_found.items:
                    if artist_found.name.lower() == artist_name.lower():
                        artist_name_on_spotify = artist_found.name
                        return artist_name_on_spotify
            except (TypeError, IndexError):
                return None
    except tk.HTTPError:
        return None
    print(f'found spotify artist name: {artist_name_on_spotify}')
    return artist_name_on_spotify


@cache.memoize(timeout=6000)
def spotify_get_artist_id(artist_name: str):
    """
    search for an artist's id
    :param artist_name: artist's name
    :return: album_image_url
    """
    spotify = get_spotify()
    try:
        artist_info = spotify.search(q=artist_name, type="artist", limit=5, market='SE')
    except spotipy.exceptions.SpotifyException:
        return None
    if not artist_info:
        return None
    artist_id = None
    for item in artist_info['artists']['items']:
        print(item['name'].lower(), artist_name.lower())
        if item['name'].lower() == artist_name.lower():
            try:
                print('artists name are equal!')
                artist_id = item['id']
                break
            except KeyError:
                return None
    return artist_id


@cache.memoize(timeout=6000)
def spotify_get_artists_genres(artist_id: str):
    """
    gets artist's top music genres
    :return:
    """
    spotify = get_spotify()
    artist_info = spotify.artist(artist_id)
    if not artist_info:
        return None
    try:
        genres = artist_info['genres']
    except KeyError:
        return None
    if not getattr(artist_info, 'from_cache', False):
        time.sleep(0.2)
    return genres


