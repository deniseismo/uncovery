import time
from datetime import datetime

import requests
from flask import current_app


def mb_get_album_alternative_name(album_id: str):
    """
    gets the alternative name for the album (e. g. White Album for 'The Beatles')
    :param album_id: album_id from MusicBrainz
    :return: alternative name for an album
    """
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    url = "http://musicbrainz.org/ws/2/release-group/" + album_id
    params = {"inc": "ratings", "fmt": "json"}
    response = requests.get(url=url, params=params, headers=headers)
    if response.status_code != 200:
        return None
    try:
        alternative = response.json()['disambiguation']
    except (KeyError, IndexError):
        return None
    return alternative


def mb_get_album_release_date(album_id: str):
    """
    :param album_id: album_id from MusicBrainz
    :return: album release date
    """
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    url = "http://musicbrainz.org/ws/2/release-group/" + album_id
    params = {"fmt": "json"}
    response = requests.get(url=url, params=params, headers=headers)
    if response.status_code != 200:
        return None
    try:
        release_date = response.json()['first-release-date']
    except (KeyError, IndexError, TypeError):
        return None
    if not getattr(response, 'from_cache', False):
        time.sleep(1)
    return release_date


def mb_get_album_mbid(album: str, artist: str):
    """
    search for an album's mbid on MusicBrainz
    :param album: album's name
    :param artist: artist's name (e.g. MGMT, The Prodigy, etc.)
    :return: mbid (MusicBrainz ID)
    """
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    url = "http://musicbrainz.org/ws/2/release-group/?query=release:"
    album_query_filter = f'%20AND%20artist:{artist}%20AND%20primarytype:album%20AND%20secondarytype:(-*)%20AND%20status:official&fmt=json'
    response = requests.get(url + album + album_query_filter, headers=headers)
    if response.status_code != 200:
        return None
    try:
        mbid = response.json()["release-groups"][0]["id"]
    except (KeyError, IndexError):
        return None
    return mbid


def mb_get_album_image(mbid: str, size='large', fast=False):
    """
    :param fast: a faster way to get the cover image
    :param mbid: mbid for an album release on MusicBrainz
    :param size: small, etc.
    :return: an album cover location
    """
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    # /release-group/{mbid}/front[-(250|500|1200)]
    if not mbid:
        return None
    image = None
    if fast:
        # a faster way (lower resolution)
        url = "http://coverartarchive.org/release-group/" + mbid
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
        url = "http://coverartarchive.org/release-group/" + mbid + '/front'
        # response = requests.get(url)
        response = requests.head(url, headers=headers)
        if response.status_code != 307:
            return None
        try:
            image = response.headers['location']
        except (KeyError, IndexError):
            return None
    return image


def parse_release_date(release_date):
    if not release_date:
        return None
    release_date = datetime.strptime(release_date[:4], '%Y')
    return release_date


async def mb_fetch_album_release_date(album_id: str, session):
    """
    ASYNC
    :param session: ClientSession()
    :param album_id: album_id from MusicBrainz
    :return: album release date
    """
    if not album_id or not session:
        return None
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    url = "http://musicbrainz.org/ws/2/release-group/" + album_id
    params = {"fmt": "json"}
    print('fetching release date for: ', album_id)
    async with session.get(url=url, params=params, headers=headers) as response:
        if response.status != 200:
            print('status not ok')
            return None
        try:
            album_info = await response.json()
            release_date = album_info['first-release-date']
        except (KeyError, IndexError, TypeError):
            print('some error occurred')
            return None
        if not getattr(response, 'from_cache', False):
            time.sleep(1)
        return release_date


async def mb_fetch_album_alternative_name(album_id: str, session):
    """
    gets the alternative name for the album (e. g. White Album for 'The Beatles')
    :param album_id: album_id from MusicBrainz
    :return: alternative name for an album
    """
    if not album_id or not session:
        return None
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    url = "http://musicbrainz.org/ws/2/release-group/" + album_id
    params = {"inc": "ratings", "fmt": "json"}
    async with session.get(url=url, params=params, headers=headers) as response:
        if response.status != 200:
            return None
        try:
            alternative = await response.json()
        except (KeyError, IndexError):
            return None
        return alternative['disambiguation']
