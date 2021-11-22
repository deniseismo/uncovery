from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor, XYZColor, sRGBColor, LCHabColor

# rgb = sRGBColor(76, 75, 74, is_upscaled=True)
# xyz = convert_color(rgb, XYZColor)
# lch = convert_color(xyz, LCHabColor)
# print(lch.lch_c)
# print(dir(lch))
colors = [(21, 27, 35), (234, 234, 227), (142, 149, 150), (186, 193, 191), (116, 116, 119), (172, 172, 176),
          (108, 124, 122), (116, 124, 116), (172, 180, 164)]


def convert_rgb_to_lch(rgb_color: tuple):
    """
    converts RGB to LCH ((lightness), chroma (color intensity), hue (basic color))
    :param rgb_color: (R, G, B)
    :return: LCHabColor (lch_l, lch_c, lch_h)
    """
    rgb = sRGBColor(*rgb_color, is_upscaled=True)
    xyz = convert_color(rgb, XYZColor)
    lch = convert_color(xyz, LCHabColor)
    # print(f'LCH: {lch}')
    return lch


def convert_rgb_to_lab(rgb_color: tuple):
    """
    converts RGB to LCH ((lightness), chroma (color intensity), hue (basic color))
    :param rgb_color: (R, G, B)
    :return: LCHabColor (lch_l, lch_c, lch_h)
    """
    rgb = sRGBColor(*rgb_color, is_upscaled=True)
    xyz = convert_color(rgb, XYZColor)
    lab = convert_color(xyz, LabColor)
    print(f'LAB: {lab}')
    return lab


def is_color_gray(lch_color):
    """
    :param lch_color: LCH ((lightness), chroma (color intensity), hue (basic color))
    :return: if chroma < 10 return True
    """
    return lch_color.lch_c < 10


def is_color_black_or_white(lch_color):
    if is_color_gray(lch_color):
        if lch_color.lch_l <= 33:
            return 0, 0, 0, "black"
        elif 34 <= lch_color.lch_l <= 66:
            return 128, 128, 128, 'gray'
        else:
            return 255, 255, 255, "white"
    return False


def get_color_difference(color_1, color_2):
    """
    determines how close/similar two colors are
    :param color_1: LAB color
    :param color_2: LAB color
    :return:  Delta E CIE 2000 difference between two colors
    """
    if not isinstance(color_1, LabColor) or not isinstance(color_2, LabColor):
        return None
    return delta_e_cie2000(color_1, color_2)


def nearest_color_delta(base_colors, query_color):
    """
    uses Delta E CIE 2000 difference between two colors (Lab colors)
    :param base_colors: a list of main colors to base search off
    :param query_color: a query color (R, G, B)
    :return:
    """
    lch_version = convert_rgb_to_lch(query_color)
    black_or_white = is_color_black_or_white(lch_version)
    if not black_or_white:
        lab_query_color = convert_rgb_to_lab(query_color)
        return min(base_colors, key=lambda subject: get_color_difference(
            convert_rgb_to_lab(subject[:3]),
            lab_query_color
        ))
    return black_or_white

    # lab_query_color = convert_rgb_to_lab(query_color)
    # return min(base_colors, key=lambda subject: get_color_difference(
    #     convert_rgb_to_lab(subject[:3]),
    #     lab_query_color
    # ))

# for color in colors:
#     print(convert_rgb_to_lab(color))
