import json.decoder
import time
from typing import Optional

from uncover import cache
from uncover.music_apis.lastfm_api.lastfm_client_api import lastfm_get_response


@cache.memoize(timeout=3600)
def lastfm_get_artist_music_genres(artist_name: str) -> Optional[list[str]]:
    """
    :param artist_name: musician/band
    :return: top 3 tags from the given artist in the form of a string
    """
    response = lastfm_get_response({
        'method': 'artist.getTopTags',
        'artist': artist_name
    })
    if not response:
        return None
    # in case of an error, return None
    if response.status_code != 200:
        return None
    try:
        artist_music_genres_info = response.json()
    except json.decoder.JSONDecodeError as e:
        print(e)
        return None

    try:
        artist_music_genres = [tag['name'].lower() for tag in artist_music_genres_info['toptags']['tag'][:3]]
    except (KeyError, IndexError, TypeError) as e:
        print(e)
        return None

    artist_music_genres = list(set(artist_music_genres))
    # rate limiting
    if not getattr(response, 'from_cache', False):
        time.sleep(0.4)
    return artist_music_genres
