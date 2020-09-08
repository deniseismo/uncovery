import os

import discogs_client

from uncover.helpers.lastfm_api import get_artist_correct_name
from uncover.helpers.musicbrainz_api import get_artists_albums, get_album_image_via_mb
from uncover.helpers.utils import timeit

discogs = discogs_client.Client('uncover', user_token=os.environ.get('DISCOGS_USER_TOKEN'))


def get_album_id(album: str, artist: str):
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


def get_album_image(album_id: str, mbid=None):
    """
    :param mbid: optional mbid as a fallback in case of missing ids from discogs
    :param album_id:
    :return:
    """
    if mbid:
        print('fallback function worked')
        album_image = get_album_image_via_mb(mbid)
        return album_image
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
        print(f'the correct name is {correct_name}')
    try:
        # gets album titles
        albums = get_artists_albums(artist)
    except AttributeError:
        return None
    if not albums:
        return None
    # initialize a dict to avoid KeyErrors
    album_info = {"info": artist, "albums": []}
    for album in list(albums):
        album_id = get_album_id(album['title'], artist=artist)
        if not album_id:
            album_image = get_album_image(album_id='', mbid=album['id'])
        else:
            album_image = get_album_image(album_id)
        if album_image:
            album['image'] = album_image
    album_id = 0
    for album in albums:
        if 'image' in album:
            album['id'] = album_id
            album_info['albums'].append(album)
            album_id += 1
    if not album_info['albums']:
        print('error: no albums to show')
        return None
    print(f'there are {len(album_info["albums"])} albums found with Discogs')
    return album_info
