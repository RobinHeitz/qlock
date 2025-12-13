from typing import Tuple

class Pixel:
    """
    Representation of one pixel of the led grid/ matrix.

    Implements __eq__ and __hash__, therefore state changes can easily be calculated by set operations.
    """

 
    def __init__(self, pixel_index:int, color:Tuple[int, int, int]=(255,255,255)) -> None:
        self.pixel_index = pixel_index
        self.color = color

    def __str__(self) -> str:
        return f"P: {self.pixel_index}"

    def __repr__(self) -> str:
        return f"Pixel with index: {self.pixel_index} | color: {self.color}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Pixel) and other.pixel_index == self.pixel_index and other.color == self.color:
            return True
        return False

    def __hash__(self) -> int:
        return hash(self.pixel_index)