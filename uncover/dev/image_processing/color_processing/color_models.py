from enum import Enum
from typing import NamedTuple, Union


class RGBColor(NamedTuple):
    red: int
    green: int
    blue: int


class ColorInfo(Enum):
    @property
    def color_values(self) -> RGBColor:
        if isinstance(self, BasicColor):
            return self.value
        elif isinstance(self, ShadeColor):
            return self.value.rgb
        else:
            return NotImplemented

    @property
    def base_color_name(self) -> str:
        if isinstance(self, BasicColor):
            return self.name
        elif isinstance(self, ShadeColor):
            return self.value.base.name
        else:
            return NotImplemented

    def __eq__(self, other):
        if issubclass(type(other), ColorInfo):
            return other.color_values == self.color_values
        elif isinstance(other, tuple):
            return other == self.color_values
        else:
            return NotImplemented

    def __hash__(self):
        return hash(self.color_values)


class BasicColor(ColorInfo):
    WHITE = RGBColor(255, 255, 255)
    BLACK = RGBColor(0, 0, 0)
    RED = RGBColor(255, 0, 0)
    BLUE = RGBColor(0, 0, 255)
    GREEN = RGBColor(0, 128, 0)
    YELLOW = RGBColor(255, 255, 0)
    PURPLE = RGBColor(128, 0, 128)
    BROWN = RGBColor(139, 69, 19)
    GRAY = RGBColor(128, 128, 128)
    ORANGE = RGBColor(255, 140, 0)
    MAGENTA = RGBColor(255, 0, 255)


class ComplexColor(NamedTuple):
    rgb: RGBColor
    base: BasicColor


class ShadeColor(ColorInfo):
    GRAY = ComplexColor(rgb=RGBColor(128, 128, 128), base=BasicColor.GRAY)

    RED = ComplexColor(rgb=RGBColor(255, 0, 0), base=BasicColor.RED)
    VERMILION = ComplexColor(rgb=RGBColor(227, 66, 52), base=BasicColor.RED)
    BLOOD = ComplexColor(rgb=RGBColor(102, 0, 0), base=BasicColor.RED)
    TOMATO = ComplexColor(rgb=RGBColor(255, 99, 71), base=BasicColor.RED)
    MAROON = ComplexColor(rgb=RGBColor(128, 0, 0), base=BasicColor.RED)
    CARMINE = ComplexColor(rgb=RGBColor(150, 0, 24), base=BasicColor.RED)

    GREEN = ComplexColor(rgb=RGBColor(0, 128, 0), base=BasicColor.GREEN)
    CHARTREUSE = ComplexColor(rgb=RGBColor(127, 255, 0), base=BasicColor.GREEN)
    LIME = ComplexColor(rgb=RGBColor(0, 255, 0), base=BasicColor.GREEN)
    DARKGREEN = ComplexColor(rgb=RGBColor(0, 100, 0), base=BasicColor.GREEN)
    VIRIDIAN = ComplexColor(rgb=RGBColor(64, 130, 109), base=BasicColor.GREEN)

    BLUE = ComplexColor(rgb=RGBColor(0, 0, 255), base=BasicColor.BLUE)
    CYAN = ComplexColor(rgb=RGBColor(0, 0, 255), base=BasicColor.BLUE)
    NAVYBLUE = ComplexColor(rgb=RGBColor(0, 0, 128), base=BasicColor.BLUE)
    CAPRI = ComplexColor(rgb=RGBColor(0, 191, 255), base=BasicColor.BLUE)
    CERULEAN = ComplexColor(rgb=RGBColor(0, 123, 167), base=BasicColor.BLUE)

    BROWN = ComplexColor(rgb=RGBColor(139, 69, 19), base=BasicColor.BROWN)
    CHOCOLATE = ComplexColor(rgb=RGBColor(123, 63, 0), base=BasicColor.BROWN)
    SIENNA = ComplexColor(rgb=RGBColor(136, 45, 23), base=BasicColor.BROWN)
    MAHOGANY = ComplexColor(rgb=RGBColor(192, 64, 0), base=BasicColor.BROWN)
    SEPIA = ComplexColor(rgb=RGBColor(112, 66, 20), base=BasicColor.BROWN)

    MAGENTA = ComplexColor(rgb=RGBColor(255, 0, 255), base=BasicColor.MAGENTA)
    PINK = ComplexColor(rgb=RGBColor(255, 192, 203), base=BasicColor.MAGENTA)
    ROSE = ComplexColor(rgb=RGBColor(255, 0, 127), base=BasicColor.MAGENTA)

    ORANGE = ComplexColor(rgb=RGBColor(255, 140, 0), base=BasicColor.ORANGE)
    CORAL = ComplexColor(rgb=RGBColor(255, 127, 80), base=BasicColor.ORANGE)
    FLAME = ComplexColor(rgb=RGBColor(226, 88, 34), base=BasicColor.ORANGE)

    PURPLE = ComplexColor(rgb=RGBColor(128, 0, 128), base=BasicColor.PURPLE)
    VIOLET = ComplexColor(rgb=RGBColor(127, 0, 255), base=BasicColor.PURPLE)
    HELIOTROPE = ComplexColor(rgb=RGBColor(223, 115, 255), base=BasicColor.PURPLE)

    YELLOW = ComplexColor(rgb=RGBColor(255, 255, 0), base=BasicColor.YELLOW)
    AMBER = ComplexColor(rgb=RGBColor(255, 191, 0), base=BasicColor.YELLOW)
    LEMON = ComplexColor(rgb=RGBColor(227, 255, 0), base=BasicColor.YELLOW)
    PEACH = ComplexColor(rgb=RGBColor(255, 229, 180), base=BasicColor.YELLOW)

    # backup complex colors; no need for them right now;
    # white/black/gray colors are calculated differently for more consistency
    # WHITE = ComplexColor(rgb=RGBColor(255, 255, 255), base=BasicColor.WHITE)
    # BLACK = ComplexColor(rgb=RGBColor(0, 0, 0), base=BasicColor.BLACK)
    # JET = ComplexColor(rgb=RGBColor(52, 52, 52), base=BasicColor.BLACK)
    # NERO = ComplexColor(rgb=RGBColor(33, 33, 33), base=BasicColor.BLACK)
    # LIGHTGRAY = ComplexColor(rgb=RGBColor(211, 211, 211), base=BasicColor.GRAY)
    # SILVER = ComplexColor(rgb=RGBColor(192, 192, 192), base=BasicColor.GRAY)
    # PLATINUM = ComplexColor(rgb=RGBColor(229, 228, 226), base=BasicColor.GRAY)
    # LIGHTBLUE = ComplexColor(rgb=RGBColor(173, 216, 230), base=BasicColor.BLUE)
    # TEAL = ComplexColor(rgb=RGBColor(0, 12, 128), base=BasicColor.BLUE) # blue/green — ?
    # LIGHTGREEN = ComplexColor(rgb=RGBColor(152, 251, 152), base=BasicColor.GREEN)


class ImageColor(NamedTuple):
    color: Union[BasicColor, ShadeColor]
    is_black_and_white: bool
