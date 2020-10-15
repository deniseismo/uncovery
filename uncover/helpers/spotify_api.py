import random
import time
from datetime import datetime

import requests_cache
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

import uncover.helpers.lastfm_api as lastfm_api
import uncover.helpers.musicbrainz_api as musicbrainz
import uncover.helpers.utilities as utils
from uncover import cache

scope = "user-top-read"

auth_manager = SpotifyClientCredentials()
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

requests_cache.install_cache()


@utils.timeit
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
        if track['track']['album']['album_type'] == "album":
            name = track['track']['album']['name']
            filtered_title = utils.get_filtered_name(name)
            filtered_title = utils.remove_punctuation(filtered_title)
            artist_name = track['track']['album']['artists'][0]['name']
            an_album_dict = {
                "artist_name": artist_name,
                "artist_names": [artist_name] + utils.get_filtered_artist_names(artist_name),
                "title": track['track']['album']['name'],
                "names": [name.lower()] + utils.get_filtered_names_list(name),
                "image": track["track"]["album"]["images"][0]["url"],
                "rating": track["track"]['popularity']
            }
            an_album_dict["artist_names"] = list(set(an_album_dict["artist_names"]))
            an_album_dict['names'] = list(set(an_album_dict['names']))
            # filter duplicates:
            if filtered_title not in list_of_titles:
                # append a title to a set of titles
                list_of_titles.add(filtered_title)
                # adds an album info only if a title hasn't been seen before
                album_info["albums"].append(an_album_dict)
    # shuffles a list of albums to get random results
    random.shuffle(album_info["albums"])
    # adds ids to albums
    for count, album in enumerate(album_info['albums']):
        album['id'] = count
    return album_info


@cache.memoize(timeout=6000)
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
    if not getattr(album_info, 'from_cache', False):
        time.sleep(0.25)
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
        album_titles = musicbrainz.mb_get_artists_albums(artist).keys()
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


@cache.memoize(timeout=6000)
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


@cache.memoize(timeout=6000)
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


def spotify_get_artists_albums_images(artist: str, sorting="popular"):
    """
    a backup function that gets all the info from Spotify
    (in case MusicBrainz has nothing about a particular artist)
    :param artist: artist's name
    :return:
    """
    ORDER = {
        "popular": ("rating", True),
        "latest": ("release_date", True),
        "earliest": ("release_date", False)
    }
    print('finding through backup spotify')
    if not artist:
        return None
    artist_correct_name = lastfm_api.lastfm_get_artist_correct_name(artist)
    if artist_correct_name:
        artist = artist_correct_name
    artist_spotify_id = spotify_get_artist_id(artist)
    if not artist_spotify_id:
        return None
    albums = spotify.artist_albums(artist_id=artist_spotify_id, album_type="album", country="SE", limit=50)
    if not albums:
        return None
    album_info = {"info": artist, "albums": []}
    albums_list = []
    try:
        for an_album in albums['items']:
            try:
                album_image = an_album['images'][0]['url']
                if album_image:
                    album_title = an_album['name']
                    correct_title = album_title.lower()
                    rating = lastfm_api.lastfm_get_album_listeners(correct_title, artist)
                    filtered_name = utils.get_filtered_name(album_title)
                    release_date = datetime.strptime(an_album["release_date"][:4], '%Y')
                    an_album_dict = {
                        "title": album_title,
                        "image": album_image,
                        "names": [correct_title] + utils.get_filtered_names_list(album_title),
                        "rating": rating if rating else 0,
                        "release_date": release_date
                    }
                    # remove duplicates
                    an_album['names'] = list(set(an_album['names']))
                    albums_list.append(an_album_dict)

            except (KeyError, IndexError):
                continue

    except (KeyError, TypeError, IndexError) as e:
        print(e)
        return None

    if not albums_list:
        return None
    if sorting == "shuffle":
        random.seed(datetime.now())
        random.shuffle(albums_list)
        album_info['albums'] = albums_list
    else:
        album_info['albums'] = sorted(albums_list, key=lambda item: item[ORDER[sorting][0]], reverse=ORDER[sorting][1])
    for count, album in enumerate(album_info['albums']):
        album['id'] = count
    return album_info


def spotify_get_users_top_albums():
    tracks = sp.current_user_top_tracks(limit=20, offset=0, time_range='medium_term')
    for track in tracks:
        print(track)
