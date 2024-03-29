import json
from typing import Optional

import aiohttp

from uncover import cache
from uncover.music_apis.lastfm_api.lastfm_client_api import lastfm_get_response, lastfm_fetch_response


@cache.memoize(timeout=60000)
def lastfm_get_album_listeners(album_title: str, artist: str) -> Optional[int]:
    """
    gets the number of listeners of a particular album; used as a metric for album's rating
    :param album_title: album's title
    :param artist: artist's name
    :return: (int) number of album listeners on last.fm
    """
    if not album_title or not artist:
        return None
    album_title = album_title.lower()
    response = lastfm_get_response({
        'method': ' album.getInfo',
        'album': album_title,
        'artist': artist
    })
    if not response:
        return None
    # in case of an error, return None
    if response.status_code != 200:
        print(f"couldn't find {album_title} on last.fm")
        return None
    try:
        album_listeners = response.json()['album']['listeners']
    except (KeyError, TypeError, json.decoder.JSONDecodeError) as e:
        print(e)
        print(f"there are no listeners for {album_title}")
        return None
    return int(album_listeners)


async def lastfm_fetch_album_listeners(album: str, artist: str, session: aiohttp.ClientSession) -> Optional[int]:
    """
    gets the number of listeners of a particular album
    :param album: album's title
    :param artist: artist's name
    :param session: aiohttp.ClientSession
    :return: (int) number of listeners on last.fm for an a particular album
    """
    if not album or not artist:
        return None
    response = await lastfm_fetch_response({
        'method': ' album.getInfo',
        'album': album,
        'artist': artist
    }, session)
    # in case of an error, return None
    if not response:
        return None
    try:
        album_listeners = response['album']['listeners']
    except KeyError as e:
        print(e)
        print(f"there are no listeners for {album}")
        return None
    return int(album_listeners)
