import random
import time
from datetime import datetime

import spotipy
import tekore as tk
from fuzzywuzzy import fuzz

from uncover import cache
from uncover.music_apis.lastfm_api.lastfm_album_handlers import lastfm_get_album_listeners
from uncover.music_apis.lastfm_api.lastfm_artist_handlers import lastfm_get_artist_correct_name
from uncover.music_apis.musicbrainz_api.mb_artist_handlers import mb_get_artists_albums
from uncover.music_apis.spotify_api.spotify_artist_handlers import spotify_get_artist_name, spotify_get_artist_id
from uncover.music_apis.spotify_api.spotify_client_api import get_spotify_tekore_client, get_spotify
from uncover.music_apis.spotify_api.spotify_user_handlers import check_spotify
from uncover.utilities.name_filtering import get_filtered_name, get_filtered_names_list


@cache.memoize(timeout=3600)
def spotify_get_album_id(album_name, artist_name, spotify_artist_name, country):
    """
    gets Spotify album id with through Tekore
    :param spotify_artist_name:
    :param country: current user's market/country for spotify
    :param album_name: album's title
    :param artist_name: artist's title
    :return: Spotify album id
    """
    print(f'country: {country}')
    artist_name = artist_name.lower().replace('the ', '')
    query = "album:" + album_name + " artist:" + artist_name
    user, token = check_spotify()
    spotify_tekore_client = get_spotify_tekore_client()
    if user and token:
        try:
            with spotify_tekore_client.token_as(token):
                # try getting the album in one go: album and artist provided
                album_info = spotify_tekore_client.search(
                    query=query,
                    types=('album',),
                    market=country if country else 'from_token',
                    limit=5
                )
                if album_info:
                    if not album_info[0].items:
                        if not spotify_artist_name:
                            print('try finding with spotify artist name')
                            # try finding an album with a different (Spotify's version) artist name
                            spotify_artist_name = spotify_get_artist_name(artist_name)
                            if not spotify_artist_name:
                                # no artist name found
                                return None
                        if spotify_artist_name.lower() == artist_name.lower():
                            # spotify's version is the same — no need to try again
                            return None
                        query = f"album:{album_name} artist:{spotify_artist_name}"
                        album_info = spotify_tekore_client.search(
                            query=query,
                            types=('album',),
                            market=country if country else 'from_token',
                            limit=5
                        )
        except tk.HTTPError:
            return None
        if not album_info:
            return None
        print(len(album_info[0].items))
        album_items = album_info[0].items
        if not album_items:
            return None
        artist_name = artist_name.lower().replace(' & ', ' and ')
        album_name = get_filtered_name(album_name)
        ratio_threshold = 94
        album_id_found = None
        for album in album_items:
            print(album.name)
            try:
                current_artist = album.artists[0].name. \
                    lower().replace(' & ', ' and ').replace('the ', '')
                current_album = get_filtered_name(album.name)
                print(current_artist)
                print(current_album)
                print(artist_name)
                current_artist_ratio = fuzz.ratio(artist_name, current_artist)
                print(current_artist_ratio)
                current_album_ratio = fuzz.ratio(album_name, current_album)
                if current_album_ratio > 98 and current_artist_ratio > 85:
                    # found perfect match, return immediately
                    return album.id
                elif current_album_ratio > ratio_threshold and current_artist_ratio > 85:
                    ratio_threshold = current_album_ratio
                    album_id_found = album.id
            except (KeyError, TypeError, IndexError):
                continue
        return album_id_found
    return None


@cache.memoize(timeout=6000)
def spotify_get_album_image(album: str, artist: str):
    """
    search for an album with the query: q=album:gold%20artist:abba&type=album
    :param album: album's title
    :param artist: artist's name
    :return: album_image_url
    """
    spotify = get_spotify()
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


def spotipy_get_album_id(album: str, artist: str):
    """
    search for an album's id
    :param album: album's title
    :param artist: artist's name
    :return: album id
    """
    if not album or not artist:
        return None
    spotify = get_spotify()
    query = "album:" + album + " artist:" + artist
    try:
        album_info = spotify.search(q=query, type="album", limit=5, market='RU')
    except spotipy.exceptions.SpotifyException:
        return None
    if not album_info:
        return None
    try:
        album_items = album_info['albums']['items']
    except (KeyError, TypeError, IndexError):
        return None
    if not album_items:
        return None
    for album in album_items:
        try:
            artist_name = album['artists'][0]['name']
            album_id = album['id']
            if fuzz.ratio(artist_name, artist) > 90:
                return album_id
        except (KeyError, TypeError, IndexError):
            continue
    if not getattr(album_info, 'from_cache', False):
        time.sleep(1)
    return None


def get_artist_mb_albums_cover_arts_through_spotify(artist: str):
    """
    get artist's album images through Spotify's API
    :param artist: artist's name
    :return:
    """
    # try correcting some typos in artist's name
    correct_name = lastfm_get_artist_correct_name(artist)
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
    album_info = {
        "info": {
            "type": "artist",
            "query": artist
        },
        "albums": dict()
    }
    for album_title in album_titles:
        album_image = spotify_get_album_image(album_title, artist)
        if album_image:
            album_info["albums"][album_title] = album_image
    print(f'there are {len(album_info["albums"])} albums found with Spotify')
    return album_info


def spotify_get_artists_albums_images(artist: str, sorting="popular"):
    """
    a backup function that gets all the info from Spotify
    (in case MusicBrainz has nothing about a particular artist)
    :param sorting: sorted by shuffle, popular, earliest, latest
    :param artist: artist's name
    :return:
    """
    spotify = get_spotify()
    ORDER = {
        "popular": ("rating", True),
        "latest": ("release_date", True),
        "earliest": ("release_date", False)
    }
    print('finding through backup spotify')
    if not artist:
        return None
    artist_correct_name = lastfm_get_artist_correct_name(artist)
    if artist_correct_name:
        artist = artist_correct_name
    artist_spotify_id = spotify_get_artist_id(artist)
    if not artist_spotify_id:
        return None
    albums = spotify.artist_albums(artist_id=artist_spotify_id, album_type="album", country="SE", limit=50)
    if not albums:
        return None
    album_info = {
        "info": {
            "type": "artist",
            "query": artist
        },
        "albums": []
    }
    a_set_of_titles = set()
    albums_list = []
    try:
        for an_album in albums['items']:
            try:
                album_image = an_album['images'][0]['url']
                if album_image:
                    album_title = an_album['name']
                    filtered_name = get_filtered_name(album_title)
                    if filtered_name not in a_set_of_titles:
                        a_set_of_titles.add(filtered_name)
                        correct_title = album_title.lower()
                        rating = lastfm_get_album_listeners(correct_title, artist)
                        print(f'rating: {rating}')
                        print(f'filtered_name: {filtered_name}')
                        print('test!jke')
                        release_date = datetime.strptime(an_album["release_date"][:4], '%Y')
                        an_album_dict = {
                            "artist_name": artist,
                            "title": album_title,
                            "image": album_image,
                            "names": [correct_title] + get_filtered_names_list(album_title),
                            "rating": rating if rating else 0,
                            "release_date": release_date
                        }
                        # remove duplicates
                        an_album_dict['names'] = list(set(an_album_dict['names']))
                        albums_list.append(an_album_dict)

            except (KeyError, IndexError) as e:
                print(e)
                print('some key or index error exception occurred')
                continue

    except (KeyError, TypeError, IndexError) as e:
        print('some spotify error occurred!')
        print(e)
        return None

    if not albums_list:
        print('no album list')
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
