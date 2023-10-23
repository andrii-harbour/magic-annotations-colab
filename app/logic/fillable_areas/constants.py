"""Package constants."""

from enum import Enum


class ColorRGB(Enum):
    """Colors in RGB scale."""

    BLACK = (0, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    WHITE = (255, 255, 255)


class ColorGray(Enum):
    """Colors in Gray scale."""

    BLACK = 0
    WHITE = 255
