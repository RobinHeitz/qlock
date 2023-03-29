from .constants import Color
from typing import Tuple


class Pixel:
    """
    Representation of one pixel of the led grid/ matrix.

    Implements __eq__ and __hash__, therefore state changes can easily be calculated by set operations.
    """

 
    def __init__(self, pixel:int, color:Tuple[int, int, int]=Color.white.value) -> None:
        self.pixel = pixel
        self.color = color

    def __str__(self) -> str:
        return f"P: {self.pixel}"

    def __repr__(self) -> str:
        return f"P: {self.pixel}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Pixel) and other.pixel == self.pixel and other.color == self.color:
            return True
        return False

    def __hash__(self) -> int:
        return hash(self.pixel)


# def create_pxls(pixels, color: Tuple[int, int, int] = STANDARD_COLOR) -> set:
#     """Method for creating many Pixel objects.
    
#     Params:
#     - pixels (iterable): int's for the pixel index.
#     - color (tuple of ints): Color of the pixel, defined as values [0; 255]. Default is (255,255,255).
    
#     Returns a set of Pixel-objects."""
#     p = set()
#     for item in pixels:
#         p.add(
#             Pixel(item, color)
#         )
#     return p