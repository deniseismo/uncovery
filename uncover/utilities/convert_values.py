import math
from datetime import datetime
from typing import NamedTuple


class TimeSpan(NamedTuple):
    start_date: datetime
    end_date: datetime


class CollageDimensions(NamedTuple):
    width: int
    height: int


def convert_a_list_of_dates_to_time_span(time_span: list) -> TimeSpan:
    """
    convert [start_year, end_year] to datetime objects
    :param time_span: a list of start and end years picked by the user
    :return: a TimeSpan instance (start_date, end_date)
    """
    start_year, end_year = time_span
    end_year += 1
    return TimeSpan(start_date=datetime.strptime(str(start_year), '%Y'),
                    end_date=datetime.strptime(str(end_year), '%Y'))


def _get_multipliers(number: int) -> tuple[int, int]:
    """
    get two multipliers of a number (closest to the square root of a number)
    :param number: integer number
    :return: tuple(int, int)
    """
    first = math.floor(number ** 0.5)
    second = int(number / first)
    return first, second


def get_collage_dimensions(number_of_images: int) -> CollageDimensions:
    """
    calculate appropriate collage dimensions (width, height) in pixels
    :param number_of_images: total number of images to get appropriate collage dimensions from
    :return: namedtuple CollageDimensions(width, height)
    """
    DEFAULT_IMAGE_SIZE = 600
    DIMENSIONS = {
        1: CollageDimensions(600, 600),
        2: CollageDimensions(1200, 600),
        3: CollageDimensions(1800, 600),
        4: CollageDimensions(1200, 900),
        5: CollageDimensions(1800, 1500),
        6: CollageDimensions(1800, 1200),
        7: CollageDimensions(1500, 900),
        8: CollageDimensions(1800, 2100),
        9: CollageDimensions(1800, 1800),
    }
    try:
        return DIMENSIONS[number_of_images]
    except KeyError as e:
        print(f"{number_of_images} is not a default number of images, proceeding to further calculations")
    multipliers = _get_multipliers(number_of_images)
    dimensions = sorted(map(lambda x: DEFAULT_IMAGE_SIZE * x, multipliers), reverse=True)
    return CollageDimensions(*dimensions)
