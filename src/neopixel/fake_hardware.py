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

    
        table = self.__generate_table(self.current_pixels, self.width, self.height)     
        c = Console()
        c.print(table)   

    
    
    def __generate_table(self, data:Iterable[Pixel], width:int, height:int) -> Table:
        ...

        def init_new_row():
            return ["o"]*width
        
        def is_inv(row:int) -> bool:
            return row % 2 == 1
        
        def add_to_table(row: list):
            print("row was added to table: ", *row)
            table.add_row(*row)


        table = Table("My Table Header",show_header=False)

        for _ in range(self.width - 1):
            table.add_column(justify="center", no_wrap=True)


        data_list = list(data)
        data_list = sorted(data_list, key=lambda item: item.pixel_index)

        cur_row_index = 0
        cur_column_index = 0

        # cur_row = ...

        cur_row = init_new_row()

        while len(data_list) > 0:
            cur_pixel = data_list.pop(0)
            print(f"--- pop item|| row: {cur_row_index}, col: {cur_column_index} Actual INDEX: {cur_pixel.pixel_index}")

            pixel_row = cur_pixel.pixel_index // width
            pixel_column =cur_pixel.pixel_index % width

            print(f"+ pixel_row: {pixel_row} pixel_column: {pixel_column}")
            
            if pixel_row != cur_row_index:
                for row_ in range(cur_row_index, pixel_row):
                    
                    if is_inv(row_):
                        cur_row = cur_row[::-1]
                    add_to_table(cur_row)
                    cur_row = init_new_row()
            
            cur_row[pixel_column] = "X"



            # update 
            cur_row_index = pixel_row
            cur_column_index = pixel_column
        return table



if __name__ == "__main__":

    WIDTH = 8
    HEIGHT = 4

    def rand_color():
        return (randint(0,255), randint(0,255), randint(0,255))
    
    def rand_index():
        return randint(0, WIDTH*HEIGHT -1)    


    # pixels = {Pixel(rand_index(),rand_color()) for _ in range(30)}

    pixels = [
        Pixel(0, rand_color()),
        Pixel(5, rand_color()),
        Pixel(8, rand_color()),
        Pixel(15, rand_color()),
        Pixel(20, rand_color()),
        Pixel(24, rand_color()),
    ]

    ConsoleOutputHardwareInterface(width=WIDTH, height=HEIGHT, initial_pixels=pixels)