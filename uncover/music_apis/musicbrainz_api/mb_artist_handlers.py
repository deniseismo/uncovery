import asyncio
import random
from datetime import datetime
from pprint import pprint

import aiohttp
import musicbrainzngs
import requests
from flask import current_app

from uncover.music_apis.lastfm_api.lastfm_album_handlers import lastfm_get_album_listeners, lastfm_fetch_album_listeners
from uncover.music_apis.musicbrainz_api.mb_album_handlers import mb_get_album_alternative_name, \
    mb_get_album_release_date, mb_fetch_album_release_date, mb_fetch_album_alternative_name
from uncover.utilities.name_filtering import get_filtered_name, get_filtered_names_list, fix_artist_name


def mb_get_artist_mbid(artist_name: str):
    """
    get artist's MusicBrainz ID
    :param artist_name:
    :return:
    """
    artist_name_fixed = fix_artist_name(artist_name).lower()
    artists_found = musicbrainzngs.search_artists(artist_name, limit=4)
    mbid = None
    if not artists_found['artist-count']:
        # nothing found
        return None
    for artist in artists_found['artist-list']:
        found_artist_name_fixed = fix_artist_name(artist['name']).lower()
        if found_artist_name_fixed == artist_name_fixed:
            mbid = artist['id']
            return mbid
    print(f'found artists mbid: {mbid}')
    return None


def mb_get_artist_mbid_backup(artist_name: str):
    """
    search for an artist's mbid on MusicBrainz
    :param artist_name: artist's name (e.g. MGMT, The Prodigy, etc.)
    :return: mbid (MusicBrainz ID)
    """
    musicbrainzngs.set_useragent(*current_app.config['MUSIC_BRAINZ_USER_AGENT'].split(','))
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    url = "http://musicbrainz.org/ws/2/artist/"
    params = {"query": "artist:" + artist_name, "limit": "10", "fmt": "json"}
    response = requests.get(url=url, params=params, headers=headers)
    if response.status_code != 200:
        return None
    try:
        artist_name_fixed = fix_artist_name(artist_name).lower()
        mbid = musicbrainzngs.search_artists(artist_name, limit=2)["artist-list"][0]['id']
        print(f'mbid found with ngs: {mbid}')
        for artist_obj in response.json()['artists']:
            # go deep in case of some discrepancies or bugs
            object_fixed = fix_artist_name(artist_obj['name']).lower()
            if artist_name_fixed == object_fixed:
                try:
                    mbid = artist_obj['id']
                    break
                except (IndexError, KeyError):
                    continue
    except (KeyError, IndexError):
        mbid = mb_get_artist_mbid_v2(artist_name)
    if not mbid:
        return None
    return mbid


def mb_get_artist_mbid_v2(artist: str):
    """
    a backup search for an artist's mbid
    :param artist: artist's name
    :return: mbid
    """
    url = "http://musicbrainz.org/ws/2/artist/"
    params = {"query": artist, "limit": "1", "fmt": "json"}
    response = requests.get(url=url, params=params)
    if response.status_code != 200:
        return None
    try:
        mbid = response.json()["artists"][0]["id"]
    except (KeyError, IndexError):
        return None
    return mbid


def mb_get_artists_albums(artist: str, sorting="popular", limit=9):
    """
    :param limit: a number of albums retrieved
    :param sorting: sorting by: popularity, release date, random
    :param artist: artist's name
    :return:
    """
    ORDER = {
        "popular": ("rating", True),
        "latest": ("release_date", True),
        "earliest": ("release_date", False)
    }
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

    albums = []
    # initialize a set of titles used to filter duplicate titles
    a_set_of_titles = set()
    for release in response.json()["release-groups"]:
        alternative_name = mb_get_album_alternative_name(release['id'])
        full_title = release['title'].replace("’", "'")
        print(full_title)
        correct_title = full_title.lower()
        rating = lastfm_get_album_listeners(correct_title, artist)
        filtered_name = get_filtered_name(full_title)
        an_album_dict = {
            "title": full_title,
            "names": [correct_title] + get_filtered_names_list(full_title),
            "mbid": release['id'],
            "rating": rating if rating else 0
        }
        if sorting in ["earliest", "latest"]:
            release_date = mb_get_album_release_date(release['id'])
            release_date = datetime.strptime(release_date[:4], '%Y')
            an_album_dict["release_date"] = release_date
        # add an alternative album name if exists
        if alternative_name:
            alternative_name = alternative_name.replace("“", "").replace("”", "")
            an_album_dict['altenative_name'] = alternative_name
            an_album_dict["names"] += alternative_name
            an_album_dict["names"] += get_filtered_names_list(alternative_name)

        # filters duplicate album names
        an_album_dict['names'] = list(set(an_album_dict['names']))
        # add an album to the albums list only if it's a new one
        # if filtered_name not in a_set_of_titles:
        #     a_set_of_titles.add(filtered_name)
        #     albums.append(an_album_dict)
        albums.append(an_album_dict)
    if sorting == "shuffle":
        random.seed(datetime.now())
        random.shuffle(albums)
        return albums[:limit]
    else:
        sorted_albums = sorted(albums, key=lambda item: item[ORDER[sorting][0]], reverse=ORDER[sorting][1])
    return sorted_albums[:limit]


def mb_get_artist_albums_v2(artist: str, album_query_filter=None):
    """
    :param album_query_filter: query filter to filter out all unnecessary albums (compilations, remixes, etc)
    :param artist: artist's name
    :return:
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

    albums = {}
    pprint(response.json())
    print(f'albums found: {len(response.json()["release-groups"])}')
    pprint(response.json()["release-groups"])
    for release in response.json()["release-groups"]:
        albums[release['id']] = release['title']
    return albums


async def mb_fetch_artists_albums(artist: str, sorting="popular", limit=9):
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
    ORDER = {
        "popular": ("rating", True),
        "latest": ("release_date", True),
        "earliest": ("release_date", False)
    }
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

    albums_found = response.json()["release-groups"]
    albums = []
    # initialize a set of titles used to filter duplicate titles
    a_set_of_titles = set()
    tasks = []
    async with aiohttp.ClientSession() as session:
        for release in albums_found:
            task = asyncio.create_task(add_album(album=release,
                                                 set_of_titles=a_set_of_titles,
                                                 session=session,
                                                 albums_list=albums,
                                                 artist=artist,
                                                 sorting=sorting))
            tasks.append(task)
        await asyncio.gather(*tasks)
    if sorting == "shuffle":
        random.seed(datetime.now())
        random.shuffle(albums)
        return albums[:limit]
    else:
        sorted_albums = sorted(albums, key=lambda item: item[ORDER[sorting][0]], reverse=ORDER[sorting][1])
    print(f'inside: {albums}')
    return sorted_albums[:limit]


async def add_album(album, set_of_titles, session, albums_list, artist, sorting):
    """
    :param album: an album to add
    :param set_of_titles: a set of titles used to filter out duplicates
    :param session: aiohttp object
    :param albums_list: destination album list
    :param artist: artist's name
    :param sorting: shuffle, popular, earliest, latest, etc
    :return:
    """
    if not album or not artist:
        return None
    alternative_name = await mb_fetch_album_alternative_name(album['id'], session)
    print(alternative_name)
    full_title = album['title'].replace("’", "'")
    print(full_title)
    correct_title = full_title.lower()
    rating = await lastfm_fetch_album_listeners(correct_title, artist, session)
    print(rating)
    filtered_name = get_filtered_name(full_title)
    an_album_dict = {
        "artist_name": artist,
        "title": full_title,
        "names": [correct_title] + get_filtered_names_list(full_title),
        "mbid": album['id'],
        "rating": rating if rating else 0
    }
    if sorting in ["earliest", "latest"]:
        release_date = await mb_fetch_album_release_date(album['id'], session)
        if release_date:
            release_date = datetime.strptime(release_date[:4], '%Y')
            an_album_dict["release_date"] = release_date
        else:
            an_album_dict["release_date"] = datetime.strptime('1970', '%Y')
    if alternative_name:
        alternative_name = alternative_name.replace("“", "").replace("”", "")
        an_album_dict['altenative_name'] = alternative_name
        an_album_dict["names"] += alternative_name
        an_album_dict["names"] += get_filtered_names_list(alternative_name)

    # filters duplicate album names
    an_album_dict['names'] = list(set(an_album_dict['names']))
    # add an album to the albums list only if it's a new one
    # if filtered_name not in set_of_titles:
    #     set_of_titles.add(filtered_name)
    #     albums_list.append(an_album_dict)
    if album['id'] not in set_of_titles:
        set_of_titles.add(album['id'])
        albums_list.append(an_album_dict)
