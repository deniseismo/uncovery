from uncover import cache
from uncover.music_apis.lastfm_api.lastfm_client_api import lastfm_get_response, lastfm_fetch_response


@cache.memoize(timeout=60000)
def lastfm_get_album_listeners(album: str, artist: str):
    """
    gets the number of listeners of a particular album
    :param album: album's title
    :param artist: artist's name
    :return:
    """
    if not album or not artist:
        return None
    response = lastfm_get_response({
        'method': ' album.getInfo',
        'album': album,
        'artist': artist
    })
    # in case of an error, return None
    if response.status_code != 200:
        print(f"couldn't find {album} on last.fm")
        return None
    try:
        print(response.json())
        album_listeners = response.json()['album']['listeners']

    except (KeyError, IndexError, TypeError, ValueError) as e:
        print(e)
        print(f"there are no listeners for {album}")
        return None
    return int(album_listeners)


async def lastfm_fetch_album_listeners(album: str, artist: str, session):
    """
    gets the number of listeners of a particular album
    :param album: album's title
    :param artist: artist's name
    :return:
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
    except KeyError:
        print(f"there are no listeners for {album}")
        return None
    return int(album_listeners)