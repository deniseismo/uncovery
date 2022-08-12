from typing import Optional

import tekore as tk
from fuzzywuzzy import fuzz
from tekore._model import SimpleAlbumPaging, SimpleAlbum

from uncover import cache
from uncover.album_processing.album_processing_helpers import sort_artist_albums, enumerate_artist_albums
from uncover.album_processing.process_albums_from_spotify import process_spotify_artist_albums
from uncover.music_apis.lastfm_api.lastfm_artist_handlers import lastfm_get_artist_correct_name
from uncover.music_apis.spotify_api.spotify_artist_handlers import get_artist_spotify_name_by_name, \
    get_spotify_artist_info
from uncover.music_apis.spotify_api.spotify_client_api import get_spotify_tekore_client
from uncover.schemas.album_schema import AlbumInfo
from uncover.schemas.characteristics import SpotifyAlbumSearchParams, AlbumMatch
from uncover.utilities.fuzzymatch import fuzzy_match_artist
from uncover.utilities.name_filtering import get_filtered_name


@cache.memoize(timeout=3600)
def spotify_get_album_image(album_name: str, artist_name: str) -> Optional[str]:
    """
    get album's cover (image url) on spotify
    :param album_name: (str) album's title
    :param artist_name: (str) artist's name
    :return: (str) album's cover (image url)
    """
    if not artist_name:
        return None
    spotify_tekore_client = get_spotify_tekore_client()
    if not spotify_tekore_client:
        return None
    album_info = get_spotify_album_info(
        album_name=album_name,
        artist_name=artist_name,
        tekore_client=spotify_tekore_client
    )
    if not album_info:
        return None
    if not album_info.images:
        return None
    try:
        image = album_info.images[0]
        image_url = image.url
        print(f'{image_url=}')
        return image_url
    except (IndexError, AttributeError) as e:
        print(e)
        return None


@cache.memoize(timeout=3600)
def spotify_get_artists_albums(artist_name: str, sorting: str = "popular") -> Optional[list[AlbumInfo]]:
    """
    a backup function that gets all the info from Spotify
    (in case MusicBrainz has nothing about a particular artist)
    :param artist_name: (str) artist's name
    :param sorting: (str) sorted by shuffle, popular, earliest, latest
    :return: artist's albums (list[AlbumInfo]) found on spotify
    """
    spotify_tekore_client = get_spotify_tekore_client()
    if not spotify_tekore_client:
        return None
    artist_correct_name = lastfm_get_artist_correct_name(artist_name)
    if artist_correct_name:
        artist_name = artist_correct_name
    artist_spotify_entry = get_spotify_artist_info(artist_name)
    if not artist_spotify_entry:
        return None
    albums = spotify_tekore_client.artist_albums(artist_id=artist_spotify_entry.id, market="GE", limit=50)
    if not albums:
        return None
    if not albums.items:
        return None
    if albums.total == 0:
        return None
    processed_albums = process_spotify_artist_albums(albums.items)
    sort_artist_albums(processed_albums, sorting=sorting)
    enumerate_artist_albums(processed_albums)
    return processed_albums


def get_spotify_album_info(
        album_name: str,
        artist_name: str,
        spotify_artist_name: str = None,
        tekore_client: tk.Spotify = None,
        token_based: bool = False,
        country: str = None,
        token=None) -> Optional[SimpleAlbum]:
    """
    find album on spotify
    :param album_name: album's title
    :param artist_name: artist's name
    :param spotify_artist_name: artist's name on spotify
    :param tekore_client: spotify tekore client
    :param token_based: (bool) if True, get album only if user's access token specified (and on user's market (country))
    :param country: two-letter country code, spotify's market to search for an item on
    :param token: user's access token
    :return: (SimpleAlbum) album found on spotify
    """
    if not (album_name and artist_name):
        return None
    # if tekore client is not provided, get a new one
    if token_based and not token:
        print(f"token based, but no token provided")
        return None
    if not tekore_client:
        tekore_client = get_spotify_tekore_client()
    if not tekore_client:
        return None
    if token:
        print("access token provided")
        try:
            with tekore_client.token_as(token):
                albums_found = get_album_search_results(
                    album_name=album_name,
                    artist_name=artist_name,
                    spotify_tekore_client=tekore_client,
                    spotify_artist_name=spotify_artist_name,
                    country=country,
                    token_based=token_based
                )
        except tk.HTTPError:
            return None
    else:
        print("no access token, default search")
        albums_found = get_album_search_results(
            album_name=album_name,
            artist_name=artist_name,
            spotify_tekore_client=tekore_client,
            token_based=token_based
        )
    print(albums_found)
    if not albums_found:
        return None
    perfect_match = find_album_best_match(album_name, artist_name, albums_found.items)
    print(f"perfect match: {perfect_match}")
    if not perfect_match:
        return None
    return perfect_match


@cache.memoize(timeout=3600)
def find_album_best_match(
        album_title: str,
        artist_name: str,
        search_results: list[SimpleAlbum]
) -> Optional[SimpleAlbum]:
    """find the most appropriate (best) match amongst all the search results for an album to find

    :param album_title: track's title to find
    :param artist_name: artist's name
    :param search_results: a list of all the search results
    :return: perfect match if found
    """
    album_title = album_title.lower()
    print(f"searching for Album({album_title}) among {len(search_results)} results")
    matches = []
    for album in search_results:
        album_found = get_filtered_name(album.name).lower()
        correct_artist_found = fuzzy_match_artist(
            artist_name, album.artists[0].name)
        print(correct_artist_found)
        if not correct_artist_found:
            print("INCORRECT ARTIST")
            continue
        if album_found == album_title:
            print("album found: perfect match")
            return album
        print(album.name, "→", album_found, "vs.", album_title,
              fuzz.ratio(album_found, album_title), sep=" | ")
        ratio = fuzz.ratio(album_found, album_title)
        if ratio > 90:
            print(f"pretty close: {album_found} vs. {album_title}")
            return album
        if ratio > 80:
            # append a match to matches list
            matches.append(AlbumMatch(album, ratio))
    # if there are matches
    if not matches:
        return None
    best_album_match = _pick_closest_album_match(matches)
    return best_album_match


def get_album_search_results(
        album_name: str,
        artist_name: str,
        spotify_tekore_client: tk.Spotify,
        spotify_artist_name: str = None,
        country: str = None,
        token_based: bool = False
) -> Optional[SimpleAlbumPaging]:
    """
    get
    :param album_name: album's title
    :param artist_name: artist's name
    :param spotify_artist_name: artist's name on Spotify
    :param spotify_tekore_client: an instance of a Spotify client. Defaults to None.
    :param country: user's country (spotify market)
    :param token_based:
    :return: albums found (max=5)
    """
    search_params = _configure_search_params_for_spotify_album_searching(
        album_name=album_name,
        artist_name=artist_name,
        country=country,
        token_based=token_based
    )
    print(search_params)
    albums_found, = spotify_tekore_client.search(**search_params.to_dict())
    # in case of not getting any response
    if not albums_found:
        print("no albums found")
        return None
    if albums_found.total == 0:
        if not spotify_artist_name:
            print('try finding with spotify artist name')
            # try finding an album with a different (Spotify's version) artist name
            spotify_artist_name = get_artist_spotify_name_by_name(artist_name)
            if not spotify_artist_name:
                # no artist name found
                return None
        if spotify_artist_name.lower() == artist_name.lower():
            # spotify's version is the same — no need to try again
            return None
        search_params.query = f"{album_name} artist:{spotify_artist_name}"
        albums_found, = spotify_tekore_client.search(**search_params.to_dict())
        if albums_found.total == 0:
            return None
    return albums_found


def _configure_search_params_for_spotify_album_searching(
        album_name: str,
        artist_name: str,
        types: tuple[str] = ('album',),
        limit: int = 50,
        country: Optional[str] = None,
        token_based: bool = False
) -> SpotifyAlbumSearchParams:
    """
    configure search parameters for searching album on Spotify
    :param album_name: album's title
    :param artist_name: artist's name
    :param types: type of search result (type of media you search for), e.g. 'album'
    :param limit: (max=50)
    :param country: user's country (Spotify's market to search on)
    :param token_based: True/False
    :return: SpotifyAlbumSearchParams with search params configured
    """
    market = None
    if country:
        market = country
    elif token_based:
        # no country provided, but the request is token based
        market = 'from_token'
    query = f"{album_name} artist:{artist_name}"
    return SpotifyAlbumSearchParams(
        query=query,
        types=types,
        market=market,
        limit=limit
    )


def _pick_closest_album_match(album_matches: list[AlbumMatch]) -> Optional[SimpleAlbum]:
    """
    pick album with the highest ratio (closeness) among album matches
    :param album_matches: (list[AlbumMatch]) list of AlbumMatches (SimpleAlbum, ratio)
    :return: (SimpleAlbum) hopefully perfect match (album we were looking for on spotify)
    """
    try:
        return sorted(album_matches, key=lambda album_match: album_match.ratio, reverse=True)[0].album
    except (IndexError, TypeError) as e:
        print(e)
        return None
