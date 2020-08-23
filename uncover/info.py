import os
from os import listdir
from os.path import isfile, join


images_folder = 'uncover/static/images/fail'


def get_failure_images():
    failure_art_list = [os.path.join('images/fail/', f) for f in listdir(images_folder) if isfile(join(images_folder, f))]
    return failure_art_list

