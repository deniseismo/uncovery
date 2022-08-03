import asyncio
from typing import Optional

from uncover import cache
from uncover.album_processing.album_processing_helpers import enumerate_artist_albums, \
    filter_out_albums_without_album_covers
from uncover.album_processing.process_albums_from_database import process_albums_from_db
from uncover.client.database_manipulation.db_album_handlers import db_get_albums_by_artist_entry
from uncover.client.database_manipulation.db_artist_handlers import db_get_artist
from uncover.cover_art_finder.cover_art_handlers import fetch_and_assign_images
from uncover.music_apis.musicbrainz_api.mb_artist_handlers import mb_fetch_artists_albums
from uncover.music_apis.spotify_api.spotify_album_handlers import spotify_get_artists_albums
from uncover.schemas.album_schema import AlbumInfo
from uncover.utilities.logging_handlers import log_artist_missing_from_db


@cache.memoize(timeout=3600)
def get_artist_albums_from_database(artist_name: str, sorting: str) -> Optional[list[AlbumInfo]]:
    """
    search the artist through the database
    :param sorting: sorted by: popularity, release date, randomly
    :param artist_name: artist's name
    :return: album info dict with all the info about albums
    """
    # query artist
    artist_entry = db_get_artist(artist_name)
    if not artist_entry:
        return None
    album_entries = db_get_albums_by_artist_entry(artist_entry, sorting)
    if not album_entries:
        return None
    processed_albums = process_albums_from_db(album_entries)
    return processed_albums


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

    # get artist's albums via musicbrainz (without images)
    albums = asyncio.run(mb_fetch_artists_albums(artist_name, sorting))

    # no albums on musicbrainz → try on spotify
    if not albums:
        albums = spotify_get_artists_albums(artist_name, sorting)
        if not albums:
            # no albums even on spotify
            return None
        log_artist_missing_from_db(artist_name=artist_name)
        return albums

    # find cover arts for albums found on musicbrainz
    asyncio.run(fetch_and_assign_images(albums_list=albums, artist_name=artist_name))
    albums_with_album_covers = filter_out_albums_without_album_covers(albums)
    if not albums_with_album_covers:
        return None
    enumerate_artist_albums(albums_with_album_covers)
    log_artist_missing_from_db(artist_name=artist_name)
    return albums_with_album_covers
