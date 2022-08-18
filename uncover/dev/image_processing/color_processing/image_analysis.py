import statistics
from collections import Counter
from typing import Optional, Union, Literal

from colorthief import ColorThief

from uncover.dev.image_processing.color_processing.color_analysis import is_color_gray, \
    get_color_nearest_to_reference_colors, get_basic_color_names_from_image_color
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
    try:
        color_thief = ColorThief(image_file)
        # gets the most dominant color
        dominant_color = color_thief.get_color(quality=1)
        # gets a full palette of 10 colors
        full_palette = color_thief.get_palette(color_count=10, quality=1)
        # main_palette = color_thief.get_palette(color_count=3, quality=1)
        # determines if it's b&w using full palette
        main_palette = color_thief.get_palette(color_count=5, quality=1)
    except Exception as e:
        print(f"there's been a problem with ColorThief: {e}")
        return None

    dominant_color_nearest_shade = get_color_nearest_to_reference_colors(list(ShadeColor), dominant_color)

    is_black_and_white = is_image_black_and_white(full_palette)

    if is_black_and_white:
        image_salient_color = get_salient_color_for_bw_image(full_palette)
    elif dominant_color_nearest_shade in [BasicColor.BLACK, BasicColor.WHITE, BasicColor.GRAY]:
        image_salient_color = get_salient_color_for_color_images_with_bw_dominant_colors(
            dominant_color_nearest_shade=dominant_color_nearest_shade,
            full_palette=full_palette, main_palette=main_palette
        )
        print(f"{image_salient_color=}")
        if not image_salient_color:
            print(f"-- no salient color found --")
            return None
    else:
        print("color image")
        image_salient_color = dominant_color_nearest_shade
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


def is_color_image_whitish(main_palette_nearest_shades_counter: Counter[Union[BasicColor, ShadeColor]],
                           full_palette_nearest_shades_counter: Counter[Union[BasicColor, ShadeColor]]) -> bool:
    """
    determine if color (i.e. not black and white) image can be called 'white' or 'whitish'
    if image is NOT black & white, but DOMINANT color is WHITE;
    image's dominant color MUST BE WHITE
    :param main_palette_nearest_shades_counter: (Counter[Union[BasicColor, ShadeColor]) of main palette nearest shades
    :param full_palette_nearest_shades_counter: (Counter[Union[BasicColor, ShadeColor]]) of full palette nearest shades
    :return True if color image is whitish, Else otherwise
    """
    most_common_color_in_full_palette = full_palette_nearest_shades_counter.most_common(1)[0][0]
    if most_common_color_in_full_palette not in [BasicColor.WHITE, BasicColor.GRAY]:
        print(f"{most_common_color_in_full_palette=} is not white nor gray")
        return False
    white_count = main_palette_nearest_shades_counter[BasicColor.WHITE]
    gray_count = main_palette_nearest_shades_counter[BasicColor.GRAY]
    print(white_count, gray_count)
    # return white_count > 2 or (white_count > 1 and gray_count > 1)
    return white_count > 2


def is_color_image_blackish(main_palette_nearest_shades_counter: Counter[Union[BasicColor, ShadeColor]]) -> bool:
    """
    determine if color (i.e. not black and white) image can be called 'black' or 'blackish'
    # if image is NOT black & white, but DOMINANT color is BLACK;
    image's dominant color MUST BE BLACK
    :param main_palette_nearest_shades_counter: (Counter[Union[BasicColor, ShadeColor]]) of main palette nearest shades
    :return True if color image is blackish, Else otherwise
    """
    print(main_palette_nearest_shades_counter)
    black_count = main_palette_nearest_shades_counter[BasicColor.BLACK]
    gray_count = main_palette_nearest_shades_counter[BasicColor.GRAY]
    return black_count > 2 or (black_count > 1 and gray_count > 1)


def is_color_image_grayish(main_palette_nearest_shades_counter: Counter[Union[BasicColor, ShadeColor]]) -> bool:
    """
    determine if color (i.e. not black and white) image can be called 'gray' or 'grayish'
    if image is NOT black & white, but DOMINANT color is GRAY or WHITE;
    image's dominant color MUST BE GRAY or WHITE
    :param main_palette_nearest_shades_counter: (Counter[Union[BasicColor, ShadeColor]]) list of main nearest shade colors
    :return True if color image is grayish, Else otherwise
    """
    print(main_palette_nearest_shades_counter)
    gray_count = main_palette_nearest_shades_counter[BasicColor.GRAY]
    black_count = main_palette_nearest_shades_counter[BasicColor.BLACK]
    white_count = main_palette_nearest_shades_counter[BasicColor.WHITE]
    return gray_count > 2 or (gray_count > 1 and (black_count > 0 or white_count > 0))


def get_salient_color_for_color_images_with_bw_dominant_colors(
        dominant_color_nearest_shade: Union[BasicColor, ShadeColor],
        full_palette: list[RGBColor],
        main_palette: list[RGBColor]
) -> Optional[Union[BasicColor, ShadeColor]]:
    """
    get image's salient when the image is NOT black & white,
    but the most dominant color is one of the B & W ones [black, white, gray]
    :param dominant_color_nearest_shade: (Union[BasicColor, ShadeColor]) image's most dominant nearest shade;
        should be one of the [BLACK, WHITE, GRAY]
    :param full_palette: (list[RGBColor]) list of rgb colors, full palette (up to 10 colors)
    :param main_palette: (list[RGBColor]) list of rgb colors, main palette (up to 5 colors)
    :return: ([Union[BasicColor, ShadeColor]]) image's salient color
    """
    image_salient_color = None

    main_palette_nearest_shades = [
        get_color_nearest_to_reference_colors(list(ShadeColor), palette_color) for palette_color in main_palette
    ]
    full_palette_nearest_shades = [
        get_color_nearest_to_reference_colors(list(ShadeColor), palette_color) for palette_color in full_palette
    ]
    main_palette_nearest_shades_counter = Counter(main_palette_nearest_shades)
    full_palette_nearest_shades_counter = Counter(full_palette_nearest_shades)

    if dominant_color_nearest_shade == BasicColor.BLACK:
        print("nearest dominant is black")
        # if image is NOT black & white, but DOMINANT color is BLACK
        if is_color_image_blackish(main_palette_nearest_shades_counter):
            print("blackish")
            image_salient_color = BasicColor.BLACK
    elif dominant_color_nearest_shade == BasicColor.WHITE:
        print("nearest dominant is white")
        if is_color_image_whitish(main_palette_nearest_shades_counter, full_palette_nearest_shades_counter):
            print("whitish")
            image_salient_color = BasicColor.WHITE
        elif is_color_image_grayish(main_palette_nearest_shades_counter):
            print("grayish through dominant white")
            image_salient_color = BasicColor.GRAY
    elif dominant_color_nearest_shade == BasicColor.GRAY:
        print("nearest dominant is gray")
        if is_color_image_grayish(main_palette_nearest_shades_counter):
            print("grayish")
            image_salient_color = BasicColor.GRAY
    if not image_salient_color:
        # image can't be considered white/black/gray, check alternative variants
        image_salient_color = get_alternative_salient_color(
            full_palette_nearest_shades,
            main_palette_nearest_shades
        )
    return image_salient_color


def get_alternative_salient_color(
        full_palette_nearest_shades: list[Union[ShadeColor, BasicColor]],
        main_palette_nearest_shades: list[Union[ShadeColor, BasicColor]]
) -> Optional[Union[BasicColor, ShadeColor]]:
    """
    get image's alternative salient color when the image is 'too tricky': it's not black & white,
    and checking the most dominant color didn't work out: image probably can't be considered black/white/gray;
    check image's second most dominant color as a way out
    :param full_palette_nearest_shades: (list[Union[ShadeColor, BasicColor]]) list of nearest shades from full palette
    :param main_palette_nearest_shades: (list[Union[ShadeColor, BasicColor]]) list of nearest shades from main palette
    :return: ([Union[BasicColor, ShadeColor]]) image's alternative salient color;
        (second most dominant color if everything's alright)
    """
    second_dominant_color_nearest_shade = main_palette_nearest_shades[1]
    if second_dominant_color_nearest_shade in [BasicColor.BLACK, BasicColor.WHITE, BasicColor.GRAY, ShadeColor.GRAY]:
        print(f"{second_dominant_color_nearest_shade=}")
        return None
    main_nearest_basic_colors = [shade.base_color_name for shade in main_palette_nearest_shades]
    counter_of_main_basic_colors = Counter(main_nearest_basic_colors)
    most_common_basic_color_name, most_common_basic_color_name_count = counter_of_main_basic_colors.most_common(1)[0]

    second_dominant_shade_color_name = second_dominant_color_nearest_shade.base_color_name
    if second_dominant_shade_color_name != most_common_basic_color_name:
        print(
            f"--{second_dominant_shade_color_name} is not the most common basic color: {most_common_basic_color_name}")
        return None
    full_nearest_basic_colors = [shade.base_color_name for shade in full_palette_nearest_shades]
    counter_of_full_basic_colors = Counter(full_nearest_basic_colors)
    most_common_full_color_name, most_common_full_color_name_count = counter_of_full_basic_colors.most_common(1)[0]
    most_common_full_color_names = [name for name in counter_of_full_basic_colors.keys()
                                    if counter_of_full_basic_colors[name] == most_common_full_color_name_count]

    print(f"{full_palette_nearest_shades=}")
    print(f"{full_nearest_basic_colors=}")
    print(f"{main_nearest_basic_colors=}")
    print(f"{counter_of_main_basic_colors=}")
    print(f"{counter_of_full_basic_colors=}")
    print(f"{most_common_full_color_names=}")

    if most_common_basic_color_name_count < 2:
        print(f"--{second_dominant_shade_color_name} count is too low --")
        return None
    if second_dominant_shade_color_name != most_common_full_color_name:
        print(
            f"-- {second_dominant_shade_color_name} is not the most common full color name: {most_common_full_color_name} --")
        return None
    first_two_full_basic_colors = set(full_nearest_basic_colors[0:2])
    if len(most_common_full_color_names) > 1 and most_common_full_color_name_count < 4 and not (
            first_two_full_basic_colors == 1 and second_dominant_shade_color_name in first_two_full_basic_colors):
        print(
            f"--{second_dominant_shade_color_name} is not that dominant, there is a tie in full color names at {most_common_full_color_name_count}")
        return None
    if len(set(full_nearest_basic_colors)) > 6:
        print("-- too colorful! --")
        return None
    return second_dominant_color_nearest_shade


def get_salient_color_for_bw_image(
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
