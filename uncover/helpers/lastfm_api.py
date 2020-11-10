import json
import random

import requests
import requests_cache
from flask import current_app

import uncover.helpers.main as main
import uncover.helpers.main_async as main_async
import uncover.helpers.utilities as utils
from uncover import cache

requests_cache.install_cache()


def lastfm_get_response(payload: dict):
    # define headers and URL
    headers = {'user-agent': current_app.config['USER_AGENT']}
    url = 'http://ws.audioscrobbler.com/2.0/'
    # Add API key and format to the payload
    payload['api_key'] = current_app.config['API_KEY']
    payload['format'] = 'json'
    response = requests.get(url, headers=headers, params=payload)
    return response


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
        album_listeners = response.json()['album']['listeners']
    except KeyError:
        print(f"there are no listeners for {album}")
        return None
    return int(album_listeners)


def lastfm_get_artist_mbid(artist: str):
    """
    gets the MusicBrainz id through last.fm API (a backup function)
    :param artist: artist's name
    :return: MusicBrainz ID
    """
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


@cache.memoize(timeout=60000)
def lastfm_get_artist_correct_name(artist: str):
    """
    Use the last.fm corrections data to check whether the supplied artist has a correction to a canonical artist
    :param artist: artist's name as is
    :return: corrected version of the artist's name
    """
    print('getting artist correction')
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


@cache.memoize(timeout=6000)
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
    else:
        amount = 9
    # time_period_table = {
    #     "overall": "of all time",
    #     "7day": "for the past 7 days",
    #     "1month": "for the past month",
    #     "3month": "for the past 3 months",
    #     "6month": "for the past 6 months",
    #     "12month": "for the past 12 months"
    # }
    response = lastfm_get_response({
        'method': 'user.getTopAlbums',
        'username': username,
        'period': time_period,
        'limit': amount
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
            'period': time_period,
            'limit': amount
        })
    # initialize a dict to avoid KeyErrors
    try:
        username_correct = response.json()['topalbums']['@attr']['user']
    except (KeyError, IndexError, TypeError):
        return None
    album_info = {
        "info": {
            "type": "user",
            "query": username_correct
        },
        "albums": list()
    }
    # if shuffle:
    #     album_info["info"] = f"{username} random albums {time_period_table[time_period]}"
    albums_found = response.json()['topalbums']['album']
    print(f'albums found: {albums_found}')
    try:
        a_set_of_titles = set()
        for album in albums_found:
            # gets the correct artist's name
            resizable = True
            artist_name = album['artist']['name']
            artist_correct_name = lastfm_get_artist_correct_name(album['artist']['name'])
            if artist_correct_name:
                artist_name = artist_correct_name

            album_name = album['name']
            album_correct_name = utils.get_filtered_name(album_name)

            # try getting the album image through database
            album_image = main_async.sql_find_specific_album(artist_name, album_name)
            if not album_image:
                print(f'second sql attempt for {album_name}')
                # second attempt in case the album name was badly written
                album_image = main_async.sql_find_specific_album(artist_name, album_correct_name)
            # try getting through the ultimate image finder function if database doesn't have the image
            if not album_image:
                resizable = False
                album_image = main.ultimate_album_image_finder(album_title=album_name,
                                                               artist=artist_name,
                                                               fast=True,
                                                               ultrafast=True)
            if not album_image:
                try:
                    album_image = album['image'][3]['#text']
                except (TypeError, IndexError, KeyError):
                    album_image = None
            # checks for incorrect/broken images
            if album_image:
                filtered_name = utils.get_filtered_name(album['name'])
                an_album_dict = {
                    "title": album_name,
                    "names": [album_name.lower()] + utils.get_filtered_names_list(album_name),
                    "artist_name": artist_name,
                    "artist_names": [artist_name] + utils.get_filtered_artist_names(artist_name)
                }
                if resizable:
                    an_album_dict['image_small'] = 'static/optimized_cover_art_images/' + album_image + "-size200.jpg"
                    an_album_dict['image_medium'] = 'static/optimized_cover_art_images/' + album_image + "-size300.jpg"
                    an_album_dict['image'] = 'static/optimized_cover_art_images/' + album_image + ".jpg"
                else:
                    an_album_dict['image'] = album_image
                an_album_dict['artist_names'] = list(set(an_album_dict["artist_names"]))
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
    for count, album in enumerate(album_info['albums']):
        album['id'] = count
    return album_info


@cache.memoize(timeout=6000)
def lastfm_get_user_avatar(username: str):
    """
    gets user's avatar image URL
    :param username: user's name
    :return:
    """
    print('getting avatar')
    response = lastfm_get_response({
        'method': 'user.getInfo',
        'user': username
    })
    # in case of an error, return None
    if response.status_code != 200:
        print(f"couldn't find {username} on last.fm")
        return None
    try:
        user_avatars = response.json()['user']['image']
    except KeyError:
        print(f"there is no avatar for {username}")
        return None
    try:
        avatar = user_avatars[-1]["#text"]
    except (KeyError, IndexError):
        return None
    return avatar

