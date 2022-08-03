from typing import Optional

from uncover.album_processing.process_albums_from_database import process_albums_from_db
from uncover.client.database_manipulation.db_album_handlers import db_get_albums_by_filters
from uncover.schemas.album_schema import AlbumInfo
from uncover.utilities.convert_values import convert_a_list_of_dates_to_time_span
from uncover.utilities.misc import timeit


@timeit
def get_albums_by_filters(
        genres: list[str],
        a_list_of_time_span_dates: list[int, int],
        colors_list: list[str]
) -> Optional[list[AlbumInfo]]:
    """
    get albums given user's filters
    :param colors_list: album colors picked
    :param genres: a list of music tags/genres
    :param a_list_of_time_span_dates: a list of a time span range [start_year, end_year]
    :return:
    """
    time_span = convert_a_list_of_dates_to_time_span(a_list_of_time_span_dates)

    print(f'time_span: {time_span}, genres: {genres}, colors: {colors_list}')

    album_entries = db_get_albums_by_filters(genres, time_span, colors_list)
    # build an album info dict
    if not album_entries:
        return None
    processed_albums = process_albums_from_db(album_entries)
    return processed_albums
