import json

from uncover import cache
from uncover.music_apis.lastfm_api.lastfm_client_api import lastfm_get_response


def lastfm_get_artist_mbid(artist: str):
    """
    get the MusicBrainz id through last.fm API (a backup function)
    :param artist: artist's name
    :return: MusicBrainz ID
    """
    response = lastfm_get_response({
        'method': 'artist.getInfo',
        'artist': artist
    })
    # in case of an error, return None
    if response.status_code != 200:
        print(f"couldn't find {artist} on last.fm")
        return None
    try:
        artist_mbid = response.json()['artist']['mbid']
    except KeyError:
        print(f"there is no mbid for {artist}")
        return None
    return artist_mbid


@cache.memoize(timeout=60000)
def lastfm_get_artist_correct_name(artist: str):
    """
    Use the last.fm corrections data to check whether the supplied artist has a correction to a canonical artist
    :param artist: artist's name as is
    :return: corrected version of the artist's name
    """
    print('getting artist correction')
    response = lastfm_get_response({
        'method': 'artist.getCorrection',
        'artist': artist
    })
    # in case of an error, return None
    if response.status_code != 200:
        return None
    try:
        correct_name = response.json()["corrections"]["correction"]["artist"]["name"]
    except (KeyError, TypeError, json.decoder.JSONDecodeError):
        return None
    return correct_name