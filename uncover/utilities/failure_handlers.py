import os
import random

from uncover import cache


def display_failure_art(list_of_images: list):
    """
    picks a random 'failure' cover art from a list
    :return: a 'failure' cover art location
    """
    return random.choice(list_of_images)


@cache.cached(timeout=3600)
def get_failure_images():
    """
    gets the list of all 'failure' art images found in the corresponding folder
    :return:
    """
    images_folder = 'uncover/static/images/fail'
    failure_art_list = [os.path.join('images/fail/', f)
                        for f in os.listdir(images_folder)
                        if os.path.isfile(os.path.join(images_folder, f))]
    return failure_art_list