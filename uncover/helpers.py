import os
import time
import requests
import requests_cache
import json


requests_cache.install_cache()


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


def lastfm_get(payload):
    # define headers and URL
    headers = {'user-agent':  os.environ.get('USER_AGENT')}
    url = 'http://ws.audioscrobbler.com/2.0/'
    # Add API key and format to the payload
    payload['api_key'] = os.environ.get('API_KEY')
    payload['format'] = 'json'
    response = requests.get(url, headers=headers, params=payload)
    return response


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


def get_top_albums(artist):
    response = lastfm_get({
        'method': 'artist.getTopAlbums',
        'artist': artist
    })
    # in case of an error, return None
    if response.status_code != 200:
        return None
    albums = [album['name'] for album in response.json()['topalbums']['album'][:3]]

    album_images = {album['name']: album['image'][3]["#text"] for album in response.json()['topalbums']['album'][:9]}

    return album_images


def get_users_top_albums(username):
    response = lastfm_get({
        'method': 'user.getTopAlbums',
        'username': username
    })
    # in case of an error, return None
    if response.status_code != 200:
        return None
    albums = [album['name'] for album in response.json()['topalbums']['album'][:3]]

    album_images = {album['name']: album['image'][3]["#text"] for album in response.json()['topalbums']['album'][:9]}

    return album_images


# print(lookup_tags("David Bowie"))
# print(get_top_albums('Arcade Fire'))
# print(get_users_top_albums('tomsk-seismo'))

