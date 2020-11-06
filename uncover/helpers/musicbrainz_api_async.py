import random
import time
from datetime import datetime

import aiohttp
import asyncio
import musicbrainzngs
import requests
from flask import current_app

import uncover.helpers.lastfm_api_async as lastfm
import uncover.helpers.utilities as utils

musicbrainzngs.set_useragent("uncovery", "0.8", "denisseismo@gmail.com")


@utils.timeit
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


async def mb_fetch_album_release_date(album_id: str, session):
    """
    ASYNC
    :param session: ClientSession()
    :param album_id: album_id from MusicBrainz
    :return: album release date
    """
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    url = "http://musicbrainz.org/ws/2/release-group/" + album_id
    params = {"fmt": "json"}
    async with session.get(url=url, params=params, headers=headers) as response:
        if response.status_code != 200:
            return None
        try:
            release_date = await response.json()['first-release-date']
        except (KeyError, IndexError, TypeError):
            return None
        if not getattr(response, 'from_cache', False):
            time.sleep(1)
        return release_date


@utils.timeit
async def mb_fetch_album_alternative_name(album_id: str, session):
    """
    gets the alternative name for the album (e. g. White Album for 'The Beatles')
    :param album_id: album_id from MusicBrainz
    :return: alternative name for an album
    """
    headers = {'User-Agent': current_app.config['MUSIC_BRAINZ_USER_AGENT']}
    url = "http://musicbrainz.org/ws/2/release-group/" + album_id
    params = {"inc": "ratings", "fmt": "json"}
    async with session.get(url=url, params=params, headers=headers) as response:
        if response.status != 200:
            return None
        try:
            alternative = await response.json()
        except (KeyError, IndexError):
            return None
        return alternative['disambiguation']


@utils.timeit
async def mb_fetch_artists_albums(artist: str, sorting="popular", limit=9):
    """
    :param limit: a number of albums retrieved
    :param sorting: sorting by: popularity, release date, random
    :param artist: artist's name
    :return:
    """
    print('async!')
    print('async!')
    print('async!')
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

    albums_found = response.json()["release-groups"]
    albums = []
    # initialize a set of titles used to filter duplicate titles
    a_set_of_titles = set()
    tasks = []
    async with aiohttp.ClientSession() as session:
        for release in albums_found:
            task = asyncio.create_task(add_album(album=release,
                                                 set_of_titles=a_set_of_titles,
                                                 session=session,
                                                 albums_list=albums,
                                                 artist=artist,
                                                 sorting=sorting))
            tasks.append(task)
        await asyncio.gather(*tasks)
    if sorting == "shuffle":
        random.seed(datetime.now())
        random.shuffle(albums)
        return albums[:limit]
    else:
        sorted_albums = sorted(albums, key=lambda item: item[ORDER[sorting][0]], reverse=ORDER[sorting][1])
    print(f'inside: {albums}')
    return sorted_albums[:limit]


async def add_album(album, set_of_titles, session, albums_list, artist, sorting):
    alternative_name = await mb_fetch_album_alternative_name(album['id'], session)
    print(alternative_name)
    full_title = album['title'].replace("’", "'")
    print(full_title)
    correct_title = full_title.lower()
    rating = await lastfm.lastfm_fetch_album_listeners(correct_title, artist, session)
    print(rating)
    filtered_name = utils.get_filtered_name(full_title)
    an_album_dict = {
        "artist_name": artist,
        "title": full_title,
        "names": [correct_title] + utils.get_filtered_names_list(full_title),
        "mbid": album['id'],
        "rating": rating if rating else 0
    }
    if sorting in ["earliest", "latest"]:
        release_date = mb_fetch_album_release_date(album['id'])
        release_date = datetime.strptime(release_date[:4], '%Y')
        an_album_dict["release_date"] = release_date
    if alternative_name:
        alternative_name = alternative_name.replace("“", "").replace("”", "")
        an_album_dict['altenative_name'] = alternative_name
        an_album_dict["names"] += alternative_name
        an_album_dict["names"] += utils.get_filtered_names_list(alternative_name)

    # filters duplicate album names
    an_album_dict['names'] = list(set(an_album_dict['names']))
    # add an album to the albums list only if it's a new one
    if filtered_name not in set_of_titles:
        set_of_titles.add(filtered_name)
        albums_list.append(an_album_dict)

# async def main():
#     albums_list = await mb_fetch_artists_albums(artist="Exhumed")
#     return albums_list

# if __name__ == '__main__':
#     t0 = time.time()
#
#     albumsjke = asyncio.run(mb_fetch_artists_albums(artist="Exhumed"))
#     print(time.time() - t0)
#     print(albumsjke)
