from datetime import datetime

import aiohttp

from uncover.music_apis.lastfm_api.lastfm_album_handlers import lastfm_get_album_listeners, lastfm_fetch_album_listeners
from uncover.music_apis.musicbrainz_api.mb_album_handlers import mb_get_album_alternative_name, \
    mb_get_album_release_date, mb_fetch_album_alternative_name, mb_fetch_album_release_date
from uncover.schemas.album_schema import AlbumInfo
from uncover.utilities.convert_values import parse_release_date
from uncover.utilities.name_filtering import get_filtered_name, get_filtered_names_list


def process_musicbrainz_artist_albums(
        albums: list[dict],
        artist: str,
        sorting: str,
        unique_titles_only: bool = False
) -> list[AlbumInfo]:
    """
    extract all the needed info from artist's albums found on MusicBrainz (no images)
    :param albums: a list of dicts with all metadata from musicbrainz
    :param artist: artist's name
    :param sorting: sorting type [shuffle, popular, earliest, latest]
    :param unique_titles_only:
    :return:
    """
    processed_albums = []
    # initialize a set of titles used to filter duplicate titles
    a_set_of_titles = set()
    for album in albums:
        album_mbid = album['id']
        alternative_name = mb_get_album_alternative_name(album_mbid)
        full_title = album['title'].replace("’", "'")
        print(full_title)
        correct_title = full_title.lower()
        rating = lastfm_get_album_listeners(correct_title, artist)

        if unique_titles_only:
            filtered_name = get_filtered_name(full_title)
            if filtered_name in a_set_of_titles:
                continue
            a_set_of_titles.add(filtered_name)

        album_info = AlbumInfo(
            title=full_title,
            artist_name=artist,
            names=[correct_title] + get_filtered_names_list(full_title),
            rating=rating if rating else 0,
            artist_names=[artist],
            mbid=album_mbid
        )
        # get release dates only if sorting is date-based
        if sorting in ["earliest", "latest"]:
            release_date = mb_get_album_release_date(album_mbid)
            parsed_release_date = parse_release_date(release_date, forced_parsing=True)
            album_info.release_date = parsed_release_date
        # add an alternative album name if exists
        if alternative_name:
            alternative_name = alternative_name.replace("“", "").replace("”", "")
            album_info.alternative_name = alternative_name
            album_info.names += alternative_name
            album_info.names += get_filtered_names_list(alternative_name)

        # filters duplicate album names
        album_info.remove_duplicate_names()
        processed_albums.append(album_info)
    return processed_albums


async def add_processed_mb_album(
        album: dict,
        set_of_titles: set,
        session: aiohttp.ClientSession,
        albums_list: list,
        artist: str,
        sorting: str
):
    """
    :param album: an album to add
    :param set_of_titles: a set of titles (or mbids) used to filter out duplicates
    :param session: aiohttp object
    :param albums_list: destination album list
    :param artist: artist's name
    :param sorting: shuffle, popular, earliest, latest, etc
    :return:
    """
    if not album or not artist:
        return None
    album_mbid = album["id"]
    alternative_name = await mb_fetch_album_alternative_name(album_mbid, session)
    print(alternative_name)
    full_title = album['title'].replace("’", "'")
    print(full_title)
    correct_title = full_title.lower()
    rating = await lastfm_fetch_album_listeners(correct_title, artist, session)
    print(rating)

    album_info = AlbumInfo(
        title=full_title,
        artist_name=artist,
        names=[correct_title] + get_filtered_names_list(full_title),
        rating=rating if rating else 0,
        artist_names=[artist],
        mbid=album_mbid
    )
    if sorting in ["earliest", "latest"]:
        release_date = await mb_fetch_album_release_date(album_mbid, session)
        parsed_release_date = parse_release_date(release_date, forced_parsing=True)
        album_info.release_date = parsed_release_date
    if alternative_name:
        alternative_name = alternative_name.replace("“", "").replace("”", "")
        album_info.alternative_name = alternative_name
        album_info.names += alternative_name
        album_info.names += get_filtered_names_list(alternative_name)

    # filters duplicate album names
    album_info.remove_duplicate_names()

    # add an album to the albums list only if it's a new one (by mbid)
    if album_mbid not in set_of_titles:
        set_of_titles.add(album_mbid)
        albums_list.append(album_info)
