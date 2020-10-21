import random
import time
from datetime import datetime

import musicbrainzngs
import requests
from flask import current_app

import uncover.helpers.lastfm_api as lastfm
import uncover.helpers.utilities as utils

# from uncover import cache

# requests_cache.install_cache()

musicbrainzngs.set_useragent("uncovery", "0.8", "denisseismo@gmail.com")


@utils.timeit
# @cache.memoize(timeout=60000)
def mb_get_album_alternative_name(album_id: str):
    """
    gets the alternative name for the album (e. g. White Album for 'The Beatles')
    :param album_id: album_id from MusicBrainz
    :return: alternative name for an album
    """
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
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


@utils.timeit
# @cache.memoize(timeout=60000)
def mb_get_album_release_date(album_id: str):
    """
    :param album_id: album_id from MusicBrainz
    :return: album release date
    """
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
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


@utils.timeit
# @cache.memoize(timeout=60000)
def mb_get_artist_mbid(artist_name: str):
    artist_fixed = artist_name.lower().replace("’", "'").replace('‐', '-').replace(',', '')
    artists_found = musicbrainzngs.search_artists(artist_name, limit=4)
    mbid = None
    if not artists_found['artist-count']:
        # nothing found
        return None
    for artist in artists_found['artist-list']:
        if artist['name'].lower().replace("’", "'").replace('‐', '-').replace(',', '') == artist_fixed:
            mbid = artist['id']
            return mbid
    print(f'found artists mbid: {mbid}')
    return None


def mb_get_artist_mbid_backup(artist_name: str):
    """
    search for an artist's mbid on MusicBrainz
    :param artist_name: artist's name (e.g. MGMT, The Prodigy, etc.)
    :return: mbid (MusicBrainz ID)
    """
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    url = "http://musicbrainz.org/ws/2/artist/"
    params = {"query": "artist:" + artist_name, "limit": "10", "fmt": "json"}
    response = requests.get(url=url, params=params, headers=headers)
    if response.status_code != 200:
        return None
    try:
        # get the first one (should probably be ok)
        # mbid = response.json()["artists"][0]["id"]
        mbid = musicbrainzngs.search_artists(artist_name, limit=2)["artist-list"][0]['id']
        print(f'mbid found with ngs: {mbid}')
        for artist_obj in response.json()['artists']:
            # go deep in case of some discrepancies or bugs
            artist_fixed = artist_name.lower().replace("’", "'").replace('‐', '-').replace(',', '')
            object_fixed = artist_obj['name'].lower().replace("’", "'").replace('‐', '-').replace(',', '')
            if artist_fixed == object_fixed:
                try:
                    mbid = artist_obj['id']
                    break
                except (IndexError, KeyError):
                    continue
    except (KeyError, IndexError):
        mbid = mb_get_artist_mbid_v2(artist_name)
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


# @cache.memoize(timeout=60000)
def mb_get_album_mbid(album: str, artist: str):
    """
    search for an album's mbid on MusicBrainz
    :param album: album's name
    :param artist: artist's name (e.g. MGMT, The Prodigy, etc.)
    :return: mbid (MusicBrainz ID)
    """
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
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


@utils.timeit
def mb_get_artists_albums(artist: str, sorting="popular", limit=9):
    """
    :param limit: a number of albums retrieved
    :param sorting: sorting by: popularity, release date, random
    :param artist: artist's name
    :return:
    """
    ORDER = {
        "popular": ("rating", True),
        "latest": ("release_date", True),
        "earliest": ("release_date", False)
    }
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    artist_mbid = mb_get_artist_mbid(artist)
    print(artist_mbid)

    if not artist_mbid:
        # if nothing found
        return None
    album_query_filter = '%20AND%20primarytype:album%20AND%20secondarytype:(-*)%20AND%20status:official&limit=100&fmt=json'
    response = requests.get(
        'https://musicbrainz.org/ws/2/release-group?query=arid:'
        + artist_mbid
        + album_query_filter,
        headers=headers
    )
    # in case of an error, return None
    if response.status_code != 200:
        return None

    albums = []
    # initialize a set of titles used to filter duplicate titles
    a_set_of_titles = set()
    for release in response.json()["release-groups"]:
        alternative_name = mb_get_album_alternative_name(release['id'])
        full_title = release['title'].replace("’", "'")
        print(full_title)
        correct_title = full_title.lower()
        rating = lastfm.lastfm_get_album_listeners(correct_title, artist)
        filtered_name = utils.get_filtered_name(full_title)
        an_album_dict = {
            "title": full_title,
            "names": [correct_title] + utils.get_filtered_names_list(full_title),
            "mbid": release['id'],
            "rating": rating if rating else 0
        }
        if sorting in ["earliest", "latest"]:
            release_date = mb_get_album_release_date(release['id'])
            release_date = datetime.strptime(release_date[:4], '%Y')
            an_album_dict["release_date"] = release_date
        # add an alternative album name if exists
        if alternative_name:
            alternative_name = alternative_name.replace("“", "").replace("”", "")
            an_album_dict['altenative_name'] = alternative_name
            an_album_dict["names"] += alternative_name
            an_album_dict["names"] += utils.get_filtered_names_list(alternative_name)

        # filters duplicate album names
        an_album_dict['names'] = list(set(an_album_dict['names']))
        # add an album to the albums list only if it's a new one
        if filtered_name not in a_set_of_titles:
            a_set_of_titles.add(filtered_name)
            albums.append(an_album_dict)
    if sorting == "shuffle":
        random.seed(datetime.now())
        random.shuffle(albums)
        return albums[:limit]
    else:
        sorted_albums = sorted(albums, key=lambda item: item[ORDER[sorting][0]], reverse=ORDER[sorting][1])
    return sorted_albums[:limit]


# @cache.memoize(timeout=3600)
def mb_get_album_image(mbid: str, size='large', fast=False):
    """
    :param fast: a faster way to get the cover image
    :param mbid: mbid for an album release on MusicBrainz
    :param size: small, etc.
    :return: an album cover location
    """
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    # /release-group/{mbid}/front[-(250|500|1200)]
    if not mbid:
        return None
    image = None
    if fast:
        # a faster way (lower resolution)
        url = "http://coverartarchive.org/release-group/" + mbid
        response = requests.get(url)
        if response.status_code != 200:
            return None
        try:
            images = response.json()
            if images:
                image = images['images'][0]['thumbnails'][size]
        except (KeyError, IndexError):
            return None
    else:
        # get what's supposed to be a 'front' cover (slower but most likely gets higher quality)
        url = "http://coverartarchive.org/release-group/" + mbid + '/front'
        # response = requests.get(url)
        response = requests.head(url, headers=headers)
        if response.status_code != 307:
            return None
        try:
            image = response.headers['location']
        except (KeyError, IndexError):
            return None
    return image


if __name__ == '__main__':
    albums = mb_get_artists_albums("Exhumed")
    print(albums)
