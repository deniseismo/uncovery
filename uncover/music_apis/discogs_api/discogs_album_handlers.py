from uncover import cache
from uncover.music_apis.discogs_api.discogs_client_api import get_discogs


@cache.memoize(timeout=3600)
def get_album_discogs_id(album: str, artist: str):
    """
    :param artist: artist's name
    :param album: album name
    :return: discogs ID for the album
    """
    discogs = get_discogs()
    results = discogs.search(album, type='release', artist=artist)
    try:
        album_id = results[0].id
    except (KeyError, IndexError):
        return None
    return album_id


@cache.memoize(timeout=3600)
def discogs_get_album_image(album_discogs_id: str):
    """
    :param album_discogs_id: album's discogs id
    :return:
    """
    discogs = get_discogs()
    album_image = None
    if not album_discogs_id:
        return None
    try:
        album_images = discogs.release(album_discogs_id).images
        if album_images:
            album_image = album_images[0]['uri']
    except (IndexError, KeyError, TypeError):
        return None
    return album_image
