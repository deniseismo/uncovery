import os
import secrets
import urllib.request

from PIL import Image
from flask import current_app

from uncover import cache
from uncover.utilities.misc import timeit


@timeit
def get_resized_image(image, size):
    """
    get a resized copy of an image
    :param image: a Pillow Image object to resize
    :param size: a new size
    :return: a resized image
    """
    return image.resize(size, Image.LANCZOS)


@timeit
def arrange_the_images(a_list_of_image_urls: list, collage_image: Image, width: int, size: tuple, offset=(0, 0)):
    """
    :param a_list_of_image_urls: a list of image URLs
    :param collage_image: the output image
    :param width: (of the current 'frame' or part of the output picture we need to put images in)
    :param size: a tuple (width, height) of images to put in
    :param offset: a tuple (x_offset, y_offset) where we need to start putting images in
    :return:
    """
    for counter, image_url in enumerate(a_list_of_image_urls):
        print(f"{counter}: {image_url}")
        try:
            an_image = Image.open(urllib.request.urlopen(image_url))
        except ValueError:
            try:
                path = os.path.join(current_app.root_path, image_url)
                an_image = Image.open(path)
            except (OSError, ValueError):
                return None
        resized_image = get_resized_image(an_image, size)
        to_fit = (width - offset[0]) // resized_image.width
        collage_image.paste(resized_image,
                            (offset[0] + counter % to_fit * resized_image.width,
                             offset[1] + (counter // to_fit) * resized_image.height))


@timeit
def create_a_collage(cover_art_urls: list, filename_path: str):
    """
    a main collage creator function
    :param cover_art_urls: a list of filenames of all the images to create a collage from
    :param filename_path: a filename (prior randomized) to save as
    :return:
    """
    if not cover_art_urls or not filename_path:
        return False
    DIMENSIONS = {
        1: (600, 600),
        2: (1200, 600),
        3: (1800, 600),
        4: (1200, 900),
        5: (1800, 1500),
        6: (1800, 1200),
        7: (1500, 900),
        8: (1800, 2100),
        9: (1800, 1800)
    }
    IMAGE_SIZE = {
        'small': (300, 300),
        'default': (600, 600),
        'large': (900, 900)
    }
    number_of_cover_art_images = len(cover_art_urls)
    width = DIMENSIONS[number_of_cover_art_images][0]
    height = DIMENSIONS[number_of_cover_art_images][1]
    collage_image = Image.new('RGB', (width, height))

    # arrange album images in a collage depending on the number of images in it
    if number_of_cover_art_images in [1, 2, 3, 6, 9]:
        arrange_the_images(cover_art_urls, collage_image, width, IMAGE_SIZE['default'])
    elif number_of_cover_art_images == 4:
        arrange_the_images(cover_art_urls[0:1], collage_image, width, IMAGE_SIZE['large'])
        arrange_the_images(cover_art_urls[1:], collage_image, width, IMAGE_SIZE['small'], (900, 0))
    elif number_of_cover_art_images == 5:
        arrange_the_images(cover_art_urls[0:2], collage_image, width, IMAGE_SIZE['large'])
        arrange_the_images(cover_art_urls[2:], collage_image, width, IMAGE_SIZE['default'], (0, 900))
    elif number_of_cover_art_images == 7:
        arrange_the_images(cover_art_urls[0:1], collage_image, width, IMAGE_SIZE['large'])
        arrange_the_images(cover_art_urls[1:], collage_image, width, IMAGE_SIZE['small'], (900, 0))
    elif number_of_cover_art_images == 8:
        arrange_the_images(cover_art_urls[0:2], collage_image, width, IMAGE_SIZE['large'])
        arrange_the_images(cover_art_urls[2:], collage_image, width, IMAGE_SIZE['default'], (0, 900))

    # save the collage to a file
    collage_image.save(filename_path, quality=95)


@cache.memoize(timeout=360)
def save_collage(cover_art_urls: list):
    """
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
