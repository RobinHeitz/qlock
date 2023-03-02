import time
import logging
from typing import Tuple, List
from datetime import datetime

from .time_helpers import shift_hour, get_localized_date_segments, transform_hours_to_clock_format, get_clock_mode
from .constants import QlockMode
from .pixel import Pixel

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







class QlockController:
    
    old_pixels = set()
    new_pixels = set()
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
        new_pixels = self.determine_on_pixels(local_time, state)
        changes = self.compute_pixel_changes(new_pixels)
        

    def specify_clock_mode(self, time:datetime) -> QlockMode:
        """Returns a QlocMode, depending on configured times and day-of-the-week."""
        early_day_config = self.config.get("early_day_times")
        late_day_config = self.config.get("late_day_config")
        return get_clock_mode(early_day_config, late_day_config, time)


    def check_birthday(self, month, day):
        month_ = self.config.get("birthday").get("month")
        day_ = self.config.get("birthday").get("day")
        self.is_birthday = month == month_ and day == day_
        return self.is_birthday
    
    
    def determine_on_pixels(self, time:datetime, state:QlockMode)->set:
        """Based on the states (show birthday/ good morning/ good night) we define which pixels should be active.
        Returns a set of pixels that should be active given the time and qlock_mode."""
        mode_map = {
            QlockMode.mode_morning: self.pixels_qlock_mode_good_morning,
            QlockMode.mode_night: self.pixels_qlock_mode_night,
            QlockMode.mode_normal: self.pixels_qlock_mode_normal,
        }

        pixels_func = mode_map.get(state)
        pixels = pixels_func(time)

        if self.is_birthday == True:
            ...
            pixels.append()

    
    def pixels_qlock_mode_normal(self, time:datetime)->List[Pixel]:
        ...
    
    def pixels_qlock_mode_morning(self, time:datetime)->List[Pixel]:
        ...
    
    def pixels_qlock_mode_night(self, time:datetime)->List[Pixel]:
        ...
    def pixels_qlock_mode_good_morning(self, time:datetime)->List[Pixel]:
        ...
    
    def compute_pixel_changes(self, new_pixels):
        """Based on current state of active pixels and the changes, computes which pixels should be turned on and off."""




    # def _clock_state_normal(self, minutes, hour):
    #     # minute pixels at the edge of the board
    #     minute_edge_pixels = MIN_POINTS_DEF.get(minutes % 5)
    #     logger.info(f"min_pixels = {minute_edge_pixels}")
    #     self.add_new_pixels(minute_edge_pixels)
        
    #     # show the word "it is"
    #     logger.info(f"add word-def 'it is': {WD_IT_IS}")
    #     self.add_new_pixels(WD_IT_IS)

    #     #words corresponding to muntes, like 15 min before, half etc.
    #     minutes_words = clock_words(minutes)
    #     logger.info(f"minute words: {minutes_words}")
    #     self.add_new_pixels(minutes_words)

    #     #hour as word like 1, 2, 3 etc.
    #     current_hour_word = hour_wording_rep(minutes, hour)
    #     self.add_new_pixels(current_hour_word)

    # def _clock_state_show_good_morning(self):
    #     if self._is_birthday:
    #         good_morning_pixels = WD_GOOD_MORNING
    #     else:
    #         good_morning_pixels  = WD_GOOD_MORNING +  WD_CHARLY
    #     self.add_new_pixels(good_morning_pixels, color=(140,240,10))

    
    # def _clock_state_show_good_night(self):
    #     if self._is_birthday:
    #         good_night_pixels = WD_GOOD_NIGHT
    #     else:
    #         good_night_pixels = WD_GOOD_NIGHT + WD_CHARLY
    #     self.add_new_pixels(good_night_pixels, color=(50,150,250))
        


