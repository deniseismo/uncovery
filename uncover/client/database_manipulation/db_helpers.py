from sqlalchemy import func
from sqlalchemy.sql import expression

from uncover.models import Album


def get_db_album_sorting_function(sorting: str) -> expression:
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
