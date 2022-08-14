import os
import secrets
import urllib.request
from io import BytesIO
from os import listdir
from os.path import isfile, join
from typing import Optional
from urllib.error import URLError, HTTPError

from PIL import Image
from flask import current_app


def open_image_from_external_url(image_url: str) -> Optional[Image.Image]:
    """
    open image from external source
    :param image_url: (str) image url
    :return: (Image.Image) opened Pillow Image object
    """
    req = urllib.request.Request(url=image_url)
    req.add_header("User-Agent", current_app.config['USER_AGENT'])
    try:
        with urllib.request.urlopen(req) as response:
            image_bytes = response.read()
            image = Image.open(BytesIO(image_bytes)).convert('RGB')
        return image
    except (URLError, HTTPError) as e:
        print(e)
        return None


def save_image_file(image: Image.Image) -> Optional[str]:
    """
    save image to filesystem in three sizes/copies (original, 200px, 300px)
    :param image: (Image.Image) opened Pillow Image object
    :return: (str) image filename
    """
    if image.width >= 900:
        image.thumbnail((900, 900), Image.ANTIALIAS)
    image_filename = secrets.token_hex(8)
    image_path = os.path.join(current_app.root_path, 'static/cover_art_new_batch', image_filename)
    try:
        image.save(f'{image_path}.jpg', quality=95)

        image_200 = image
        image_300 = image
        if image.width > 300:
            # make pictures smaller if the original is bigger than 300 pixels wide
            image_200 = image.resize((200, 200), Image.LANCZOS)
            image_300 = image.resize((300, 300), Image.LANCZOS)

        # save (smaller) copies
        image_200.save(f'{image_path}-size200.jpg', quality=95)
        image_300.save(f'{image_path}-size300.jpg', quality=95)
    except (OSError, ValueError) as e:
        print(e)
        return None
    return image_filename


def save_image_from_external_source(image_url: str) -> Optional[str]:
    """
    a shortcut function for saving image from external url
    :param image_url: (str) image's external url
    :return: (str) image filename (as it's saved in filesystem)
    """
    image_file = open_image_from_external_url(image_url)
    if not image_file:
        return None
    image_filename = save_image_file(image_file)
    if not image_file:
        return None
    return image_filename


def get_a_list_of_images() -> list[str]:
    """
    get a list of image files in cover art directory
    :return: (list[str]) list of image filenames
    """
    COVER_ART_FOLDER = 'static/cover_art_images'
    COVER_ART_FOLDER_PATH = os.path.join(current_app.root_path, COVER_ART_FOLDER)
    album_images_list = [
        os.path.join(COVER_ART_FOLDER_PATH, f) for f in listdir(COVER_ART_FOLDER_PATH)
        if isfile(join(COVER_ART_FOLDER_PATH, f))
    ]
    return album_images_list
