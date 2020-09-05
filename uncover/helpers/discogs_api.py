import os

import discogs_client

from uncover.helpers.lastfm_api import get_artist_correct_name
from uncover.helpers.musicbrainz_api import get_artists_albums
from uncover.helpers.utils import timeit

discogs = discogs_client.Client('uncover', user_token=os.environ.get('DISCOGS_USER_TOKEN'))


def get_album_id(album: str, artist: str):
    """
    :param artist: artist's name
    :param album: album name
    :return: discogs ID for the album
    """
    results = discogs.search(album, type='release', artist=artist)
    try:
        album_id = results[0].id
    except (KeyError, IndexError):
        return None
    return album_id


def get_album_image(album_id: str):
    if not album_id:
        return None
    try:
        album_image = discogs.release(album_id).images[0]['uri']
    except Exception:
        return None
    return album_image


@timeit
def get_artist_top_albums_images_via_discogs(artist: str):
    """
    get artist's album images through Spotify's API
    :param artist: artist's name
    :return:
    """
    # try correcting some typos in artist's name
    correct_name = get_artist_correct_name(artist)
    if correct_name:
        artist = correct_name
    try:
        # gets album titles
        album_titles = get_artists_albums(artist).keys()
    except AttributeError:
        return None
    if not album_titles:
        return None
    # initialize a dict to avoid KeyErrors
    album_info = {"info": artist, "albums": dict()}
    for album_title in album_titles:
        album_id = get_album_id(album_title, artist=artist)
        album_image = get_album_image(album_id)
        if album_image:
            album_info["albums"][album_title] = album_image
    print(f'there are {len(album_info["albums"])} albums found with Discogs')
    return album_info
