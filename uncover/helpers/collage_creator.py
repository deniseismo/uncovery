import os
import secrets
import urllib.request

from PIL import Image

from uncover import app
from uncover.helpers.utils import timeit


@timeit
def resize_image(image, size):
    """

    :param image: a Pillow Image object to resize
    :param size: a new size
    :return:
    """
    return image.resize(size, Image.LANCZOS)
    # if size[0] <= image.width:
    #     image.thumbnail(size, Image.ANTIALIAS)
    #     return image
    # else:
    #     return image.resize(size, Image.LANCZOS)


@timeit
def arrange_the_images(a_list_of_image_urls: list, collage_image: Image, width: int, size: tuple, offset=(0, 0)):
    """
    :param a_list_of_image_urls: a list of Pillow Image objects
    :param collage_image: the output image
    :param width: (of the current 'frame' or part of the output picture we need to put images in)
    :param size: a tuple (width, height) of images to put in
    :param offset: a tuple (x_offset, y_offset) where we need to start putting images in
    :return:
    """
    for counter, image_url in enumerate(a_list_of_image_urls):
        try:
            an_image = Image.open(urllib.request.urlopen(image_url))
        except ValueError:
            try:
                parent_directory = os.path.dirname(os.getcwd())
                path = os.getcwd() + '/uncover/' + image_url
                an_image = Image.open(path)
            except Exception:
                return None
        # an_image = Image.open(os.path.dirname(os.getcwd()) + '/static/' + image_url)
        resized = resize_image(an_image, size)
        to_fit = (width - offset[0]) // resized.width
        collage_image.paste(resized,
                            (offset[0] + counter % to_fit * resized.width,
                             offset[1] + (counter // to_fit) * resized.height))


@timeit
def create_a_collage(a_list_of_images, filename_path):
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
    album_images = a_list_of_images
    total_amount_of_albums = len(album_images)
    width = DIMENSIONS[total_amount_of_albums][0]
    height = DIMENSIONS[total_amount_of_albums][1]
    collage_image = Image.new('RGB', (width, height))

    if total_amount_of_albums in [1, 2, 3, 6, 9]:
        arrange_the_images(album_images, collage_image, width, IMAGE_SIZE['default'])
    elif total_amount_of_albums == 4:
        arrange_the_images(album_images[0:1], collage_image, width, IMAGE_SIZE['large'])
        arrange_the_images(album_images[1:], collage_image, width, IMAGE_SIZE['small'], (900, 0))
    elif total_amount_of_albums == 5:
        arrange_the_images(album_images[0:2], collage_image, width, IMAGE_SIZE['large'])
        arrange_the_images(album_images[2:], collage_image, width, IMAGE_SIZE['default'], (0, 900))
    elif total_amount_of_albums == 7:
        arrange_the_images(album_images[0:1], collage_image, width, IMAGE_SIZE['large'])
        arrange_the_images(album_images[1:], collage_image, width, IMAGE_SIZE['small'], (900, 0))
    elif total_amount_of_albums == 8:
        arrange_the_images(album_images[0:2], collage_image, width, IMAGE_SIZE['large'])
        arrange_the_images(album_images[2:], collage_image, width, IMAGE_SIZE['default'], (0, 900))

    collage_image.save(f'{filename_path}.png')


def save_collage(a_list_of_album_images):
    random_hex = secrets.token_hex(8)
    collage_filename = random_hex
    collage_path = os.path.join(app.root_path, 'static/collage', collage_filename)
    create_a_collage(a_list_of_album_images, collage_path)
    return collage_filename + '.png'
