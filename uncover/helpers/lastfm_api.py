import os
import time
import requests
import requests_cache
from uncover.helpers.utils import jprint

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
    # TODO: if an artist has no mbid on lastfm, find it on mb directly, or get images from lastfm
    response = lastfm_get({
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


def get_artist_correct_name(artist):
    """
    Use the last.fm corrections data to check whether the supplied artist has a correction to a canonical artist
    :param artist: artist's name as is
    :return: corrected version of the artist's name
    """
    response = lastfm_get({
        'method': 'artist.getCorrection',
        'artist': artist
    })
    # in case of an error, return None
    if response.status_code != 200:
        return None
    try:
        correct_name = response.json()["corrections"]["correction"]["artist"]["name"]
    except KeyError:
        return None
    jprint(response.json())
    return correct_name


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


def get_artists_top_albums_via_lastfm(artist, size=3, amount=9):
    """
    :param amount: a number of albums, default = 9
    :param size: 3 - large size (300x300)
    :param artist: artist's name (musician, band, etc)
    :return: a dict {album_name: album_image_url}
    """
    # try correcting some typos in artist's name
    correct_name = get_artist_correct_name(artist)
    if correct_name:
        artist = correct_name

    response = lastfm_get({
        'method': 'artist.getTopAlbums',
        'artist': artist
    })
    # in case of an error, return None
    if response.status_code != 200:
        return None
    try:
        album_images = {
            album['name']: album['image'][size]["#text"] for album in response.json()['topalbums']['album'][:amount]
            if album['image'][size]["#text"]}
    except KeyError:
        return None
    return album_images


def get_users_top_albums(username, size=3):
    """

    :param username: lastfm username
    :param size: 0 - small (34x34), 1 - medium (64x64), 2 - large (174x174), 3 - XL (300x300)
    :return: a dictionary  {"info": username, "albums": 9 x [album_title : image_url]}
    """
    response = lastfm_get({
        'method': 'user.getTopAlbums',
        'username': username
    })
    # in case of an error, return None
    if response.status_code != 200:
        return None

    # initialize a dict to avoid KeyErrors
    album_info = {"info": f"{username}'s favorite albums", "albums": dict()}
    try:
        for album in response.json()['topalbums']['album'][:9]:
            if album['image'][size]['#text']:
                # checks for incorrect/broken images
                album_info["albums"][album['name']] = album['image'][size]['#text']
    except KeyError:
        return None
    if not album_info["albums"]:
        print('user has nothing to show')
        # if the user has no albums to show
        return None
    return album_info
