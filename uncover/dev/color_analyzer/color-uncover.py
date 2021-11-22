import math
import os
import statistics
from os import listdir
from os.path import isfile, join

from colorthief import ColorThief
from rgb2lch import convert_rgb_to_lch, is_color_gray, is_color_black_or_white, nearest_color_delta

images_folder = './test-images/'


def get_a_list_of_images():
    album_images_list = [os.path.join('test-images/', f) for f in listdir(images_folder) if
                         isfile(join(images_folder, f))]
    return album_images_list


SHADES = {

    # (255, 255, 255, "white"),  # white

    # (0, 0, 0, "black"),  # black
    # (52, 52, 52, 'jet'),  # black
    # (33, 33, 33, 'nero'),  # black

    (128, 128, 128, 'gray'),  # gray
    # (211, 211, 211, 'lightgray'),  # gray
    # (192, 192, 192, 'silver'),  # grey
    # (229, 228, 226, 'platinum'),  # gray

    (0, 0, 255, 'blue'),  # blue
    (0, 255, 255, 'cyan'),  # blue
    # (0, 128, 128, 'teal'),  # blue?
    (0, 0, 128, 'navyblue'),  # blue
    (0, 191, 255, 'capri'),  # blue
    (0, 123, 167, 'cerulean'),  # blue

    (139, 69, 19, 'brown'),  # brown
    (123, 63, 0, 'chocolate'),  # chocolate
    (136, 45, 23, 'sienna'),  # sienna
    (192, 64, 0, 'mahogany'),  # brown
    (112, 66, 20, 'sepia'),  # brown

    (0, 128, 0, 'green'),  # green
    (127, 255, 0, 'chartreuse'),  # green
    (0, 255, 0, "lime"),  # green
    (0, 100, 0, 'darkgreen'),  # green
    (64, 130, 109, 'viridian'),  # green

    (255, 0, 255, 'magenta'),  # magenta
    (255, 192, 203, 'pink'),  # magenta
    (255, 0, 127, 'rose'),  # magenta

    (255, 140, 0, 'orange'),  # orange
    (255, 127, 80, 'coral'),  # orange
    (226, 88, 34, 'flame'),  # orange

    (128, 0, 128, 'purple'),  # purple
    (127, 0, 255, 'violet'),  # purple
    (223, 115, 255, 'heliotrope'),  # purple

    (255, 0, 0, "red"),  # red
    (227, 66, 52, 'vermilion'),  # red
    (102, 0, 0, 'blood'),  # red
    (255, 99, 71, 'tomato'),  # red
    (128, 0, 0, 'maroon'),  # maroon
    (150, 0, 24, 'carmine'),  # red

    (255, 255, 0, 'yellow'),  # yellow
    (255, 191, 0, 'amber'),  # yellow
    (227, 255, 0, 'lemon'),  # yellow
    (255, 229, 180, 'peach'),  # yellow
}

main_colors = (
    (255, 255, 255, "white"),
    (0, 0, 0, "black"),
    (255, 0, 0, "red"),
    (227, 66, 52, 'vermilion'),
    (255, 191, 0, 'amber'),
    (127, 255, 0, 'chartreuse'),
    (127, 0, 255, 'violet'),
    (0, 255, 0, "lime"),
    (0, 0, 255, 'blue'),
    # (173, 216, 230, 'lightblue'),  # light blue
    (255, 255, 0, 'yellow'),
    (0, 255, 255, 'cyan'),
    (255, 0, 255, 'magenta'),
    (128, 0, 128, 'purple'),
    (0, 128, 128, 'teal'),
    (0, 128, 0, 'green'),
    # (152, 251, 152, 'lightgreen'),  # pale green
    # (1, 50, 32, 'darkgreen'),  # dark green
    # (112, 66, 20, 'sepia'),
    # (139, 69, 19, 'brown'),
    # (128, 128, 128, 'gray'),  # regular gray
    # (211, 211, 211, 'lightgray'),  # light gray
    (255, 140, 0, 'orange'),
    (128, 0, 0, 'maroon'),
    # (54, 69, 79, 'charcoal'),
    # (33, 33, 33, 'nero'),
    (128, 128, 0, 'olive'),

)

basic_colors = (
    (255, 255, 255, "white"),
    (0, 0, 0, "black"),
    (255, 0, 0, "red"),
    (0, 0, 255, 'blue'),
    (255, 255, 0, 'yellow'),
    (128, 0, 128, 'purple'),
    (0, 128, 0, 'green'),
    (139, 69, 19, 'brown'),
    (128, 128, 128, 'gray'),
    (255, 140, 0, 'orange'),
    (255, 0, 255, 'magenta')
)

a_list_of_basic_colors = [
    "white",
    "black",
    "black_and_white",
    "gray",
    "red",
    "green",
    "blue",
    "magenta",
    "purple",
    "yellow",
    "orange",
    "brown"
]


def get_basic_color(complex_color):
    """
    get the most basic color for the db/site
    :param complex_color: tertiary color
    :return: basic color
    """
    COLOR_MAP = {
        'white': 'white',
        'black': 'black',
        'red': 'red',
        'vermilion': 'red',
        'maroon': 'red',
        'blood': 'red',
        'yellow': 'yellow',
        'amber': 'yellow',
        'lemon': 'yellow',
        'green': 'green',
        'chartreuse': 'green',
        'olive': 'green',
        'lime': 'green',
        'coral': 'orange',
        'orange': 'orange',
        'flame': 'orange',
        'magenta': 'magenta',
        'pink': 'magenta',
        'rose': 'magenta',
        'gray': 'gray',
        'brown': 'brown',
        'blue': 'blue',
        'cyan': 'blue',
        'teal': 'blue',
        'purple': 'purple',
        'violet': 'purple',
        'lightgray': 'gray',
        'lightblue': 'blue',
        'lightgreen': 'green',
        'darkgreen': 'green',
        'nero': 'black',
        'sepia': 'brown',
        'charcoal': 'gray',
        'jet': 'black',
        'neonblue': 'blue',
        'chocolate': 'brown',
        'sienna': 'brown',
        'heliotrope': 'purple',
        'silver': 'gray',
        'platinum': 'gray',
        'bluegray': 'blue',
        'navyblue': 'blue',
        'cerulean': 'blue',
        'mahogany': 'brown',
        'peach': 'yellow',
        'tomato': 'red',
        'capri': 'blue',
        'viridian': 'green',
        'carmine': 'red'
    }
    return COLOR_MAP[complex_color]


def nearest_color(base_colors, query_color):
    """
    :param base_colors: a list of main colors to base search off
    :param query_color: a query color (R, G, B)
    :return:
    """
    lch_version = convert_rgb_to_lch(query_color)
    black_or_white = is_color_black_or_white(lch_version)
    if not black_or_white:
        return min(base_colors, key=lambda subject: math.sqrt(sum((s - q) ** 2 for s, q in zip(subject, query_color))))
    return black_or_white


def is_image_black_and_white(color_list):
    """
    determines if an images is more of a black & white one
    :param color_list: a list of prominent colors (rgb values)
    :return: True if b & w, False otherwise
    """
    # print(convert_rgb_to_lch(color).lch_c for color in color_list)
    print(f'mean: {statistics.mean(convert_rgb_to_lch(color).lch_l for color in color_list)}')
    return all(is_color_gray(convert_rgb_to_lch(color)) for color in color_list)


def is_image_black_or_white(color_list, is_black_and_white=False):
    """
    determine if a picture is more black or white
    :param color_list: a list of prominent colors (rgb values)
    :param is_black_and_white: a flag that picture is black and white (can be provided beforehand)
    :return: True if black, False if white
    """
    if not is_black_and_white:
        # it not provided
        is_black_and_white = all(is_color_gray(convert_rgb_to_lch(color)) for color in color_list)
    if is_black_and_white:
        mean_lightness = statistics.mean(convert_rgb_to_lch(color).lch_l for color in color_list)
        median_lightness = statistics.median(convert_rgb_to_lch(color).lch_l for color in color_list)
        print(f'mean lightness: {mean_lightness}')
        print(f'median lightness: {median_lightness}')
        if mean_lightness <= 33:
            # black
            return 'black'
        elif 33 < mean_lightness <= 66:
            # white
            return 'gray'
        else:
            return 'white'
    # none of the above
    return False


def get_colors_for_db(main_palette):
    """
    :param main_palette: a palette of nearest main colors (up to 3)
    :return: a list simplified color names for db
    """
    a_list_of_colors = list(map(
        lambda color: get_basic_color(color),
        main_palette
    ))
    return a_list_of_colors


def analyze_image_colors():
    black_and_white_images = []

    for count, image in enumerate(get_a_list_of_images()):
        print(count, image)
        image_colors = None
        color_thief = ColorThief(image)
        dominant_color = color_thief.get_color(quality=1)
        nearest_dominant_shade = nearest_color(SHADES, dominant_color)[-1]
        nearest_dominant_shade_2 = nearest_color_delta(SHADES, dominant_color)[-1]
        print(f'dominant color/shade: {dominant_color}, {nearest_dominant_shade}')
        print(f'dominant color/shade 2: {dominant_color}, {nearest_dominant_shade_2}')
        full_palette = color_thief.get_palette(color_count=10, quality=1)
        main_palette = color_thief.get_palette(color_count=5, quality=1)
        main_nearest_colors_shades = [nearest_color_delta(SHADES, palette_color)[-1] for palette_color in main_palette]
        print(main_nearest_colors_shades)
        is_black_or_white = is_image_black_or_white(full_palette)
        if is_black_or_white:
            # if IMAGE is black & white
            image_colors = ['black_and_white'] + [is_black_or_white]
        elif nearest_dominant_shade_2 == 'black':
            # if image is NOT black & white, but DOMINANT color is BLACK
            black_count = main_nearest_colors_shades.count('black')
            gray_count = main_nearest_colors_shades.count('gray')
            if black_count > 2 or (black_count > 1 and gray_count > 1):
                image_colors = ['black']
        elif nearest_dominant_shade_2 == 'white':
            white_count = main_nearest_colors_shades.count('white')
            gray_count = main_nearest_colors_shades.count('gray')
            if white_count > 2 or (white_count > 1 and gray_count > 1):
                image_colors = ['white']
        elif nearest_dominant_shade_2 == 'gray':
            gray_count = main_nearest_colors_shades.count('gray')
            black_count = main_nearest_colors_shades.count('black')
            white_count = main_nearest_colors_shades.count('white')
            if gray_count > 2 or (gray_count > 1 and (black_count > 0 or white_count > 0)):
                image_colors = ['gray']
        else:
            main_nearest_colors = [nearest_color(main_colors, palette_color)[-1] for palette_color in main_palette]
            simplified_dominant_shade = get_basic_color(nearest_dominant_shade)
            simplified_dominant_shade_2 = get_basic_color(nearest_dominant_shade_2)
            image_colors = simplified_dominant_shade_2
            print(f'simple: {simplified_dominant_shade_2}')
            full_nearest_colors = [nearest_color(main_colors, palette_color)[-1] for palette_color in full_palette]
            full_nearest_colors_shades = [nearest_color(SHADES, palette_color)[-1] for palette_color in
                                          full_palette] + [nearest_dominant_shade]
            # print(is_image_black_and_white(full_palette))
            simple_nearest_colors = [nearest_color(basic_colors, palette_color)[-1] for palette_color in main_palette]
            simple_nearest_colors_full = [nearest_color(basic_colors, palette_color)[-1] for palette_color in
                                          full_palette]
            nearest_dominant = nearest_color(main_colors, dominant_color)[-1]
            basic_colors_for_db = list(set(main_nearest_colors + [nearest_dominant]))
            basic_colors_for_db_shades = list(set(main_nearest_colors_shades + [nearest_dominant_shade]))
            db_colors_2 = get_colors_for_db(basic_colors_for_db_shades)

        print(f'final colors: {image_colors}')

    for count, bw in enumerate(black_and_white_images):
        print(count, bw)


analyze_image_colors()
