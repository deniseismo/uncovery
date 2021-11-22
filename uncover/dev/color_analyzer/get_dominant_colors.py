import os
import json
import csv
from tqdm import tqdm
from os.path import isfile, join

from colorthief import ColorThief
from flask import current_app

from uncover import create_app
from uncover.models import Album
from colormath.color_objects import sRGBColor, AdobeRGBColor

app = create_app()
app.app_context().push()


def log_missing_info(info):
    """
    logs missing info (missing songs/albums/releases, etc.) to a file
    """
    with open('album_colors_missing_info.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([info])


def get_rgb_to_hex(rgb_r, rgb_g, rgb_b):
    """
    gets a hex value (#RRGGBB) from RGB
    :param rgb_r: 0-255
    :param rgb_g: 0-255
    :param rgb_b: 0-255
    :return: hex color
    """
    color_object = AdobeRGBColor(rgb_r, rgb_g, rgb_b, is_upscaled=True)
    return color_object.get_rgb_hex()


def get_image_dominant_color(image_file):
    """
    get the most dominant color
    :param image_file: image filename path
    :return: a list of colors
    """
    color_thief = ColorThief(image_file)
    # gets the most dominant color
    try:
        dominant_color = color_thief.get_color(quality=1)
        dominant_object = AdobeRGBColor(*dominant_color, is_upscaled=True).get_rgb_hex()
        full_palette = color_thief.get_palette(color_count=2, quality=1)
        full_palette = [get_rgb_to_hex(*color) for color in full_palette]
        print('dominant color:', dominant_color)
        print(dominant_object)
        print('full palette:', full_palette)
        return full_palette
    except Exception as e:
        print(e)
        log_missing_info(f'{image_file} -- {e}')
        return None


def get_a_list_of_images():
    album_images_list = [join(current_app.root_path, 'static/color_testing', f) for f in
                         os.listdir(join(current_app.root_path, 'static/color_testing')) if
                         isfile(join(current_app.root_path, 'static/color_testing', f))]
    return album_images_list


def analyze_cover_arts_colors():
    """
    :return:
    """

    folder = 'static/optimized_cover_art_images'
    albums = Album.query.filter(Album.id > 26520).all()
    # album_entries = albums[0:10]
    fieldnames = ["album_id", "album_title", "artist", "colors"]
    with open("album_colors.csv", "a", encoding="utf-8") as file:
        csvfile = csv.DictWriter(file, fieldnames=fieldnames)
        # csvfile.writeheader()
        for album_entry in tqdm(albums):
            print(album_entry)
            image_filename = album_entry.cover_art
            image_path = os.path.join(current_app.root_path, folder,
                                      image_filename) + '-size200.jpg'
            colors = get_image_dominant_color(image_path)
            if not colors:
                colors = ['#FFFFFF', '#FFFFFF', '#FFFFFF']
            data = {
                "album_id": album_entry.id,
                "album_title": album_entry.title,
                "artist": album_entry.artist.name,
                "colors": colors
            }
            csvfile.writerow(data)
    # list_of_images = get_a_list_of_images()
    # with open("album_colors.csv", "a", encoding="utf-8") as file:
    #     csvfile = csv.DictWriter(file, fieldnames=["name", "colors"])
    #     csvfile.writeheader()
    #     for image in list_of_images:
    #         print('-' * 7)
    #         print(image.split('\\')[-1])
    #         colors = get_image_dominant_color(image)
    #         csvfile.writerow({
    #             "name": image.split('\\')[-1],
    #             "colors": colors
    #         })


#analyze_cover_arts_colors()

# def read_csv_filejke():
#     with open("album_colors.csv", encoding="utf-8") as file:
#         csvfile = csv.DictReader(file)
#         for row in csvfile:
#             print(list(row["colors"]))
#             for color in row["colors"].split(","):
#                 print(color.strip("'[]"), len(color.strip()), color[0])
#             print(row["colors"])
#
# read_csv_filejke()
