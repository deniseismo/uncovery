import os
import time
import requests
import requests_cache

requests_cache.install_cache()


def lastfm_get(payload):
    # define headers and URL
    headers = {'user-agent': os.environ.get('USER_AGENT')}
    url = 'http://ws.audioscrobbler.com/2.0/'
    # Add API key and format to the payload
    payload['api_key'] = os.environ.get('API_KEY')
    payload['format'] = 'json'
    response = requests.get(url, headers=headers, params=payload)
    return response


def get_artist_info(artist):
    response = lastfm_get({
        'method': 'artist.getInfo',
        'artist': artist
    })
    # in case of an error, return None
    if response.status_code != 200:
        return None

    return response.json()['artist']['mbid']


def lookup_tags(artist):
    """
    :param artist: musician/band
    :return: top 3 tags from the given artist in the form of a string
    """
    response = lastfm_get({
        'method': 'artist.getTopTags',
        'artist': artist
    })
    # in case of an error, return None
    if response.status_code != 200:
        return None
    tags = [tag['name'] for tag in response.json()['toptags']['tag'][:3]]

    tags_string = ', '.join(tags)

    # rate limiting
    if not getattr(response, 'from_cache', False):
        time.sleep(0.25)
    return tags_string


def get_artists_top_albums_via_lastfm(artist):
    """

    :param artist: artist's name (musician, band, etc)
    :return: a dict {album_name: album_image_url }
    """
    response = lastfm_get({
        'method': 'artist.getTopAlbums',
        'artist': artist
    })
    # in case of an error, return None
    if response.status_code != 200:
        return None
    # albums = [album['name'] for album in response.json()['topalbums']['album'][:3]]
    try:
        album_images = {
            album['name']: album['image'][3]["#text"] for album in response.json()['topalbums']['album'][:9]
            if album['image'][3]["#text"]}
    except KeyError:
        return None
    return album_images


def get_users_top_albums(username, size=3):
    """

    :param username: lastfm username
    :param size: 0 - small (34x34), 1 - medium (64x64), 2 - large (174x174), 3 - XL (300x300)
    :return: a dictionary of 9 top the username's top albums {album_name: album_image_location}
    """
    response = lastfm_get({
        'method': 'user.getTopAlbums',
        'username': username
    })
    # in case of an error, return None
    if response.status_code != 200:
        return None
    # albums = [album['name'] for album in response.json()['topalbums']['album'][:3]]

    try:
        album_images = {album['name']: album['image'][size]['#text'] for album in
                        response.json()['topalbums']['album'][:9]}
    except KeyError:
        return None
    return album_images
