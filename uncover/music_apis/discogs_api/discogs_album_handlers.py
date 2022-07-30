from typing import Optional

from discogs_client.exceptions import DiscogsAPIError

from uncover import cache
from uncover.music_apis.discogs_api.discogs_client_api import get_discogs_client


@cache.memoize(timeout=3600)
def get_album_discogs_id(album_name: str, artist_name: str):
    """
    :param artist_name: artist's name
    :param album_name: album name
    :return: discogs ID for the album
    """
    discogs = get_discogs_client()
    try:
        album_search_results = discogs.search(album_name, type='release', artist=artist_name)
    except DiscogsAPIError as e:
        print(e)
        return None
    try:
        album_id = album_search_results[0].id
    except (IndexError, AttributeError) as e:
        print(e)
        return None
    return album_id


@cache.memoize(timeout=3600)
def discogs_get_album_image(album_discogs_id: str) -> Optional[str]:
    """
    get album image url given album id (album id on discogs)
    :param album_discogs_id: album's discogs id
    :return: (str) album image url
    """
    discogs = get_discogs_client()
    album_image_uri = None
    if not album_discogs_id:
        return None
    try:
        release_info = discogs.release(album_discogs_id)
    except DiscogsAPIError as e:
        print(e)
        return None
    try:
        album_images = release_info.images
        if album_images:
            # the first image is is the primary image found on the Release page
            album_image_uri = album_images[0]['uri']
    except (AttributeError, KeyError, IndexError, TypeError) as e:
        print(e)
        return None
    return album_image_uri
