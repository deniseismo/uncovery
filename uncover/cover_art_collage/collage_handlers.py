import os
import secrets
import urllib.request
from io import BytesIO
from typing import Optional
from urllib.error import URLError, HTTPError

from PIL import Image
from flask import current_app

from uncover import cache
from uncover.schemas.characteristics import ImageOffset, ImageSize
from uncover.utilities.convert_values import get_collage_dimensions


def arrange_the_images(
        images: list[Image.Image],
        collage_image: Image.Image,
        width: int,
        image_size: ImageSize,
        offset: ImageOffset = ImageOffset(0, 0)
):
    """
    arrange (paste) given images in a collage
    :param images: a list of PIL Images
    :param collage_image: the output image
    :param width: (of the current 'frame' or part of the output picture we need to put images in)
    :param image_size: a tuple (width, height) of images to put in
    :param offset: a tuple (x_offset, y_offset) where we need to start putting images in
    """
    to_fit = (width - offset.x) // image_size.width
    for counter, image in enumerate(images):
        resized_image = image.resize(image_size, Image.LANCZOS)
        paste_region = _calculate_image_paste_region(
            image_number=counter,
            image_size=image_size,
            offset=offset,
            to_fit=to_fit
        )
        collage_image.paste(resized_image, paste_region)


def _calculate_image_paste_region(
        image_number: int,
        image_size: ImageSize,
        offset: ImageOffset,
        to_fit: int
) -> tuple[int, int]:
    """
    get paste region for image to paste into (where exactly to put in a collage)
    :param image_number:
    :param image_size: ImageSize(width, height)
    :param offset: ImageOffset(x, y)
    :param to_fit: how many to fit
    :return: tuple(int, int)
    """
    return offset.x + image_number % to_fit * image_size.width, offset.y + (image_number // to_fit) * image_size.height


def _get_image_file_from_url(image_url: str) -> Optional[Image.Image]:
    """
    open a given url to get image file as a Pillow Image object
    :param image_url: (str) url to image (local/external)
    :return: Pillow Image file of an opened image
    """
    try:
        req = urllib.request.Request(url=image_url)
        req.add_header("User-Agent", current_app.config['USER_AGENT'])
        try:
            with urllib.request.urlopen(req) as response:
                image_bytes = response.read()
                image = Image.open(BytesIO(image_bytes))
            return image
        except (URLError, HTTPError) as e:
            print(e)
            return None
    except ValueError as e:
        print(e)
        try:
            print(current_app.root_path, image_url)
            path = os.path.join(current_app.root_path, image_url)
            print(f'final path= {path}')
            image = Image.open(path)
            return image
        except (OSError, ValueError) as e:
            print(e)
            return None


def _collect_opened_images(a_list_of_image_urls: list[str]) -> list[Optional[Image.Image]]:
    """
    get a list of opened images from image urls (collect only images that could be opened)
    :param a_list_of_image_urls: list of image urls
    :return: list of Pillow Image objects
    """
    images = []
    for image_url in a_list_of_image_urls:
        image = _get_image_file_from_url(image_url)
        if not image:
            continue
        images.append(image)
    return images


def create_a_collage(cover_art_urls: list[str], filename_path: str):
    """
    create a collage from given cover art images (image urls)
    :param cover_art_urls: a list of filenames of all the images to create a collage from
    :param filename_path: a filename (prior randomized) to save as
    """
    if not cover_art_urls or not filename_path:
        return False
    IMAGE_SIZES_TABLE = {
        'small': ImageSize(300, 300),
        'default': ImageSize(600, 600),
        'large': ImageSize(900, 900)
    }
    number_of_urls = len(cover_art_urls)
    images = _collect_opened_images(cover_art_urls)
    if not images:
        # TODO: raise Error, catch somewhere outside the function
        return None
    number_of_images = len(images)
    print(f"{number_of_urls=}, {number_of_images=}")

    width, height = get_collage_dimensions(number_of_images)
    collage_image = Image.new('RGB', (width, height))

    # arrange album images in a collage depending on the number of images in it
    if number_of_images == 4:
        arrange_the_images(images[0:1], collage_image, width, IMAGE_SIZES_TABLE['large'])
        arrange_the_images(images[1:], collage_image, width, IMAGE_SIZES_TABLE['small'], ImageOffset(900, 0))
    elif number_of_images == 5:
        arrange_the_images(images[0:2], collage_image, width, IMAGE_SIZES_TABLE['large'])
        arrange_the_images(images[2:], collage_image, width, IMAGE_SIZES_TABLE['default'], ImageOffset(0, 900))
    elif number_of_images == 7:
        arrange_the_images(images[0:1], collage_image, width, IMAGE_SIZES_TABLE['large'])
        arrange_the_images(images[1:], collage_image, width, IMAGE_SIZES_TABLE['small'], ImageOffset(900, 0))
    elif number_of_images == 8:
        arrange_the_images(images[0:2], collage_image, width, IMAGE_SIZES_TABLE['large'])
        arrange_the_images(images[2:], collage_image, width, IMAGE_SIZES_TABLE['default'], ImageOffset(0, 900))
    else:
        arrange_the_images(images, collage_image, width, IMAGE_SIZES_TABLE['default'])
    # save the collage to a file
    collage_image.save(filename_path, quality=95)


@cache.memoize(timeout=360)
def save_collage(cover_art_urls: list[str]):
    """
    save collage created from given images (image urls)
    :param: a list of album filenames
    :return: a filename of the collage created
    """
    if not cover_art_urls:
        return None
    random_hex = secrets.token_hex(8)
    # randomize filename
    collage_filename = f"{random_hex}.jpg"
    collage_path = os.path.join(current_app.root_path, 'static/collage', collage_filename)
    # trigger collage creator function
    create_a_collage(cover_art_urls, collage_path)
    return collage_filename
