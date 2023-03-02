import time
import logging
from typing import Tuple
from datetime import datetime

from .time_helpers import shift_hour, get_localized_date_segments, transform_hours_to_clock_format, get_clock_mode
from hw_interface.hw_protocol import QlockHardwareInterface
from .constants import QlockMode

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
        states = self.specify_clock_mode(local_time, self.is_birthday)
        

    def specify_clock_mode(self, local_time:datetime, is_bd:bool) -> Tuple[QlockMode]:
        """Returns a tuple of QlocMode's, depending on configured times, day-of-the-week and whether it's her birthday."""
        early_day_config = self.config.get("early_day_times")
        late_day_config = self.config.get("late_day_config")

        mode = get_clock_mode(early_day_config, late_day_config, local_time)
        if is_bd:
            return (mode, QlockMode.mode_birthday)
        return (mode,)
        
        

    def check_birthday(self, month, day):
        month_ = self.config.get("birthday").get("month")
        day_ = self.config.get("birthday").get("day")
        self.is_birthday = month == month_ and day == day_
        return self.is_birthday