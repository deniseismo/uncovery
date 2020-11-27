import math
import os
import statistics

from colorthief import ColorThief
from flask import current_app
from rgb2lch import convert_rgb_to_lch, is_color_gray, is_color_black_or_white, nearest_color_delta
from tqdm import tqdm

from uncover import db, create_app
from uncover.models import Album, Color

app = create_app()
app.app_context().push()

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


def analyze_image_colors(image_file):
    """
    analyzes colors of a given image
    determines if an images is black and white (specifies if it's black, white or gray) using full palette of
    prominent colors → uses LCH, C (chroma) in particular,
    or a color image using the most dominant color
    :param image_file: image filename
    :return: a list of colors
    """
    if not image_file:
        return None
    print(image_file)
    color_thief = ColorThief(image_file)
    # gets the most dominant color
    dominant_color = color_thief.get_color(quality=1)
    # gets a full palette of 10 colors
    full_palette = color_thief.get_palette(color_count=10, quality=1)
    # main_palette = color_thief.get_palette(color_count=3, quality=1)
    # determines if it's b&w using full palette
    is_black_or_white = is_image_black_or_white(full_palette)
    if is_black_or_white:
        image_colors = ['black_and_white'] + [is_black_or_white]
        print(image_colors)
    else:
        # color image
        # gets the nearest shade color from (r, g, b)
        nearest_dominant_shade = nearest_color_delta(SHADES, dominant_color)[-1]
        # gets a simplified version of a color name (shade/tone → simple color) for the database
        simplified_dominant_shade = get_basic_color(nearest_dominant_shade)
        image_colors = [simplified_dominant_shade]
    return image_colors


def populate_album_colors():
    all_albums = Album.query.all()
    for album_entry in tqdm(all_albums):
        add_album_color(album_entry)


def add_album_color(album_entry: Album):
    """

    :param album_entry: album of Album class
    :return:
    """
    if not album_entry:
        return None
    print(f'... analyzing {album_entry.title} ...')
    image_filename = album_entry.cover_art
    image_path = os.path.join(current_app.root_path, 'static/optimized_cover_art_images',
                              image_filename) + '-size200.jpg'
    try:
        color_names = analyze_image_colors(image_path)
    except Exception as e:
        print('__error__')
        print(e)
        return
    if color_names:
        print(f'{color_names}')
        for color in color_names:
            print(color)
            color_entry = Color.query.filter_by(color_name=color).first()
            if not color_entry:
                # add the tag if not exists
                color_entry = Color(color_name=color)
                db.session.add(color_entry)
                db.session.commit()
            # append artist to the tag, thus creating the many-to-many association between tags & artists
            color_entry.albums.append(album_entry)
    db.session.commit()

# def delete_colors():
#     colors = Color.query.all()
#     for color in colors:
#         print(color.color_name)
#         db.session.delete(color)
#         db.session.commit()
# #delete_colors()

# populate_album_colors()
