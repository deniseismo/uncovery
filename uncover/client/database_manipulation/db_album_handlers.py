from typing import Optional

from fuzzywuzzy import fuzz
from sqlalchemy import func

from uncover.client.database_manipulation.db_artist_handlers import db_get_artist
from uncover.client.database_manipulation.db_helpers import get_db_album_sorting_function
from uncover.models import Artist, Album, tags, Tag, colors, Color
from uncover.schemas.characteristics import TimeSpan
from uncover.utilities.logging_handlers import log_artist_missing_from_db
from uncover.utilities.misc import timeit


def db_get_albums_by_artist_entry(artist_entry: Artist, sorting: str, limit: int = 9) -> Optional[list[Album]]:
    """
    get artist's albums from database (given Artist from db)
    :param artist_entry: (Artist) artist found in database
    :param sorting: (str) sorting as per user's request
    :param limit: (int) limit the number of albums returned
    :return: (list[Album]) Albums by Artist from db
    """
    order_by = get_db_album_sorting_function(sorting)
    album_entries = Album.query.filter_by(artist=artist_entry).order_by(order_by).limit(limit).all()
    if not album_entries:
        return None
    return album_entries


@timeit
def db_find_album_by_name(artist_name: str, album_to_find: str) -> Optional[Album]:
    """
    finds a specific album image via database
    :param artist_name: artist's name
    :param album_to_find: album's title
    :return:
    """
    artist_entry = db_get_artist(artist_name)
    if not artist_entry:
        # no such artist found
        # logs artist to the missing artists list log
        log_artist_missing_from_db(artist_name=artist_name)
        return None

    albums_by_artist_query = Album.query.with_parent(artist_entry)
    album_entry = albums_by_artist_query.filter(Album.title == album_to_find).first()
    if album_entry:
        return album_entry
    album_entries = albums_by_artist_query.all()
    album_found = _find_album_among_album_entries_in_db(album_to_find, album_entries)
    if not album_found:
        return None
    return album_found


def _find_album_among_album_entries_in_db(album_to_find: str, album_entries: list[Album]) -> Optional[Album]:
    """
    pick absolute best match (strict ratio threshold) among album entries (Albums from database)
    :param album_to_find: (str) album's title
    :param album_entries: (list[Album]) a list of Albums from database (guaranteed to be albums by correct artist)
    :return: (Album) best-matching Album from database
    """
    best_match = None
    ratio_threshold = 94
    album_to_find = album_to_find.lower()
    for album_entry in album_entries:
        album_entry_title = album_entry.title.lower()
        # implements a fuzzy match algorithm function
        current_ratio = fuzz.ratio(album_entry_title, album_to_find)
        partial_ratio = fuzz.partial_ratio(album_entry_title, album_to_find)
        if partial_ratio == 100:
            best_match = album_entry
        if current_ratio > 98:
            # found perfect match, return immediately
            return album_entry
        elif current_ratio > ratio_threshold:
            ratio_threshold = current_ratio
            best_match = album_entry
    return best_match


def db_get_albums_by_filters(genres: list, time_span: TimeSpan, colors_list: Optional[list]) -> Optional[list[Album]]:
    """
    filter out albums from database
    :param genres: a list of picked music genres
    :param time_span: a tuple of datetime object (start_date, end_date)
    :param colors_list: a list of picked colors
    :return:
    """
    ALBUM_LIMIT = 9
    start_date, end_date = time_span
    filter_query = Album.query.join(Artist, Artist.id == Album.artist_id) \
        .join(tags, (tags.c.artist_id == Artist.id)).join(Tag, (Tag.id == tags.c.tag_id)) \
        .join(colors, (colors.c.album_id == Album.id)).join(Color, (Color.id == colors.c.color_id)) \
        .filter(Album.release_date >= start_date).filter(Album.release_date <= end_date)

    if genres:
        filter_query = filter_query.filter(Tag.tag_name.in_(genres))

    if colors_list:
        filter_query = filter_query.filter(Color.color_name.in_(colors_list))
    # randomize sample
    filter_query = filter_query.order_by(func.random()).limit(ALBUM_LIMIT)

    album_entries = filter_query.all()
    return album_entries
