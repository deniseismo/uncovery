from flask import url_for

from uncover.schemas.album_schema import AlbumInfo
from uncover.utilities.name_filtering import get_filtered_names_list


def process_albums_from_db(album_entries: list) -> list[AlbumInfo]:
    """
    process album entries from database
    :param album_entries: a list of album entries from db
    :return: a list of album info dicts
    """
    # url_for('static', filename='collage/' + collage_filename)
    SMALL_SIZE = "size200"
    MEDIUM_SIZE = "size300"
    processed_albums = []
    for counter, album_entry in enumerate(album_entries):
        album_name = album_entry.title
        album_info = AlbumInfo(
            id=counter,
            title=album_entry.title,
            names=[album_entry.title.lower()] + get_filtered_names_list(album_name),
            image=url_for("static", filename=f"optimized_cover_art_images/{album_entry.cover_art}.jpg"),
            image_small=url_for("static",
                                filename=f"optimized_cover_art_images/{album_entry.cover_art}-{SMALL_SIZE}.jpg"),
            image_medium=url_for("static",
                                 filename=f"optimized_cover_art_images/{album_entry.cover_art}-{MEDIUM_SIZE}.jpg"),
            artist_name=album_entry.artist.name,
            artist_names=[album_entry.artist.name] + get_filtered_names_list(album_entry.artist.name),
            rating=album_entry.rating
        )
        if album_entry.artist.spotify_name:
            album_info.spotify_name = album_entry.artist.spotify_name
        if album_entry.release_date:
            album_info.release_date = album_entry.release_date.strftime("%Y")
        if album_entry.alternative_title:
            album_info.names += [album_entry.alternative_title]
            album_info.names += get_filtered_names_list(album_entry.alternative_title)
        # remove duplicates
        album_info.artist_names = list(set(album_info.artist_names))
        album_info.names = list(set(album_info.names))
        processed_albums.append(album_info)
    return processed_albums
