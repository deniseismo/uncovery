import json
import os
import random
import time

import requests
import requests_cache

import uncover.helpers.main as joint
from uncover.helpers.utils import timeit, get_filtered_names_list, get_filtered_name

requests_cache.install_cache()


def lastfm_get_response(payload: dict):
    # define headers and URL
    headers = {'user-agent': os.environ.get('USER_AGENT')}
    url = 'http://ws.audioscrobbler.com/2.0/'
    # Add API key and format to the payload
    payload['api_key'] = os.environ.get('API_KEY')
    payload['format'] = 'json'
    response = requests.get(url, headers=headers, params=payload)
    return response


def lastfm_get_album_listeners(album: str, artist: str):
    """

    :param album: album's title
    :param artist: artist's name
    :return:
    """
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
        album_listeners = response.json()['album']['listeners']
    except KeyError:
        print(f"there are no listeners for {album}")
        return None
    return int(album_listeners)


def lastfm_get_artist_mbid(artist: str):
    response = lastfm_get_response({
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


def lastfm_get_artist_correct_name(artist: str):
    """
    Use the last.fm corrections data to check whether the supplied artist has a correction to a canonical artist
    :param artist: artist's name as is
    :return: corrected version of the artist's name
    """
    response = lastfm_get_response({
        'method': 'artist.getCorrection',
        'artist': artist
    })
    # in case of an error, return None
    if response.status_code != 200:
        return None
    try:
        correct_name = response.json()["corrections"]["correction"]["artist"]["name"]
    except (KeyError, TypeError, json.decoder.JSONDecodeError):
        return None
    return correct_name


def lookup_tags(artist: str):
    """
    :param artist: musician/band
    :return: top 3 tags from the given artist in the form of a string
    """
    response = lastfm_get_response({
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


def lastfm_get_artist_top_albums(artist: str, size=3, amount=9):
    """
    :param amount: a number of albums, default = 9
    :param size: 3 - large size (300x300)
    :param artist: artist's name (musician, band, etc)
    :return: a dict {album_name: album_image_url}
    """
    # try correcting some typos in artist's name
    correct_name = lastfm_get_artist_correct_name(artist)
    if correct_name:
        artist = correct_name

    response = lastfm_get_response({
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


@timeit
def lastfm_get_users_top_albums(username: str, size=3, time_period="overall", amount=25):
    """
    :param amount: amount ot albums
    :param time_period: (Optional) : overall | 7day | 1month | 3month | 6month | 12month | shuffle
                                    - The time period over which to retrieve top artists for.
    :param username: lastfm username
    :param size: 0 - small (34x34), 1 - medium (64x64), 2 - large (174x174), 3 - XL (300x300)
    :return: a dictionary  {"info": username, "albums": 9 x [album_title : image_url]}
    """
    shuffle = False
    possible_time_periods = ["overall", "7day", "1month", "3month", "6month", "12month"]
    if time_period == "shuffle":
        shuffle = True
        time_period = random.choice(possible_time_periods)
    time_period_table = {
        "overall": "of all time",
        "7day": "for the past 7 days",
        "1month": "for the past month",
        "3month": "for the past 3 months",
        "6month": "for the past 6 months",
        "12month": "for the past 12 months"
    }
    response = lastfm_get_response({
        'method': 'user.getTopAlbums',
        'username': username,
        'period': time_period
    })
    # in case of an error, return None
    if response.status_code != 200:
        return None
    # in case the user doesn't have any albums for a specific time period but perhaps does have for 'overall'
    if shuffle and time_period != "overall" and not response.json()['topalbums']['album']:
        time_period = "overall"
        response = lastfm_get_response({
            'method': 'user.getTopAlbums',
            'username': username,
            'period': time_period
        })
    # initialize a dict to avoid KeyErrors
    album_info = {
        "info": f"{username}'s top albums {time_period_table[time_period]}",
        "albums": list()
    }
    if shuffle:
        album_info["info"] = f"{username} random albums {time_period_table[time_period]}"
    try:
        a_set_of_titles = set()
        for album in response.json()['topalbums']['album'][:amount]:
            # gets the correct artist's anme
            artist_correct_name = lastfm_get_artist_correct_name(album['artist']['name'])
            # gets the album image
            album_image = joint.ultimate_album_image_finder(album_title=album['name'],
                                                            artist=artist_correct_name)
            # checks for incorrect/broken images
            if album_image:
                filtered_name = get_filtered_name(album['name'])
                an_album_dict = {
                    "title": album['name'],
                    "names": [album['name'].lower()] + get_filtered_names_list(album['name']),
                    "image": album_image
                    # "image": album['image'][size]['#text'],
                }
                an_album_dict['names'] = list(set(an_album_dict['names']))
                # appends an album dict with all the info to the list
                if filtered_name not in a_set_of_titles:
                    a_set_of_titles.add(filtered_name)
                    album_info["albums"].append(an_album_dict)
    except (KeyError, IndexError):
        return None
    if not album_info["albums"]:
        print('user has nothing to show')
        # if the user has no albums to show
        return None
    if shuffle:
        random.shuffle(album_info["albums"])
    # get ids right
    album_id = 0
    for album in album_info['albums']:
        album['id'] = album_id
        album_id += 1
    return album_info
