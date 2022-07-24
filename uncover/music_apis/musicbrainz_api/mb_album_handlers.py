import json
import time
from typing import Optional

import aiohttp
import requests
from flask import current_app


def mb_get_album_alternative_name(album_mbid: str) -> Optional[str]:
    """
    gets an alternative name for the album (e. g. White Album for 'The Beatles')
    :param album_mbid: album_mbid from MusicBrainz
    :return: alternative name for an album
    """
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    url = "http://musicbrainz.org/ws/2/release-group/" + album_mbid
    params = {"inc": "ratings", "fmt": "json"}
    response = requests.get(url=url, params=params, headers=headers)
    if response.status_code != 200:
        return None
    try:
        alternative_album_name = response.json()['disambiguation']
    except (KeyError, TypeError, json.decoder.JSONDecodeError):
        return None
    return alternative_album_name


def mb_get_album_release_date(album_mbid: str) -> Optional[str]:
    """
    get album's release date
    :param album_mbid: album's mbid from MusicBrainz
    :return: (str) album release date
    """
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    url = "http://musicbrainz.org/ws/2/release-group/" + album_mbid
    params = {"fmt": "json"}
    response = requests.get(url=url, params=params, headers=headers)
    if response.status_code != 200:
        return None
    try:
        release_date = response.json()['first-release-date']
    except (KeyError, TypeError, json.decoder.JSONDecodeError):
        return None
    if not getattr(response, 'from_cache', False):
        time.sleep(1)
    return release_date


def mb_get_album_mbid(album_name: str, artist: str):
    """
    search for an album's mbid on MusicBrainz
    :param album_name: album's name
    :param artist: artist's name (e.g. MGMT, The Prodigy, etc.)
    :return: mbid (MusicBrainz ID)
    """
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    url = "http://musicbrainz.org/ws/2/release-group/?query=release:"
    OFFICIAL_STUDIO_ALBUMS_FILTER = "%20AND%20primarytype:album%20AND%20secondarytype:(-*)%20AND%20status:official&fmt=json"
    album_query_filter = f'%20AND%20artist:{artist}{OFFICIAL_STUDIO_ALBUMS_FILTER}'
    response = requests.get(url + album_name + album_query_filter, headers=headers)
    if response.status_code != 200:
        return None
    try:
        mbid = response.json()["release-groups"][0]["id"]
    except (KeyError, IndexError, TypeError, json.decoder.JSONDecodeError) as e:
        print(e)
        return None
    return mbid


def mb_get_album_image(mbid: str, size: str = 'large', fast: bool = False):
    """
    :param fast: a faster way to get the cover image
    :param mbid: mbid for an album release on MusicBrainz
    :param size: large, small, etc.
    :return: an album cover location
    """
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    # /release-group/{mbid}/front[-(250|500|1200)]
    if not mbid:
        return None
    image = None
    if fast:
        # a faster way (lower resolution)
        url = f"http://coverartarchive.org/release-group/{mbid}"
        response = requests.get(url)
        if response.status_code != 200:
            return None
        try:
            images = response.json()
            if images:
                image = images['images'][0]['thumbnails'][size]
        except (KeyError, IndexError):
            return None
    else:
        # get what's supposed to be a 'front' cover (slower but most likely gets higher quality)
        url = f"http://coverartarchive.org/release-group/{mbid}/front"
        # response = requests.get(url)
        response = requests.head(url, headers=headers)
        if response.status_code != 307:
            return None
        try:
            image = response.headers['location']
        except KeyError:
            return None
    return image


async def mb_fetch_album_release_date(album_mbid: str, session) -> Optional[str]:
    """
    fetch album's release date (ASYNC)
    :param session: ClientSession()
    :param album_mbid: album_mbid from MusicBrainz
    :return: album release date
    """
    if not album_mbid or not session:
        return None
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    url = "http://musicbrainz.org/ws/2/release-group/" + album_mbid
    params = {"fmt": "json"}
    print(f"fetching release date for: {album_mbid}")
    async with session.get(url=url, params=params, headers=headers) as response:
        if response.status != 200:
            print('status not ok')
            return None
        try:
            album_info = await response.json()
            release_date = album_info['first-release-date']
        except (KeyError, json.decoder.JSONDecodeError, TypeError) as e:
            print(e)
            return None
        if not getattr(response, 'from_cache', False):
            time.sleep(1)
        return release_date


async def mb_fetch_album_alternative_name(album_mbid: str, session: aiohttp.ClientSession) -> Optional[str]:
    """
    gets the alternative name for the album (e. g. White Album for 'The Beatles') (ASYNC)
    :param album_mbid: album_mbid from MusicBrainz
    :param session: aiohttp.ClientSession
    :return: alternative name for an album
    """
    if not album_mbid or not session:
        return None
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    url = "http://musicbrainz.org/ws/2/release-group/" + album_mbid
    params = {"inc": "ratings", "fmt": "json"}
    async with session.get(url=url, params=params, headers=headers) as response:
        if response.status != 200:
            return None
        try:
            mb_album_info = await response.json()
        except (json.decoder.JSONDecodeError, TypeError) as e:
            print(e)
            return None
        try:
            return mb_album_info['disambiguation']
        except KeyError as e:
            print(e)
            return None
