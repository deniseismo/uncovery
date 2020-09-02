import spotipy
import requests
from spotipy.oauth2 import SpotifyClientCredentials
from uncover.helpers.musicbrainz_api import get_artists_albums, get_artists_albums_v2
from uncover.helpers.lastfm_api import get_artist_correct_name
from uncover.helpers.utils import timeit, jprint

auth_manager = SpotifyClientCredentials()
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


def get_albums_by_playlist(playlist_id: str):
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
    album_info = {"info": f"'{playlist_info['name']}' by {playlist_info['owner']['display_name']}", "albums": dict()}
    # iterate through tracks
    for track in playlist_info["tracks"]["items"]:
        album_info["albums"][track["track"]["album"]["name"]] = track["track"]["album"]["images"][0]["url"]

    return album_info


def search_an_album(album: str, artist: str):
    """
    search for an album with the query: q=album:gold%20artist:abba&type=album
    :param album: album's title
    :param artist: artist's name
    :return: album_image_url
    """
    query = "album:" + album + " artist:" + artist
    try:
        album_info = spotify.search(q=query, type="album", limit=20, market='RU')
    except spotipy.exceptions.SpotifyException:
        return None

    try:
        album_image_url = album_info["albums"]["items"][0]["images"][0]["url"]
    except IndexError:
        return None
    return album_image_url

# if "https://api.spotify.com/v1/search?query=album%3AComputerwelt+artist%3Akraftwerk&type=album&offset=0&limit=20" == "https://api.spotify.com/v1/search?query=album%3AComputerwelt+artist%3Akraftwerk&type=album&offset=0&limit=20":
#     print("equal")
#
# jprint(search_an_album('Music for Films, Volume 2', "Brian Eno"))



def get_artists_top_albums_images_via_spotify(artist: str):
    """
    get artist's album images through Spotify's API
    :param artist: artist's name
    :return:
    """
    # try correcting some typos in artist's name
    correct_name = get_artist_correct_name(artist)
    if correct_name:
        artist = correct_name
    try:
        # gets album titles
        album_titles = get_artists_albums(artist).keys()
    except AttributeError:
        return None
    if not album_titles:
        return None
    # initialize a dict to avoid KeyErrors
    album_info = {"info": artist, "albums": dict()}
    for album_title in album_titles:
        album_image = search_an_album(album_title, artist)
        if album_image:
            album_info["albums"][album_title] = album_image
    print(f'there are {len(album_info["albums"])} albums found with Spotify')
    return album_info

# G.O.O.D. Morning, G.O.O.D. Night
# 808s & Heartbreak
# Cruel Summer
# Jesus Is King
# Graduation
# My Beautiful Dark Twisted Fantasy
# The College Dropout
# Yeezus
# The Life of Pablo
# ye
# Late Registration

# print(get_artists_top_albums_images_via_spotify('Pink Floyd'))

# print(search_an_album('G.O.O.D. Morning, G.O.O.D. Night', 'Kanye West'))
