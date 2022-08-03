from typing import Optional

from uncover.models import Artist


def db_get_artist(artist_name: str) -> Optional[Artist]:
    """
    get artist from database by artist's name
    :param artist_name: artist's name
    :return: (Artist) artist object from database
    """
    artist_entry = Artist.query.filter_by(name=artist_name).first()
    if not artist_entry:
        return None
    return artist_entry
