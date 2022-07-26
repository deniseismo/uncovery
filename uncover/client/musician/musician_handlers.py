import asyncio
from typing import Optional

from fuzzywuzzy import fuzz
from sqlalchemy import func
from sqlalchemy.sql import expression

from uncover import cache
from uncover.album_processing.album_processing_helpers import enumerate_artist_albums
from uncover.album_processing.process_albums_from_database import process_albums_from_db
from uncover.cover_art_finder.cover_art_handlers import fetch_and_assign_images
from uncover.models import Album, Artist
from uncover.music_apis.musicbrainz_api.mb_artist_handlers import mb_fetch_artists_albums
from uncover.music_apis.spotify_api.spotify_album_handlers import spotify_get_artists_albums_images
from uncover.schemas.album_schema import AlbumInfo
from uncover.utilities.logging_handlers import log_artist_missing_from_db


def _get_sorting_function(sorting: str) -> expression:
    """
    get sqlalchemy sorting function based on the sorting type picked by user
    :param sorting: (str) order by [popular, shuffle, latest, earliest]
    :return:
    """
    ORDER_TABLE = {
        "popular": Album.rating.desc(),
        "shuffle": func.random(),
        "latest": Album.release_date.desc(),
        "earliest": Album.release_date.asc()
    }
    return ORDER_TABLE[sorting]


@cache.memoize(timeout=3600)
def sql_select_artist_albums(artist_name: str, sorting: str) -> Optional[list[AlbumInfo]]:
    """
    search the artist through the database
    :param sorting: sorted by: popularity, release date, randomly
    :param artist_name: artist's name
    :return: album info dict with all the info about albums
    """
    ALBUM_LIMIT = 9
    order_by = _get_sorting_function(sorting)
    # query artist
    artist = Artist.query.filter_by(name=artist_name).first()
    if not artist:
        # no such artist found
        return None

    # album entries, each of 'Album' SQL class
    try:
        album_entries = Album.query.filter_by(artist=artist).order_by(order_by).limit(ALBUM_LIMIT).all()
    except (TypeError, KeyError, IndexError):
        return None
    processed_albums = process_albums_from_db(album_entries)
    return processed_albums


@cache.memoize(timeout=360)
def sql_find_specific_album(artist_name: str, an_album_to_find: str):
    """
    finds a specific album image via database
    :param artist_name: artist's name
    :param an_album_to_find: album's title
    :return:
    """
    artist = Artist.query.filter_by(name=artist_name).first()
    print(f'artist found in sql: {artist}')
    if not artist:
        # no such artist found
        print('no artist found')
        # logs an artist to the missing artists list log
        log_artist_missing_from_db(artist_name=artist_name)
        return None
    print('artist found')
    album_entries = Album.query.filter_by(artist=artist).all()
    album_found = None
    ratio_threshold = 94
    an_album_to_find = an_album_to_find.lower()
    for album in album_entries:
        album_title = album.title.lower()
        # implements a fuzzy match algorithm function
        current_ratio = fuzz.ratio(album_title, an_album_to_find)
        partial_ratio = fuzz.partial_ratio(album_title, an_album_to_find)
        if partial_ratio == 100:
            album_found = album.cover_art
        if current_ratio > 98:
            # found perfect match, return immediately
            return album.cover_art
        elif current_ratio > ratio_threshold:
            ratio_threshold = current_ratio
            album_found = album.cover_art
    if not album_found:
        return None
    return album_found


def fetch_artists_top_albums_images(artist_name: str, sorting: str) -> Optional[list[AlbumInfo]]:
    """
    get artist's top album images (default way), no database
    :param sorting: earliest/latest/popular/shuffle
    :param artist_name: artist's name
    :return: a dict of all the album images found
    """
    if not artist_name or not sorting:
        return None
    if sorting not in ["popular", "latest", "earliest", "shuffle"]:
        return None

    albums = asyncio.run(mb_fetch_artists_albums(artist_name, sorting))

    if not albums:
        try:
            print('trying spotifyjke')
            albums = spotify_get_artists_albums_images(artist_name, sorting)
            print(f'albums with spotify: {albums}')
            if albums:
                log_artist_missing_from_db(artist_name=artist_name)
                return albums
            else:
                return None
        except TypeError:
            return None
    # initialize a dict to avoid KeyErrors
    asyncio.run(fetch_and_assign_images(albums_list=albums, artist=artist_name))
    albums_with_album_covers = _filter_albums_without_album_covers(albums)
    if not albums_with_album_covers:
        return None

    enumerate_artist_albums(albums_with_album_covers)

    print(f'there are {len(albums_with_album_covers)} album images found with the Ultimate')
    print(f'search through APIs was successful')
    log_artist_missing_from_db(artist_name=artist_name)
    return albums_with_album_covers


def _filter_albums_without_album_covers(albums: list[AlbumInfo]) -> list[Optional[AlbumInfo]]:
    """
    keep only albums that have album covers
    :param albums: a list of album dicts
    :return: a list of album dicts with album covers, discard albums without album covers
    """
    albums_with_albums_covers = [album for album in albums if album.image]
    return albums_with_albums_covers
