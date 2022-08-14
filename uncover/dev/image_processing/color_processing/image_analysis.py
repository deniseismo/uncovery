from typing import Optional, Union

from colorthief import ColorThief

from uncover.dev.image_processing.color_processing.color_analysis import is_color_gray, \
    get_color_nearest_to_reference_colors, get_dominant_color_of_bw_image, get_basic_color_names_from_image_color
from uncover.dev.image_processing.color_processing.color_conversion import convert_rgb_to_lch, convert_rgb_to_hex
from uncover.dev.image_processing.color_processing.color_models import RGBColor, ShadeColor, BasicColor, ImageColor
from uncover.dev.image_processing.color_processing.get_dominant_colors import log_missing_info


def get_salient_color_names_from_image_file(image_file: str) -> Optional[list[str]]:
    """
    get 'salient' (most prominent) color names from a given image file;
    image can have no color names
    :param image_file: (str) image filename in filesystem
    :return: (list[str] a list of colors
    """
    if not image_file:
        return None
    image_salient_color = get_image_salient_color(image_file)
    if not image_salient_color:
        print("-- image has no salient/distinct color")
        return None
    return get_basic_color_names_from_image_color(image_salient_color)


def is_image_black_and_white(palette_of_colors: list[RGBColor]) -> bool:
    """
    determine if image is black & white;
    works best if fed with 'full palette: 10 colors, quality 1 from ColorThief';
    :param palette_of_colors: (list[RGBColor]) list of the most prominent colors of a given image
    :return: True if image is black & white, False otherwise
    """
    return all(is_color_gray(convert_rgb_to_lch(color)) for color in palette_of_colors)


def get_image_salient_color(image_file: str) -> Optional[ImageColor]:
    """
    get image 'salient' (most prominent) color;
    salient is the most prominent image color that makes that image qualified as being of that color;
    can have no salient color.
    :param image_file: (str) image file in filesystem
    :return: (ImageColor) with the most prominent color and info about the image 'black-and-whiteness'
    """
    image_salient_color = None
    color_thief = ColorThief(image_file)
    # gets the most dominant color
    dominant_color = color_thief.get_color(quality=1)
    # gets a full palette of 10 colors
    full_palette = color_thief.get_palette(color_count=10, quality=1)
    # main_palette = color_thief.get_palette(color_count=3, quality=1)
    # determines if it's b&w using full palette
    main_palette = color_thief.get_palette(color_count=5, quality=1)

    print(f"{main_palette=}")
    main_nearest_colors_shades = [
        get_color_nearest_to_reference_colors(list(ShadeColor), palette_color) for palette_color in main_palette
    ]
    nearest_dominant_shade = get_color_nearest_to_reference_colors(list(ShadeColor), dominant_color)

    # second_nearest_dominant_shade = main_nearest_colors_shades[1]
    print(f"{dominant_color=}")
    print(f"{full_palette=}")
    print(f"{main_palette=}")
    print(f"intersection: {set(full_palette).intersection(set(main_palette))}")
    print(f"{nearest_dominant_shade=}")
    print(f"{main_nearest_colors_shades=}")
    # print(f"{second_nearest_dominant_shade=}")
    is_black_and_white = is_image_black_and_white(full_palette)
    if is_black_and_white:
        image_salient_color = get_dominant_color_of_bw_image(full_palette)
    elif nearest_dominant_shade == BasicColor.BLACK:
        # if image is NOT black & white, but DOMINANT color is BLACK
        if is_color_image_blackish(main_nearest_colors_shades):
            image_salient_color = BasicColor.BLACK
    elif nearest_dominant_shade == BasicColor.WHITE:
        if is_color_image_whitish(main_nearest_colors_shades):
            image_salient_color = BasicColor.WHITE
    elif nearest_dominant_shade == BasicColor.GRAY:
        if is_color_image_grayish(main_nearest_colors_shades):
            image_salient_color = BasicColor.GRAY
    else:
        # color image
        # gets the nearest shade color from (r, g, b)
        # gets a simplified version of a color name (shade/tone → simple color) for the database
        image_salient_color = nearest_dominant_shade
    if not image_salient_color:
        return None
    return ImageColor(image_salient_color, is_black_and_white)


def get_image_dominant_hex_colors(image_file: str, color_count: int = 2) -> Optional[tuple[str]]:
    """
    get image's most dominant colors as hex colors;
    :param image_file: (str) image file in filesystem
    :param color_count: (int) number of colors in color palette, default is 2 (will actually return 3 colors)
    :return: (list[str, str, str]) a list of most dominant hex colors
    """
    color_thief = ColorThief(image_file)
    # gets the most dominant color
    try:
        full_palette = color_thief.get_palette(color_count=color_count, quality=1)
        full_palette = tuple([convert_rgb_to_hex(color) for color in full_palette])
        print('full palette:', full_palette)
        return full_palette
    except Exception as e:
        print(e)
        log_missing_info(f'{image_file} -- {e}')
        return None


def is_color_image_whitish(nearest_shades: list[Union[ShadeColor, BasicColor]]) -> bool:
    """
    determine if color (i.e. not black and white) image can be called 'white' or 'whitish'
    if image is NOT black & white, but DOMINANT color is WHITE;
    image's dominant color MUST BE WHITE
    :param nearest_shades: (list[Union[ShadeColor, BasicColor]]) list of main nearest shade colors
    :return True if color image is whitish, Else otherwise
    """
    white_count = nearest_shades.count(BasicColor.WHITE)
    gray_count = nearest_shades.count(BasicColor.GRAY)
    return white_count > 2 or (white_count > 1 and gray_count > 1)


def is_color_image_blackish(nearest_shades: list[Union[ShadeColor, BasicColor]]) -> bool:
    """
    determine if color (i.e. not black and white) image can be called 'black' or 'blackish'
    # if image is NOT black & white, but DOMINANT color is BLACK;
    image's dominant color MUST BE BLACK
    :param nearest_shades: (list[Union[ShadeColor, BasicColor]]) list of main nearest shade colors
    :return True if color image is blackish, Else otherwise
    """
    black_count = nearest_shades.count(BasicColor.BLACK)
    gray_count = nearest_shades.count(BasicColor.GRAY)
    return black_count > 2 or (black_count > 1 and gray_count > 1)


def is_color_image_grayish(nearest_shades: list[Union[ShadeColor, BasicColor]]) -> bool:
    """
    determine if color (i.e. not black and white) image can be called 'gray' or 'grayish'
    if image is NOT black & white, but DOMINANT color is GRAY;
    image's dominant color MUST BE GRAY
    :param nearest_shades: (list[Union[ShadeColor, BasicColor]]) list of main nearest shade colors
    :return True if color image is grayish, Else otherwise
    """
    gray_count = nearest_shades.count(BasicColor.GRAY)
    black_count = nearest_shades.count(BasicColor.BLACK)
    white_count = nearest_shades.count(BasicColor.WHITE)
    return gray_count > 2 or (gray_count > 1 and (black_count > 0 or white_count > 0))
