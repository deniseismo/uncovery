import os
import time

import musicbrainzngs
import requests
import requests_cache

import uncover.helpers.lastfm_api as lastfm_api
from uncover.helpers.utils import timeit, get_filtered_names_list, get_filtered_name

requests_cache.install_cache()

musicbrainzngs.set_useragent("albumguesser", "0.1", "denisseismo@gmail.com")


def mb_get_album_alternative_name(album_id: str):
    """
    :param album_id: album_id from MusicBrainz
    :return: alternative name for an album
    """
    headers = {'User-Agent': os.environ.get('MUSIC_BRAINZ_USER_AGENT')}
    url = "http://musicbrainz.org/ws/2/release-group/" + album_id
    params = {"inc": "ratings", "fmt": "json"}
    response = requests.get(url=url, params=params, headers=headers)
    if response.status_code != 200:
        return None
    try:
        alternative = response.json()['disambiguation']
    except (KeyError, IndexError):
        return None
    return alternative


def mb_get_album_release_date(album_id: str):
    """
    :param album_id: album_id from MusicBrainz
    :return: album release date
    """
    headers = {'User-Agent': os.environ.get('MUSIC_BRAINZ_USER_AGENT')}
    url = "http://musicbrainz.org/ws/2/release-group/" + album_id
    params = {"fmt": "json"}
    response = requests.get(url=url, params=params, headers=headers)
    if response.status_code != 200:
        return None
    try:
        release_date = response.json()['first-release-date']
    except (KeyError, IndexError, TypeError):
        return None
    if not getattr(response, 'from_cache', False):
        time.sleep(1)
    return release_date


def mb_get_artist_mbid(artist: str):
    """
    search for an artist's mbid on MusicBrainz
    :param artist: artist's name (e.g. MGMT, The Prodigy, etc.)
    :return: mbid (MusicBrainz ID)
    """
    headers = {'User-Agent': os.environ.get('MUSIC_BRAINZ_USER_AGENT')}
    url = "http://musicbrainz.org/ws/2/artist/"
    params = {"query": "artist:" + artist, "limit": "1", "fmt": "json"}
    response = requests.get(url=url, params=params, headers=headers)
    if response.status_code != 200:
        return None
    try:
        mbid = response.json()["artists"][0]["id"]
    except (KeyError, IndexError):
        mbid = mb_get_artist_mbid_v2(artist)
    if not mbid:
        return None
    return mbid


def mb_get_artist_mbid_v2(artist: str):
    """
    a backup search for an artist's mbid
    :param artist: artist's name
    :return: mbid
    """
    url = "http://musicbrainz.org/ws/2/artist/"
    params = {"query": artist, "limit": "1", "fmt": "json"}
    response = requests.get(url=url, params=params)
    if response.status_code != 200:
        return None
    try:
        mbid = response.json()["artists"][0]["id"]
    except (KeyError, IndexError):
        return None
    return mbid


def mb_get_album_mbid(album: str, artist: str):
    """
    search for an album's mbid on MusicBrainz
    :param album: album's name
    :param artist: artist's name (e.g. MGMT, The Prodigy, etc.)
    :return: mbid (MusicBrainz ID)
    """
    headers = {'User-Agent': os.environ.get('MUSIC_BRAINZ_USER_AGENT')}
    url = "http://musicbrainz.org/ws/2/release-group/?query=release:"
    album_query_filter = f'%20AND%20artist:{artist}%20AND%20primarytype:album%20AND%20secondarytype:(-*)%20AND%20status:official&fmt=json'
    response = requests.get(url + album + album_query_filter, headers=headers)
    if response.status_code != 200:
        return None
    try:
        mbid = response.json()["release-groups"][0]["id"]
    except (KeyError, IndexError):
        return None
    return mbid


@timeit
def mb_get_artists_albums(artist: str):
    """
    :param artist: artist's name
    :return:
    """
    headers = {'User-Agent': os.environ.get('MUSIC_BRAINZ_USER_AGENT')}
    artist_mbid = mb_get_artist_mbid(artist)

    if not artist_mbid:
        # if nothing found
        return None
    album_query_filter = '%20AND%20primarytype:album%20AND%20secondarytype:(-*)%20AND%20status:official&fmt=json'
    response = requests.get(
        'https://musicbrainz.org/ws/2/release-group?query=arid:'
        + artist_mbid
        + album_query_filter,
        headers=headers)
    # in case of an error, return None
    if response.status_code != 200:
        return None

    albums = []
    # initialize a set of titles used to filter duplicate titles
    a_set_of_titles = set()
    for release in response.json()["release-groups"]:
        alternative_name = mb_get_album_alternative_name(release['id'])
        full_title = release['title'].replace("’", "'")
        correct_title = full_title.lower()
        rating = lastfm_api.lastfm_get_album_listeners(correct_title, artist)
        filtered_name = get_filtered_name(full_title)
        an_album_dict = {
            "title": full_title,
            "names": [correct_title] + get_filtered_names_list(full_title),
            "id": release['id'],
            "rating": rating if rating else 0
        }
        # add an alternative album name if exists
        if alternative_name:
            alternative_name = alternative_name.replace("“", "").replace("”", "")
            an_album_dict['altenative_name'] = alternative_name
            an_album_dict["names"] += alternative_name
            an_album_dict["names"] += get_filtered_names_list(alternative_name)

        # filters duplicate album names
        an_album_dict['names'] = list(set(an_album_dict['names']))
        # add an album to the albums list only if it's a new one
        if filtered_name not in a_set_of_titles:
            a_set_of_titles.add(filtered_name)
            albums.append(an_album_dict)

    sorted_albums = sorted(albums, key=lambda item: item['rating'], reverse=True)
    return sorted_albums


def mb_get_album_image(mbid: str, size='large'):
    """
    :param mbid: mbid for an album release on MusicBrainz
    :param size: small, etc.
    :return: an album cover location
    """
    headers = {'User-Agent': os.environ.get('MUSIC_BRAINZ_USER_AGENT')}
    # /release-group/{mbid}/front[-(250|500|1200)]
    if not mbid:
        return None
    # url = "http://coverartarchive.org/release-group/" + mbid
    # get what's supposed to be a 'front' cover
    url = "http://coverartarchive.org/release-group/" + mbid + '/front'
    # response = requests.get(url)
    response = requests.head(url, headers=headers)
    if response.status_code != 307:
        return None
    try:
        image = response.headers['location']
        # image = response.json()['images'][0]['thumbnails'][size]
    except (KeyError, IndexError):
        return None
    return image
