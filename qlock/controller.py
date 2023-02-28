import time
import logging

from .time_helpers import shift_hour, get_localized_date_segments
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

        self.clock()



    def clock(self):
        """Constant loop; check for updates every minute."""
        try:
            while True:
                month, day, hour, minute = get_localized_date_segments()
                if self.current_minute != minute:
                    self.current_minute = minute
                    self.update(month, day, hour, minute)

                time.sleep(0.5)

        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt Exception caught.")


        except Exception as e:
            logger.error(f"Caught unexpected exception: {e}")


    def update(self, month:int, day:int, hour:int, minute:int):
        """Gets called every new started minute to check, whether an update of pixels is needed."""
        logger.info(f"update called, day:{day} hour: {hour} minute: {minute}")
        self.check_birthday()

    def check_birthday(self):
        return True
    
 