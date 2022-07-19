from typing import Optional

import tekore as tk
from flask import current_app
from fuzzywuzzy import fuzz
from tekore._model import FullArtist, FullArtistOffsetPaging

from uncover import cache
from uncover.music_apis.spotify_api.spotify_client_api import get_spotify_tekore_client


@cache.memoize(timeout=3600)
def get_artist_spotify_name_by_name(artist_name: str) -> Optional[str]:
    """
    gets Spotify's version of a given artist name
    :param artist_name: original/given artist name
    :return: Spotify version of artist's name (e.g. Chinese names → English names, transliterated Russian, etc)
    """
    if not artist_name:
        return None
    client_id = current_app.config['SPOTIFY_CLIENT_ID']
    client_secret = current_app.config['SPOTIFY_CLIENT_SECRET']

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
def spotify_get_artists_genres(artist_spotify_entry: FullArtist) -> list[str]:
    """
    gets artist's top music genres
    :return:
    """
    return artist_spotify_entry.genres


def get_spotify_artist_info(artist_name: str, tekore_client: tk.Spotify = None) -> Optional[FullArtist]:
    """get spotify ID for an artist (via tekore library)

    Args:
        artist_name (str): artist's name
        tekore_client (optional): an instance of a Spotify client. Defaults to None.

    Returns:
        (tekore.FullArtist): tekore.FullArtist (Artist info object)
    """
    if not artist_name:
        return None
    # if tekore client is not provided, get a new one
    if not tekore_client:
        spotify_tekore_client = get_spotify_tekore_client()
    else:
        spotify_tekore_client = tekore_client
    artists_found = get_artist_id_search_results(
        artist_name, spotify_tekore_client)
    if not artists_found:
        return None
    perfect_match = find_artist_best_match(artist_name, artists_found.items)
    if not perfect_match:
        return None
    return perfect_match


def get_artist_id_search_results(artist_name: str, spotify_tekore_client: tk.Spotify) \
        -> Optional[FullArtistOffsetPaging]:
    """
    search for a particular artist on spotify
    :param artist_name: artist's name
    :param spotify_tekore_client: an instance of a Spotify client. Defaults to None.
    :return: artists found (max=50)
    """
    artists_found, = spotify_tekore_client.search(
        query=artist_name, types=('artist',), market="GE", limit=50)
    # in case of not getting any response
    if not artists_found:
        print("search for track failed")
        return None
    if artists_found.total == 0:
        # no tracks found whatsoever
        return None
    return artists_found


def find_artist_best_match(artist_name: str, search_results: list[FullArtist]) -> Optional[FullArtist]:
    """find the most appropriate (best) match amongst all the search results for an artist id to find

    :param artist_name: artist's name
    :param search_results: a list of all the search results
    :return: perfect match if found
    """
    print(
        f"searching for Artist({artist_name}) among {len(search_results)} results")
    print([result.name for result in search_results])
    first_result = search_results[0]
    print(f"first result: {first_result}")
    artist_name = artist_name.lower()
    if not artist_name.isascii():
        print('non-latin artist name')
        return first_result
    matches = []
    for index, artist in enumerate(search_results):
        print(index, artist.name)
        # find the right one
        if artist.name.lower() == artist_name:
            return artist
        ratio = fuzz.ratio(artist.name.lower(), artist_name)
        print(ratio)
        if ratio > 95:
            print(f"pretty close: {artist.name} vs. {artist_name}")
            return artist
        if ratio > 90:
            matches.append((artist, ratio))
    if matches:
        try:
            # pick with the highest ratio
            return sorted(matches, key=lambda x: x[1], reverse=True)[0][0]
        except IndexError as e:
            print(e)
            return None
    return first_result
