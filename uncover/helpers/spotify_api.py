import random

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from uncover.helpers.lastfm_api import get_artist_correct_name
from uncover.helpers.musicbrainz_api import get_artists_albums
from uncover.helpers.utils import get_filtered_names_list

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


get_albums_by_playlist('https://open.spotify.com/playlist/2qoLvXr84mMas2tOEH8gEJ?si=YoHsJME-SNCmPKP-u8LJJQ')


def search_an_album(album: str, artist: str):
    """
    search for an album with the query: q=album:gold%20artist:abba&type=album
    :param album: album's title
    :param artist: artist's name
    :return: album_image_url
    """
    query = "album:" + album + " artist:" + artist
    try:
        album_info = spotify.search(q=query, type="album", limit=1, market='SE')
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
# jprint(search_an_album('Computerwelt', "Kraftwerk"))



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
