import random
from operator import attrgetter
from typing import NamedTuple, Optional

from uncover.schemas.album_schema import AlbumInfo
from uncover.schemas.response import AlbumCoversResponse, ResponseInfo


class SortingParams(NamedTuple):
    order_by: str
    is_reversed: bool


def _get_sorting_params(sorting: str) -> SortingParams:
    """
    get sorting parameters for MusicBrainz albums for sorting type picked by user
    :param sorting: (str) popular, latest, earliest
    :return: MusicBrainzSorting
    """
    ORDER_TABLE = {
        "popular": SortingParams("rating", True),
        "latest": SortingParams("year", True),
        "earliest": SortingParams("year", False)
    }
    return ORDER_TABLE[sorting]


def sort_artist_albums(albums: list[AlbumInfo], sorting: str) -> bool:
    """
    sort artist albums based on sorting type picked by user; sort albums in place
    :param albums: a list of album dicts
    :param sorting: (str) popular, latest, earliest, shuffle
    :return:
    """
    if sorting == "shuffle":
        random.seed()
        random.shuffle(albums)
    else:
        order_by, reverse = _get_sorting_params(sorting)
        albums.sort(key=attrgetter(order_by), reverse=reverse)
    return True


def enumerate_artist_albums(albums: list[AlbumInfo]) -> bool:
    """
    enumerate albums, asc. (add respective ids/order numbers)
    :param albums: a list of AlbumInfo albums
    :return: True
    """
    for count, album in enumerate(albums):
        album.id = count
    return True


def make_album_covers_response(albums: list[AlbumInfo], info_type: str, info_query: str) -> AlbumCoversResponse:
    """
    make a AlbumCoversResponse (ready to be jsonified and sent to the user)
    :param albums: a list of processed and ready AlbumInfo
    :param info_type: type of albums returned/request made (e.g. artist, playlist, explore, etc.)
    :param info_query: information about user's request (e.g. artist's name)
    :return: AlbumCoversResponse
    """
    album_covers_response = AlbumCoversResponse(
        info=ResponseInfo(
            type=info_type,
            query=info_query
        ),
        albums=albums
    )
    return album_covers_response


def filter_out_albums_without_album_covers(albums: list[AlbumInfo]) -> list[Optional[AlbumInfo]]:
    """
    keep only albums that have album covers
    :param albums: a list of album dicts
    :return: a list of album dicts with album covers, discard albums without album covers
    """
    albums_with_albums_covers = [album for album in albums if album.image]
    return albums_with_albums_covers
