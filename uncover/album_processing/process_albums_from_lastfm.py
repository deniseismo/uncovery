from flask import url_for

from uncover.client.database_manipulation.db_album_handlers import db_find_album_by_name
from uncover.cover_art_finder.cover_art_handlers import ultimate_album_image_finder
from uncover.music_apis.lastfm_api.lastfm_artist_handlers import lastfm_get_artist_correct_name
from uncover.schemas.album_schema import AlbumInfo
from uncover.utilities.name_filtering import get_filtered_name, get_filtered_names_list


def process_lastfm_user_top_albums(albums: list[dict], image_size: int = 3) -> list[AlbumInfo]:
    """
    extract all the needed info from artist's albums found on Spotify
    :param albums: a list of Spotify albums by artist; list[SimpleAlbum]
    :param image_size: 0 - small (34x34), 1 - medium (64x64), 2 - large (174x174), 3 - XL (300x300)
    :return: list[AlbumInfo]
    """
    a_set_of_titles = set()
    processed_albums = []
    for album in albums:
        album_name = album['name']
        album_filtered_name = get_filtered_name(album_name)

        if album_filtered_name in a_set_of_titles:
            continue
        resizable = True
        album_image = None
        artist_name = album['artist']['name']
        artist_correct_name = lastfm_get_artist_correct_name(artist_name)
        if artist_correct_name:
            artist_name = artist_correct_name
        # try getting the album image through database
        album_entry_from_db = db_find_album_by_name(artist_name, album_name)
        if not album_entry_from_db and album_filtered_name != album_name:
            # second attempt in case the album name was poorly written
            album_entry_from_db = db_find_album_by_name(artist_name, album_filtered_name)
        if album_entry_from_db:
            album_image = album_entry_from_db.cover_art
        # try getting through the ultimate image finder function if database doesn't have the image
        if not album_image:
            resizable = False
            album_image = ultimate_album_image_finder(album_title=album_name,
                                                      artist_name=artist_name,
                                                      fast=True,
                                                      ultrafast=True)
        if not album_image:
            try:
                album_image = album['image'][image_size]['#text']
            except (TypeError, IndexError, KeyError):
                album_image = None
        if not album_image:
            continue

        album_info = AlbumInfo(
            title=album_name,
            names=[album_name] + get_filtered_names_list(album_name),
            artist_name=artist_name,
            artist_names=[artist_name] + get_filtered_names_list(artist_name),
        )
        if resizable:
            album_info.image = url_for("static", filename=f"optimized_cover_art_images/{album_image}.jpg")
            album_info.image_small = url_for("static",
                                             filename=f"optimized_cover_art_images/{album_image}-size200.jpg")
            album_info.image_medium = url_for("static",
                                              filename=f"optimized_cover_art_images/{album_image}-size300.jpg")
        else:
            album_info.image = album_image

            # remove duplicates
        album_info.remove_duplicate_names()
        # add to a set of unique titles
        a_set_of_titles.add(album_filtered_name)
        processed_albums.append(album_info)

    return processed_albums
