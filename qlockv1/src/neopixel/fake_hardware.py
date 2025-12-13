from typing import List

from rich.table import Table
from rich.console import Console

from pixel import Pixel

from collections.abc import Iterable

import random
from random import randint
import time

from rich.live import Live
from rich.table import Table


class ConsoleOutputHardwareInterface:
    ...

    def __init__(self, width:int=10, height:int=1, initial_pixels: Iterable[Pixel]=[]) -> None:
        """Params:
        - width: int: Width of led strip (number of led pixels)
        - height: int (Default = 1): Height of led matrix. For strip, use 1."""
        self.width = width
        self.height = height

        self.num_pixels = width * height

        self.current_pixels = initial_pixels

        empty_matrix = self.empty_matrix(width, height)

        rows = self.create_pixel_matrix(empty_matrix, initial_pixels,width, height)
        table = self.create_table(rows)
    
        c = Console()
        c.print(table)


    def styled_cell(self, text:str, r:int = 50,g:int = 100,b:int = 150):
        """Styles a given cell text by pre and postfixes."""
        return  f"[on rgb({r},{g},{b})]{text}[/]"


    def create_pixel_matrix(self,  matrix, data:Iterable[Pixel], width:int, height:int):
        ...
        # Sort pixels iterable based on pixel_index
        data_list = list(data)
        data_list = sorted(data_list, key=lambda item: item.pixel_index)

        while len(data_list) > 0:
            cur_pixel = data_list.pop(0)

            pixel_row = cur_pixel.pixel_index // width
            pixel_column =cur_pixel.pixel_index % width

            cell_text = self.styled_cell("X", *cur_pixel.color)

            matrix[pixel_row][pixel_column] = cell_text
        return matrix



    
    def empty_matrix(self, width:int, height:int) -> List[List[str]]:
        return [
            [""]*width for _ in range(height)
        ]
    
    def create_table(self, rows:list) -> Table:

        # table = Table.grid(expand=True)
        table = Table("My Table Header",show_header=False, padding=(0,0), show_edge=True, show_lines=False, show_footer=False)

        for _ in range(self.width - 1):
            table.add_column(justify="center", no_wrap=True, width=1)
        
        for index, row in enumerate(rows):
            
            # every uneven row is inverted
            if index % 2 == 1:
                # table.add_row(*row)
                table.add_row(*row[::-1])
            else:
                table.add_row(*row)
        return table


if __name__ == "__main__":

    WIDTH = 8
    HEIGHT = 4

    def rand_color():
        return (randint(0,255), randint(0,255), randint(0,255))
    
    def rand_index():
        return randint(0, WIDTH*HEIGHT -1)    


    pixels = [
        Pixel(0, rand_color()),
        Pixel(5, rand_color()),
        Pixel(9, rand_color()),
        Pixel(15, rand_color()),
        Pixel(20, rand_color()),
        Pixel(24, rand_color()),
        Pixel(30, rand_color()),
    ]

    ConsoleOutputHardwareInterface(width=WIDTH, height=HEIGHT, initial_pixels=pixels)