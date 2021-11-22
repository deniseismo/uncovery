import random

from uncover import cache
from uncover.cover_art_finder.cover_art_handlers import ultimate_album_image_finder
from uncover.music_apis.lastfm_api.lastfm_artist_handlers import lastfm_get_artist_correct_name
from uncover.music_apis.lastfm_api.lastfm_client_api import lastfm_get_response
from uncover.musician.musician_handlers import sql_find_specific_album
from uncover.utilities.name_filtering import get_filtered_name, get_filtered_names_list


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
    albums_found = response.json()['topalbums']['album']
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
            album_correct_name = get_filtered_name(album_name)

            # try getting the album image through database
            album_image = sql_find_specific_album(artist_name, album_name)
            if not album_image:
                # second attempt in case the album name was badly written
                album_image = sql_find_specific_album(artist_name, album_correct_name)
            # try getting through the ultimate image finder function if database doesn't have the image
            if not album_image:
                resizable = False
                album_image = ultimate_album_image_finder(album_title=album_name,
                                                          artist=artist_name,
                                                          fast=True,
                                                          ultrafast=True)
            if not album_image:
                try:
                    album_image = album['image'][size]['#text']
                except (TypeError, IndexError, KeyError):
                    album_image = None
            # checks for incorrect/broken images
            if album_image:
                filtered_name = get_filtered_name(album['name'])
                an_album_dict = {
                    "title": album_name,
                    "names": [album_name.lower()] + get_filtered_names_list(album_name),
                    "artist_name": artist_name,
                    "artist_names": [artist_name] + get_filtered_names_list(artist_name)
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
    print(f'getting avatar for {username}')
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
    except (KeyError, IndexError, TypeError, ValueError):
        print(f"there is no avatar for {username}")
        return None
    try:
        user_avatar_url = user_avatars[-1]["#text"]
    except (KeyError, IndexError, TypeError):
        return None
    return user_avatar_url
