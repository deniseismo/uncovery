import random
import time

import requests_cache
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import uncover.helpers.lastfm_api as lastfm_api
from uncover.helpers.musicbrainz_api import mb_get_artists_albums
from uncover.helpers.utils import get_filtered_names_list, timeit

auth_manager = SpotifyClientCredentials()
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

requests_cache.install_cache()

@timeit
def spotify_get_users_playlist_albums(playlist_id: str):
    """
    :param playlist_id: spotify's playlist ID or a playlist's URL
    :return: a dict {album_title: album_image_url}
    """
    try:
        playlist_info = spotify.playlist(playlist_id)
    except spotipy.exceptions.SpotifyException:
        # Invalid playlist ID
        return None
    # initialize a dict to avoid KeyErrors
    album_info = {"info": f"'{playlist_info['name']}' by {playlist_info['owner']['display_name']}",
                  "albums": []}
    # initialize a set of titles used to filter duplicate titles
    list_of_titles = set()
    # iterate through tracks
    for track in playlist_info["tracks"]["items"]:
        name = track['track']['album']['name']
        an_album_dict = {
            "title": track['track']['album']['name'],
            "names": [name.lower()] + get_filtered_names_list(name),
            "image": track["track"]["album"]["images"][0]["url"],
            "rating": track["track"]['popularity']
        }
        an_album_dict['names'] = list(set(an_album_dict['names']))
        # filter duplicates:
        if an_album_dict['title'] not in list_of_titles:
            # append a title to a set of titles
            list_of_titles.add(an_album_dict['title'])
            # adds an album info only if a title hasn't been seen before
            album_info["albums"].append(an_album_dict)
    # shuffles a list of albums to get random results
    random.shuffle(album_info["albums"])
    album_id = 0
    for album in album_info['albums']:
        album['id'] = album_id
        album_id += 1
    return album_info


def spotify_get_album_image(album: str, artist: str):
    """
    search for an album with the query: q=album:gold%20artist:abba&type=album
    :param album: album's title
    :param artist: artist's name
    :return: album_image_url
    """
    query = "album:" + album + " artist:" + artist
    try:
        album_info = spotify.search(q=query, type="album", limit=5, market='SE')
    except spotipy.exceptions.SpotifyException:
        return None
    if not album_info:
        return None
    album_image_url = None
    for item in album_info['albums']['items']:
        if item['artists'][0]['name'].lower() == artist.lower():
            try:
                album_image_url = item['images'][0]['url']
                break
            except IndexError:
                return None
    if not album_image_url:
        return None
    return album_image_url


def spotify_get_artist_top_albums(artist: str):
    """
    get artist's album images through Spotify's API
    :param artist: artist's name
    :return:
    """
    # try correcting some typos in artist's name
    correct_name = lastfm_api.lastfm_get_artist_correct_name(artist)
    if correct_name:
        artist = correct_name
    try:
        # gets album titles
        album_titles = mb_get_artists_albums(artist).keys()
    except AttributeError:
        return None
    if not album_titles:
        return None
    # initialize a dict to avoid KeyErrors
    album_info = {"info": artist, "albums": dict()}
    for album_title in album_titles:
        album_image = spotify_get_album_image(album_title, artist)
        if album_image:
            album_info["albums"][album_title] = album_image
    print(f'there are {len(album_info["albums"])} albums found with Spotify')
    return album_info


def spotify_get_artist_id(artist_name: str):
    """
    search for an artist's id
    :param artist_name: artist's name
    :return: album_image_url
    """
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


def spotify_get_artists_genres(artist_id: str):
    """
    gets artist's top music genres
    :return:
    """
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
