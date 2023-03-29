import time
import logging
from typing import Tuple, List
from datetime import datetime
from collections.abc import Iterable

from .time_helpers import shift_hour, get_localized_date_segments, transform_hours_to_clock_format, get_clock_mode, get_minute_word, get_hour_word
from .constants import QlockMode, Color
from .pixel import Pixel
from .pixel_definition import WD_IT_IS, WD_GOOD, WD_GOOD_MORNING, WD_GOOD_NIGHT, WD_HAPPY, WD_HAPPY_BD, WD_CHARLY, minute_pixels

from hw_interface.hw_protocol import QlockHardwareInterface

# Setup logger
logFormatter = logging.Formatter("'%(asctime)s - %(message)s'")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

fileHandler = logging.FileHandler("qlock.log", mode="w")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)


def create_pixels(pixels: Iterable, color=Color.white.value):
    """Given an iterator it returns a set of Pixel objects with given color.
    Params: 
    - pixels (int): Number of pixel
    - color (tuple): 3-tuple with ints ranging from [0,255] (RGB Colors)
    """
    return [Pixel(p, color) for p in pixels]




class QlockController:
    
    current_pixels = set()
    current_minute = None
    is_birthday = False

    def __init__(self, config:dict, hw:QlockHardwareInterface):
        logger.debug("Initialize QlockController.")
        self.config = config
        self.hw = hw


    def clock(self):
        """Constant loop; check for updates every minute."""
        try:
            while True:
                local_time, month, day, hour, minute = get_localized_date_segments()
                if self.current_minute != minute:
                    self.current_minute = minute
                    
                    hour = shift_hour(hour, minute)
                    hour = transform_hours_to_clock_format(hour)
                    
                    self.update(local_time, month, day, hour, minute)
                time.sleep(0.5)

        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt Exception caught.")

        except Exception as e:
            logger.error(f"Caught unexpected exception: {e}")


    def update(self, local_time, month:int, day:int, hour:int, minute:int):
        """Gets called every new started minute to check, whether an update of pixels is needed."""
        logger.info(f"update called, day:{day} hour: {hour} minute: {minute}")
        self.check_birthday(month, day)
        state = self.specify_clock_mode(local_time)
        new_pixels = self.determine_active_pixels(state, hour, minute)
        turn_on, turn_off = self.compute_pixel_changes(new_pixels)
        print(f"+++ Turn On/ Off: {len(turn_on)} ons vs. {len(turn_off)} offs.")

        # TODO: Perform changes of pixels
        

    def specify_clock_mode(self, time:datetime) -> QlockMode:
        """Returns a QlocMode, depending on configured times and day-of-the-week."""
        early_day_config = self.config.get("early_day_times")
        late_day_config = self.config.get("late_day_config")
        return get_clock_mode(early_day_config, late_day_config, time)


    def check_birthday(self, month, day) -> bool:
        month_ = self.config.get("birthday").get("month")
        day_ = self.config.get("birthday").get("day")
        self.is_birthday = month == month_ and day == day_
        return self.is_birthday
    
    
    def determine_active_pixels(self, state:QlockMode, hour:int, minutes:int)->set[Pixel]:
        """Based on the states (show birthday/ good morning/ good night) we define which pixels should be active.
        Returns a set of pixels that should be active given the time and qlock_mode."""
        logger.info(f"determine_active_pixels: QlockMode = {state}")
        pixels = set()
        
        mode_map = {
            QlockMode.mode_morning: self.pixels_qlock_mode_good_morning,
            QlockMode.mode_night: self.pixels_qlock_mode_good_night,
            QlockMode.mode_normal: self.pixels_qlock_mode_normal,
        }
        
        pixels_func = mode_map.get(state)
        pixels = pixels.update(pixels_func(hour, minutes))

        return pixels

    
    def pixels_qlock_mode_normal(self, hour:int, minutes:int)->set[Pixel]:
        pixels = set()

        mins = minute_pixels(minutes)
        pixels.update(mins)
        
        pixels.update(WD_IT_IS)
        
        minute_words = get_minute_word(minutes)
        pixels.update(minute_words)

        hour_word = get_hour_word(hour, minutes)
        pixels.update(hour_word)

        return create_pixels(pixels, Color.white.value)
    


    
    def pixels_qlock_mode_good_night(self,  hour:int, minutes:int)->set[Pixel]:
        if self.is_birthday == True:
            pixels = set()
            pixels.update(create_pixels(WD_HAPPY_BD + WD_CHARLY, Color.red.value))
            pixels.update(create_pixels(WD_GOOD_NIGHT,Color.blue.value))
            return pixels
        return create_pixels(WD_GOOD_NIGHT + WD_CHARLY, Color.blue.value)
    


    def pixels_qlock_mode_good_morning(self,  hour:int, minutes:int)->set[Pixel]:
        if self.is_birthday == True:
            pixels = set()
            pixels.update(create_pixels(WD_HAPPY_BD + WD_CHARLY, Color.red.value))
            pixels.update(create_pixels(WD_GOOD_MORNING,Color.turquoise.value))
            return pixels
        return create_pixels(WD_GOOD_MORNING + WD_CHARLY, Color.turquoise.value)
    

    def compute_pixel_changes(self, new_pixels):
        """Based on current state of active pixels and the changes, computes which pixels should be turned on and off.
        By using sets for pixel representations, we have no doublings and also can easily compute differences, e.g. which pixel to turn on/ off.
        
        Returns a tuple of pixels_to_turn_on, pixels_to_turn_off
        """
        logger.info(f"compute_pixel_changes")
        pixels_to_turn_on = new_pixels - self.current_pixels
        pixels_to_turn_off = self.current_pixels - new_pixels

        self.current_pixels = new_pixels
        return pixels_to_turn_on, pixels_to_turn_off
