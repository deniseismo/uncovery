import os
import random

from uncover import cache


def pick_failure_art_image():
    """
    picks a random 'failure' cover art from a list of failure art images
    :return: a 'failure' cover art location
    """
    return random.choice(_get_failure_art_images())


@cache.cached(timeout=3600)
def _get_failure_art_images():
    """
    gets the list of all 'failure' art images found in the corresponding folder
    :return:
    """
    images_folder = 'uncover/static/images/fail'
    failure_art_list = [os.path.join('images/fail/', f)
                        for f in os.listdir(images_folder)
                        if os.path.isfile(os.path.join(images_folder, f))]
    return failure_art_list
