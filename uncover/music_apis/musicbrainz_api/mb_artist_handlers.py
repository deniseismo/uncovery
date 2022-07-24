import asyncio
from json import JSONDecodeError
from typing import Optional

import aiohttp
import musicbrainzngs
import requests
from flask import current_app

from uncover.album_processing.album_processing_helpers import sort_artist_albums, enumerate_artist_albums
from uncover.album_processing.process_albums_from_musicbrainz import process_musicbrainz_artist_albums, \
    add_processed_mb_album
from uncover.schemas.album_schema import AlbumInfo
from uncover.utilities.fuzzymatch import fuzzy_match_artist


def mb_get_artist_mbid(artist_name: str) -> Optional[str]:
    """
    get artist's MusicBrainz ID
    :param artist_name: artist's name to find mbid for
    :return: (str) MusicBrainz ID for artist
    """
    musicbrainzngs.set_useragent(*current_app.config['MUSIC_BRAINZ_USER_AGENT'].split(','))
    artists_found = musicbrainzngs.search_artists(artist_name, limit=4)

    if not artists_found['artist-count']:
        # nothing found
        return None
    for artist_found in artists_found['artist-list']:
        if fuzzy_match_artist(artist_found, artist_name, False):
            mbid = artist_found['id']
            return mbid
    return None


def mb_get_artists_albums(artist: str, sorting: str = "popular", limit: int = 9) -> Optional[list[AlbumInfo]]:
    """
    get artist's official studio albums (information about albums, no images) from MusicBrainz
    :param limit: a number of albums retrieved
    :param sorting: sorting by: popularity, release date, random
    :param artist: artist's name
    :return:(list[AlbumInfo]) a list of all the needed info about artist's albums
    """
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    artist_mbid = mb_get_artist_mbid(artist)
    print(artist_mbid)

    if not artist_mbid:
        # if nothing found
        return None
    album_query_filter = '%20AND%20primarytype:album%20AND%20secondarytype:(-*)%20AND%20status:official&limit=100&fmt=json'
    response = requests.get(
        'https://musicbrainz.org/ws/2/release-group?query=arid:'
        + artist_mbid
        + album_query_filter,
        headers=headers
    )
    # in case of an error, return None
    if response.status_code != 200:
        return None
    try:
        albums_found = response.json()["release-groups"]
    except (JSONDecodeError, KeyError) as e:
        print(e)
        return None
    processed_albums = process_musicbrainz_artist_albums(
        albums=albums_found,
        artist=artist,
        sorting=sorting,
        unique_titles_only=False
    )
    sort_artist_albums(processed_albums, sorting)
    processed_albums = processed_albums[:limit]
    enumerate_artist_albums(processed_albums)
    return processed_albums


def mb_get_artist_albums_mbids(artist: str, album_query_filter: Optional[str] = None) -> Optional[dict]:
    """
    a shortcut function to get only MusicBrainz ids for artist's albums and their respective album titles
    (used for finding new albums)
    :param album_query_filter: query filter to filter out all unnecessary albums (compilations, remixes, etc)
    :param artist: artist's name
    :return: dict {mbid: album's title}
    """
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    artist_mbid = mb_get_artist_mbid(artist)
    print(artist_mbid)

    if not artist_mbid:
        # if nothing found
        return None
    if album_query_filter is None:
        album_query_filter = '%20AND%20primarytype:album%20AND%20secondarytype:(-*)%20AND%20status:official&limit=100&fmt=json'
    response = requests.get(
        'https://musicbrainz.org/ws/2/release-group?query=arid:'
        + artist_mbid
        + album_query_filter,
        headers=headers
    )
    print(response.url)
    # in case of an error, return None
    if response.status_code != 200:
        return None
    try:
        albums_found = response.json()["release-groups"]
    except (JSONDecodeError, KeyError) as e:
        print(e)
        return None
    albums_mbids = {}
    print(f'albums found: {len(albums_found)}')
    for album_found in albums_found:
        albums_mbids[album_found['id']] = album_found['title']
    return albums_mbids


async def mb_fetch_artists_albums(artist: str, sorting: str = "popular", limit: int = 9) -> Optional[list[AlbumInfo]]:
    """
    :param limit: a number of albums retrieved
    :param sorting: sorting by: popularity, release date, random
    :param artist: artist's name
    :return:
    """
    if not artist or not sorting:
        return None
    if sorting not in ["popular", "latest", "earliest", "shuffle"]:
        return None
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}

    artist_mbid = mb_get_artist_mbid(artist)

    if not artist_mbid:
        # if nothing found
        return None
    album_query_filter = '%20AND%20primarytype:album%20AND%20secondarytype:(-*)%20AND%20status:official&limit=100&fmt=json'
    response = requests.get(
        'https://musicbrainz.org/ws/2/release-group?query=arid:'
        + artist_mbid
        + album_query_filter,
        headers=headers
    )
    # in case of an error, return None
    if response.status_code != 200:
        return None

    try:
        albums_found = response.json()["release-groups"]
    except (JSONDecodeError, KeyError) as e:
        print(e)
        return None
    processed_albums = []
    # initialize a set of titles used to filter duplicate titles
    a_set_of_titles = set()
    tasks = []
    async with aiohttp.ClientSession() as session:
        for album_found in albums_found:
            task = asyncio.create_task(
                add_processed_mb_album(
                    album=album_found,
                    set_of_titles=a_set_of_titles,
                    session=session,
                    albums_list=processed_albums,
                    artist=artist,
                    sorting=sorting)
            )
            tasks.append(task)
        await asyncio.gather(*tasks)

    sort_artist_albums(processed_albums, sorting)
    processed_albums = processed_albums[:limit]
    return processed_albums
