from enum import Enum

class Color(Enum):
    white = (255,255,255)
    black = (0,0,0)
    red = (255,0,0)
    green = (0,255,0)
    blue = (0,0,255)
    purple = (102,0,204)
    pink = (204,0,204)
    turquoise = (0,255,255)


    def __str__(self):
        return f"Color: {self.name} | {self.value}"


