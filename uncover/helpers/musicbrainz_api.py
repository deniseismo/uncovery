from collections import defaultdict

import musicbrainzngs
import requests
import requests_cache

import uncover.helpers.lastfm_api as lastfm_api
from uncover.helpers.utils import timeit, get_filtered_names_list, get_filtered_name

requests_cache.install_cache()

# Tell musicbrainz what your app is, and how to contact you
# (this step is required, as per the webservice access rules
# at http://wiki.musicbrainz.org/XML_Web_Service/Rate_Limiting )
musicbrainzngs.set_useragent("albumguesser", "0.1", "denisseismo@gmail.com")


def mb_get_album_alternative_name(album_id: str):
    """
    :param album_id: album_id from MusicBrainz
    :return: alternative name for an album
    """
    url = "http://musicbrainz.org/ws/2/release-group/" + album_id
    params = {"inc": "ratings", "fmt": "json"}
    response = requests.get(url=url, params=params)
    if response.status_code != 200:
        return None
    try:
        alternative = response.json()['disambiguation']
    except (KeyError, IndexError):
        return None
    return alternative


def mb_get_album_rating(album_id: str):
    """
    :param album_id: album_id from MusicBrainz
    :return: rating (float)
    """
    url = "http://musicbrainz.org/ws/2/release-group/" + album_id
    params = {"inc": "ratings", "fmt": "json"}
    response = requests.get(url=url, params=params)
    if response.status_code != 200:
        return None
    try:
        rating = response.json()['rating']['value']
    except (KeyError, IndexError):
        return None
    return rating


def mb_get_artist_mbid(artist: str):
    """
    search for an artist's mbid on MusicBrainz
    :param artist: artist's name (e.g. MGMT, The Prodigy, etc.)
    :return: mbid (MusicBrainz ID)
    """
    url = "http://musicbrainz.org/ws/2/artist/"
    params = {"query": "artist:" + artist, "limit": "1", "fmt": "json"}
    response = requests.get(url=url, params=params)
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


def get_artists_albums_v2(artist: str):
    """
    reserve function in case of some failures
    gets artist's albums by getting mbid directly through MusicBrainz
    (in case there was some error with mbid taken via lastfm)
    :param artist:
    :return:
    """
    artist_mbid = mb_get_artist_mbid(artist)
    if not artist_mbid:
        return None
    response = requests.get(
        'https://musicbrainz.org/ws/2/release-group?query=arid:'
        + artist_mbid
        + '%20AND%20primarytype:album%20AND%20secondarytype:(-*)%20AND%20status:official&fmt=json')
    if response.status_code != 200:
        return None
    albums = defaultdict(dict)
    for release in response.json()["release-groups"][:]:
        # ADDITIONAL CHECK-UP(?): if release['artist-credit'][0]['artist']['id'] == artist_mbid
        # add an id of an album to the dict
        albums[release['title'].lower()]['id'] = release['id']
        # get album rating
        rating = mb_get_album_rating(release['id'])
        # add rating if exists
        albums[release['title'].lower()]['rating'] = rating if rating else 0
    return albums


@timeit
def mb_get_artists_albums(artist: str, mbid=None, amount=9):
    """
    :param artist: artist's name
    :param mbid: MusicBrainz id (overrides artist's name if present)
    :param amount: a number of albums
    :return:
    """
    if mbid:
        # if mbid is already provided
        artist_mbid = mbid
    else:
        # find mbid directly through MB
        artist_mbid = mb_get_artist_mbid(artist)
    if not artist_mbid:
        # if nothing found
        return None
    album_query_filter = '%20AND%20primarytype:album%20AND%20secondarytype:(-*)%20AND%20status:official&fmt=json'
    response = requests.get(
        'https://musicbrainz.org/ws/2/release-group?query=arid:'
        + artist_mbid
        + album_query_filter)
    # in case of an error, return None
    if response.status_code != 200:
        return None

    albums = []
    # initialize a set of titles used to filter duplicate titles
    a_set_of_titles = set()
    for release in response.json()["release-groups"][:]:
        # ADDITIONAL CHECK-UP(?): if release['artist-credit'][0]['artist']['id'] == artist_mbid
        alternative_name = mb_get_album_alternative_name(release['id']).replace("“", "").replace("”", "")
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
            an_album_dict["names"] += alternative_name
            an_album_dict["names"] += get_filtered_names_list(alternative_name)

        # filters duplicate album names
        an_album_dict['names'] = list(set(an_album_dict['names']))
        # add an album to the albums list only if it's a new one
        if filtered_name not in a_set_of_titles:
            a_set_of_titles.add(filtered_name)
            albums.append(an_album_dict)
    if not albums:
        #  in case of some weird error with the mbid taken via lastfm make another attempt with v2
        albums = get_artists_albums_v2(artist)
    sorted_albums = sorted(albums, key=lambda item: item['rating'], reverse=True)
    return sorted_albums


def mb_get_album_image(mbid: str, size='large'):
    """
    :param mbid: mbid for an album release on MusicBrainz
    :param size: small, etc.
    :return: an album cover location
    """
    # /release-group/{mbid}/front[-(250|500|1200)]
    if not mbid:
        return None
    # url = "http://coverartarchive.org/release-group/" + mbid
    # get what's supposed to be a 'front' cover
    url = "http://coverartarchive.org/release-group/" + mbid + '/front'
    # response = requests.get(url)
    response = requests.head(url)
    if response.status_code != 307:
        return None
    try:
        image = response.headers['location']
        # image = response.json()['images'][0]['thumbnails'][size]
    except (KeyError, IndexError):
        return None
    return image
