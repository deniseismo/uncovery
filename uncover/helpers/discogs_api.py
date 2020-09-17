import os

import discogs_client

from uncover.helpers.musicbrainz_api import mb_get_album_image

discogs = discogs_client.Client('uncover', user_token=os.environ.get('DISCOGS_USER_TOKEN'))


def get_album_discogs_id(album: str, artist: str):
    """
    :param artist: artist's name
    :param album: album name
    :return: discogs ID for the album
    """
    # TODO: fix a search with complex artist names like 'notorious b.i.g.'
    results = discogs.search(album, type='release', artist=artist)
    try:
        album_id = results[0].id
    except (KeyError, IndexError):
        return None
    return album_id


def discogs_get_album_image(album_discogs_id: str, mbid=None):
    """
    :param mbid: optional mbid as a fallback in case of missing ids from discogs
    :param album_discogs_id: album's discogs id
    :return:
    """
    if mbid:
        print('fallback function worked')
        album_image = mb_get_album_image(mbid)
        return album_image
    if not album_discogs_id:
        return None
    try:
        album_image = discogs.release(album_discogs_id).images[0]['uri']
    except Exception:
        return None
    return album_image


