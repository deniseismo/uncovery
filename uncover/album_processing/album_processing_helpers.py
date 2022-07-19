import random
from operator import attrgetter
from typing import NamedTuple

from uncover.schemas.album_schema import AlbumInfo


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
        "latest": SortingParams("release_date", True),
        "earliest": SortingParams("release_date", False)
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
    for count, album in enumerate(albums):
        album.id = count
    return True
