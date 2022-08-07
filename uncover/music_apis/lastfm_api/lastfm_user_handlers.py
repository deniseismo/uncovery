import json
import random
from typing import Optional

from uncover import cache
from uncover.album_processing.album_processing_helpers import enumerate_artist_albums, sort_artist_albums
from uncover.album_processing.process_albums_from_lastfm import process_lastfm_user_top_albums
from uncover.music_apis.lastfm_api.lastfm_client_api import lastfm_get_response
from uncover.music_apis.lastfm_api.lastfm_helpers import lastfm_show_response_error
from uncover.schemas.album_schema import AlbumInfo


def lastfm_get_users_top_albums(
        username: str,
        time_period: str = "overall",
        amount: int = 25
) -> Optional[tuple[list[AlbumInfo], str]]:
    """
    :param amount: amount ot albums
    :param time_period: (Optional) : overall | 7day | 1month | 3month | 6month | 12month | shuffle
                                    - The time period over which to retrieve top artists for.
    :param username: lastfm username
    :return: a dictionary  {"info": username, "albums": 9 x [album_title : image_url]}
    """
    image_size = 3
    shuffle = False
    possible_time_periods = ["overall", "7day", "1month", "3month", "6month", "12month"]
    if time_period == "shuffle":
        shuffle = True
        time_period = random.choice(possible_time_periods)
        print(f"shuffle: {time_period}")
    else:
        amount = 9
    response = lastfm_get_response({
        'method': 'user.getTopAlbums',
        'username': username,
        'period': time_period,
        'limit': amount
    })
    if not response:
        return None
    # in case of an error, return None
    if response.status_code != 200:
        lastfm_show_response_error(response)
        return None
    try:
        lastfm_user_albums_info = response.json()
    except (KeyError, TypeError, json.decoder.JSONDecodeError) as e:
        print(e)
        return None
    try:
        lastfm_user_albums = lastfm_user_albums_info['topalbums']['album']
    except (KeyError, TypeError) as e:
        print(e)
        return None

    # in case the user doesn't have any albums for time period picked by random (shuffle), → try to show albums overall
    if shuffle and time_period != "overall" and not lastfm_user_albums:
        print(f"shuffle: {time_period} had nothing to show, trying to get albums overall instead")
        time_period = "overall"
        response = lastfm_get_response({
            'method': 'user.getTopAlbums',
            'username': username,
            'period': time_period,
            'limit': amount
        })
        if not response:
            return None
        try:
            lastfm_user_albums_info = response.json()
        except (KeyError, TypeError, json.decoder.JSONDecodeError) as e:
            print(e)
            return None
        try:
            lastfm_user_albums = lastfm_user_albums_info['topalbums']['album']
        except (KeyError, TypeError) as e:
            print(e)
            return None

    if not lastfm_user_albums:
        print(f"no albums found for User({username}), {time_period}")
        return None

    try:
        username_correct = lastfm_user_albums_info['topalbums']['@attr']['user']
        username = username_correct if username_correct else username
    except (KeyError, TypeError) as e:
        print(e)

    processed_albums = process_lastfm_user_top_albums(lastfm_user_albums, image_size=image_size)

    if not processed_albums:
        return None
    if shuffle:
        sort_artist_albums(processed_albums, sorting="shuffle")

    # get ids right
    enumerate_artist_albums(processed_albums)
    return processed_albums, username


@cache.memoize(timeout=6000)
def lastfm_get_user_avatar(username: str):
    """
    gets user's avatar image URL
    :param username: user's name
    :return:
    """
    response = lastfm_get_response({
        'method': 'user.getInfo',
        'user': username
    })
    if not response:
        return None
    # in case of an error, return None
    if response.status_code != 200:
        lastfm_show_response_error(response)
        return None
    try:
        user_avatars = response.json()['user']['image']
    except (KeyError, TypeError, json.decoder.JSONDecodeError):
        print(f"there is no avatar for {username}")
        return None
    try:
        user_avatar_url = user_avatars[-1]["#text"]
    except (KeyError, IndexError, TypeError):
        return None
    return user_avatar_url
