from rich.table import Table
from rich.console import Console

from pixel import Pixel

from collections.abc import Iterable

import random
from random import randint
import time

from rich.live import Live
from rich.table import Table


def generate_table() -> Table:
    """Make a new table."""
    table = Table()
    table.add_column("ID")
    table.add_column("Value")
    table.add_column("Status")

    for row in range(random.randint(2, 6)):
        value = random.random() * 100
        table.add_row(
            f"{row}", f"{value:3.2f}", "[red]ERROR" if value < 50 else "[green]SUCCESS"
        )
    return table


with Live(generate_table(), refresh_per_second=4) as live:
    for _ in range(40):
        time.sleep(0.4)
        live.update(generate_table())




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

    
        table = self.__generate_table(self.current_pixels)     
        c = Console()
        c.print(table)   

    
    
    def __generate_table(self, data:Iterable[Pixel]) -> Table:
        ...

        table = Table("My Table Header")

        data_list = list(data)
        data_list = sorted(data_list, key=lambda item: item.pixel)

        for item in data_list:
            print(item)





        for _ in range(self.width):
            self.table.add_column(justify="center", style="cyan", no_wrap=True)

    

    def update(self, pixels: Iterable[Pixel]):
        ...





        
        table = Table(title="Console Output Hardware", show_header=False)

        table.add_column(justify="center", style="cyan",no_wrap=True)
        table.add_column(justify="center", style="cyan",no_wrap=True)
        table.add_column(justify="center", style="cyan",no_wrap=True)
        
        table.add_row(*["x"]*3)

        console = Console()
        console.print(table)


if __name__ == "__main__":

    WIDTH = 16
    HEIGHT = 16

    def rand_color():
        return (randint(0,255), randint(0,255), randint(0,255))
    
    def rand_index():
        return randint(0, WIDTH*HEIGHT -1)    


    pixels = [Pixel(rand_index(),rand_color()) for _ in range(30)]


    ConsoleOutputHardwareInterface(WIDTH, HEIGHT, pixels)