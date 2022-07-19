from sqlalchemy import func

from uncover.album_processing.process_albums_from_database import process_albums_from_db
from uncover.models import Album, Artist, Tag, tags, Color, colors
from uncover.schemas.response import AlbumCoversResponse, ResponseInfo
from uncover.utilities.convert_values import convert_a_list_of_dates_to_time_span
from uncover.utilities.misc import timeit


@timeit
def get_albums_by_filters(genres: list, a_list_of_time_span_dates: list, colors_list: list):
    """
    get albums given user's filters
    :param colors_list: album colors picked
    :param genres: a list of music tags/genres
    :param a_list_of_time_span_dates: a list of a time span range [start_year, end_year]
    :return:
    """
    time_span = convert_a_list_of_dates_to_time_span(a_list_of_time_span_dates)

    print(f'time_span: {time_span}, genres: {genres}, colors: {colors_list}')

    album_entries = filter_albums(genres, time_span, colors_list)
    # build an album info dict
    if not album_entries:
        return None
    processed_albums = process_albums_from_db(album_entries)
    album_covers_response = AlbumCoversResponse(
        info=ResponseInfo(
            type="explore",
            query=f"album covers for {time_span} with colors: {colors_list}"
        ),
        albums=processed_albums
    )
    return album_covers_response


def filter_albums(genres: list, time_span: tuple, colors_list: list):
    """
    filter out albums from database
    :param genres: a list of picked music genres
    :param time_span: a tuple of datetime object (start_date, end_date)
    :param colors_list: a list of picked colors
    :return:
    """
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
    filter_query = filter_query.order_by(func.random()).limit(9)

    album_entries = filter_query.all()
    return album_entries
