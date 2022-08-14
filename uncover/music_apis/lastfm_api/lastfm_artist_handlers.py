import json
import time
from typing import Optional

import requests_cache

from uncover import cache
from uncover.music_apis.lastfm_api.lastfm_client_api import lastfm_get_response

requests_cache.install_cache()


@cache.memoize(timeout=3600)
def lastfm_get_artist_mbid(artist_name: str) -> Optional[str]:
    """
    get the MusicBrainz id through last.fm API (a backup function)
    :param artist_name: (str) artist's name
    :return: (str) artist's mbid through lastfm
    """
    response = lastfm_get_response({
        'method': 'artist.getInfo',
        'artist': artist_name
    })
    if not response:
        return None
    # in case of an error, return None
    if response.status_code != 200:
        print(f"couldn't find {artist_name} on last.fm")
        return None
    try:
        artist_mbid = response.json()['artist']['mbid']
    except (KeyError, TypeError, json.decoder.JSONDecodeError) as e:
        print(e)
        print(f"there is no mbid for {artist_name}")
        return None
    return artist_mbid


@cache.memoize(timeout=60000)
def lastfm_get_artist_correct_name(artist_name: str, delay: bool = False) -> Optional[str]:
    """
    Use the last.fm corrections data to check whether the supplied artist has a correction to a canonical artist
    :param artist_name: (str) artist's name as is
    :param delay: (bool) delay request so as not to get banned
    :return: corrected version of the artist's name
    """
    response = lastfm_get_response({
        'method': 'artist.getCorrection',
        'artist': artist_name
    })
    if not response:
        return None
    # in case of an error, return None
    if response.status_code != 200:
        return None
    try:
        correct_name = response.json()["corrections"]["correction"]["artist"]["name"]
    except (KeyError, TypeError, json.decoder.JSONDecodeError) as e:
        print(e)
        return None
    if delay:
        if not getattr(response, 'from_cache', False):
            time.sleep(0.6)
    return correct_name
