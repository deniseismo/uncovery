import math
import statistics
from typing import Literal, Union

from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LCHabColor, LabColor

from uncover.dev.image_processing.color_processing.color_conversion import convert_rgb_to_lch, convert_rgb_to_lab
from uncover.dev.image_processing.color_processing.color_models import RGBColor, BasicColor, ShadeColor, ImageColor


def get_dominant_color_of_bw_image(
        color_list: list[RGBColor]
) -> Literal[BasicColor.BLACK, BasicColor.WHITE, BasicColor.GRAY]:
    """
    determine the most dominant color of a black & white picture: black, white or gray;
    image must be a black & white one; check image with 'is_image_black_and_white' function beforehand
    :param color_list: a list of prominent colors (rgb values)
    :return: True if black, False if white
    """
    mean_lightness = statistics.mean(convert_rgb_to_lch(color).lch_l for color in color_list)
    if mean_lightness <= 33:
        # black
        return BasicColor.BLACK
    elif 33 < mean_lightness <= 66:
        # white
        return BasicColor.GRAY
    else:
        return BasicColor.WHITE


def is_color_gray(lch_color: LCHabColor) -> bool:
    """
    determine if color provided is gray(ish); uses chroma (color intensity) from LCH
    :param lch_color: (LCHabColor) LCH ((lightness), chroma (color intensity), hue (basic color))
    :return: True if color is gray, False otherwise
    """
    return lch_color.lch_c < 10


def get_dominant_color_of_grayish_color(
        lch_color: LCHabColor
) -> Literal[BasicColor.BLACK, BasicColor.WHITE, BasicColor.GRAY]:
    """
    determine if a grayish color is black, white or gray one;
    color must be 'grayish' → check color with 'is_color_gray' function beforehand;
    uses lightness parameter of a LCH color;
    :param lch_color: (LCHabColor) LCH ((lightness), chroma (color intensity), hue (basic color))
    :return: (Literal[BasicColor.BLACK, BasicColor.WHITE, BasicColor.GRAY])
    """
    if lch_color.lch_l <= 33:
        return BasicColor.BLACK
    elif 33 < lch_color.lch_l <= 66:
        return BasicColor.GRAY
    else:
        return BasicColor.WHITE


def get_color_difference(color_1: LabColor, color_2: LabColor) -> int:
    """
    calculates distance/difference between two colors using Delta E 2000
    :param color_1: (LabColor)
    :param color_2: (LabColor)
    :return:  Delta E CIE 2000 difference between two colors
    """
    return delta_e_cie2000(color_1, color_2)


def get_color_nearest_to_reference_colors(
        reference_colors: list[Union[BasicColor, ShadeColor]],
        query_color: RGBColor
) -> Union[BasicColor, ShadeColor]:
    """
    find the nearest color from a list of colors to the query color;
    uses Delta E CIE 2000 difference between two colors (Lab colors)
    :param reference_colors: (list[Union[BasicColor, ShadeColor]]) reference colors; search among these colors
    :param query_color: (RGBColor) a query color (R, G, B)
    :return: (Union[BasicColor, ShadeColor]) one of the reference colors that happened to be the nearest one
        (nearest to the query color)
    """
    query_color_lch = convert_rgb_to_lch(query_color)
    if is_color_gray(query_color_lch):
        return get_dominant_color_of_grayish_color(query_color_lch)

    lab_query_color = convert_rgb_to_lab(query_color)
    return min(
        reference_colors,
        key=lambda reference_color: get_color_difference(convert_rgb_to_lab(reference_color.color_values),
                                                         lab_query_color))


def get_color_nearest_to_reference_colors_by_euclidean(
        reference_colors: list[Union[BasicColor, ShadeColor]],
        query_color: RGBColor
) -> Union[BasicColor, ShadeColor]:
    """
    find the nearest color from a list of colors to the query color;
    uses Euclidean distance
    :param reference_colors: a list of main colors to base search off
    :param query_color: a query color (R, G, B)
    :return: (Union[BasicColor, ShadeColor]) one of the reference colors that happened to be the nearest one
        (nearest to the query color)
    """
    query_color_lch = convert_rgb_to_lch(query_color)
    if is_color_gray(query_color_lch):
        return get_dominant_color_of_grayish_color(query_color_lch)
    return min(
        reference_colors,
        key=lambda reference_color: math.sqrt(sum((s - q) ** 2 for s, q in zip(reference_color, query_color)))
    )


def get_basic_color_names_from_image_color(image_color: ImageColor) -> list[str]:
    """
    parses image color to get a list of 'basic' color names from;
    adds a special 'black_and_white' color-flag if the image is proven to be b&w
    :param image_color: (ImageColor) namedtuple with all the needed info about distinct color & black-and-whiteness
    :return: (list[str]) list of basic color names
    """
    color_names = []
    basic_color_name = image_color.color.base_color_name.lower()
    color_names.append(basic_color_name)
    if image_color.is_black_and_white:
        color_names.append("black_and_white")
    return color_names
