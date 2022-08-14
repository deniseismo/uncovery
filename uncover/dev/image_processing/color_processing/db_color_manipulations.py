import os
from typing import Optional

from flask import current_app

from uncover import create_app, db
from uncover.dev.image_processing.color_processing.image_analysis import get_salient_color_names_from_image_file, \
    get_image_dominant_hex_colors
from uncover.models import Album, Color

app = create_app()
app.app_context().push()


def get_album_entry_image_salient_colors(album_entry: Album, folder_type: str = "default") -> Optional[list[str]]:
    """
    a shortcut function to analyze album entry image to find 'salient' colors;
    salient is the most prominent image color that makes that image qualified as being of that color.
    image CAN have NO salient/prominent color, usually it's somewhat blurry or muddy pictures with no distinct color
    that stands out, not gray enough to be qualified as 'gray', etc.
    :param album_entry: album of Album class
    :param folder_type: (str) image folder: default/new
    """
    if not album_entry:
        return None
    image_folders = {
        "default": 'static/optimized_cover_art_images',
        "new": 'static/cover_art_new_batch'
    }
    cover_art_filename = album_entry.cover_art
    image_folder = image_folders[folder_type]
    image_path = os.path.join(current_app.root_path, image_folder, cover_art_filename)
    image_path = f"{image_path}-size200.jpg"
    print(image_path)
    color_names = get_salient_color_names_from_image_file(image_path)
    if not color_names:
        return None
    print(f"color names are {color_names}")
    return color_names


def add_album_entry_colors_to_db(album_entry: Album, color_names: list[str]) -> None:
    """
    add album ←→ color association; creates color if it doesn't exist yet
    :param album_entry: (Album) album from database
    :param color_names: (list[str]) list of color names
    """
    if not color_names or not album_entry:
        return None
    for color_name in color_names:
        color_entry = Color.query.filter_by(color_name=color_name).first()
        if not color_entry:
            color_entry = Color(color_name=color_name)
            db.session.add(color_entry)
            db.session.commit()
        color_entry.albums.append(album_entry)
    db.session.commit()


def get_album_entry_image_hex_colors(album_entry: Album, folder_type: str = "default") -> tuple[str]:
    """
    get top 3 most dominant colors (in hex) from album entry image; e.g. ['#FF24FF', '#FF512F', '#ABF4FD']
    :param album_entry: (Album) in database
    :param folder_type: (str) type of image folder to search image in
    :return: tuple(str) of 3 top most dominant colors (hex)
    """
    image_folders = {
        "default": 'static/optimized_cover_art_images',
        "new": 'static/cover_art_new_batch'
    }
    cover_art_filename = album_entry.cover_art
    image_folder = image_folders[folder_type]
    image_path = os.path.join(current_app.root_path, image_folder, cover_art_filename) + '-size200.jpg'
    colors = get_image_dominant_hex_colors(image_path)
    if not colors:
        print(f"-- incorrect hex colors --")
        colors = ('#FFFFFF', '#FFFFFF', '#FFFFFF')
    return colors