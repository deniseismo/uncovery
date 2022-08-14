from colormath.color_conversions import convert_color
from colormath.color_objects import LCHabColor, sRGBColor, XYZColor, LabColor, AdobeRGBColor

from uncover.dev.image_processing.color_processing.color_models import RGBColor


def convert_rgb_to_lch(rgb_color: RGBColor) -> LCHabColor:
    """
    converts RGB to LCH ((lightness), chroma (color intensity), hue (basic color))
    :param rgb_color: (R, G, B)
    :return: LCHabColor (lch_l, lch_c, lch_h)
    """
    rgb = sRGBColor(*rgb_color, is_upscaled=True)
    xyz = convert_color(rgb, XYZColor)
    lch = convert_color(xyz, LCHabColor)
    return lch


def convert_rgb_to_lab(rgb_color: tuple) -> LabColor:
    """
    converts RGB to LabColor
    :param rgb_color: (R, G, B)
    :return: LabColor (lab_l, lab_a, lab_b
    """
    rgb = sRGBColor(*rgb_color, is_upscaled=True)
    xyz = convert_color(rgb, XYZColor)
    lab = convert_color(xyz, LabColor)
    return lab


def convert_rgb_to_hex(rgb_color: RGBColor) -> str:
    """
    gets a hex value (#RRGGBB) from RGB
    :return: hex color
    """
    color_object = AdobeRGBColor(*rgb_color, is_upscaled=True)
    return color_object.get_rgb_hex()
