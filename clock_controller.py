from datetime import datetime
from tkinter import E
import pytz
import time

from pixel_definition import (MIN_POINTS_DEF, WD_GOOD_MORNING, WD_GOOD_NIGHT, WD_HAPPY_BD, WD_IT_IS, WD_CHARLY)
from helper_funcs import translate_to_12h_clock_format, clock_words,hour_wording_rep,determineClockState

from load_config import load_config_from_file


# LOGGING CONFIGURATION
import logging
logFormatter = logging.Formatter("'%(asctime)s - %(message)s'")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler("clock_controller.log", mode="w")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)



# LED STRIP CONFIGURATION
LED_COUNT      = 16**2      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 50     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


CLOCK_STATE_NORMAL = "CLOCK_STATE_NORMAL"
CLOCK_STATE_SHOW_GOOD_MORNING = "CLOCK_STATE_SHOW_GOOD_MORNING"
CLOCK_STATE_SHOW_GOOD_NIGHT = "CLOCK_STATE_SHOW_GOOD_NIGHT"

STD_COL = (255,255,255)

# BIRTH_DATE = (6,14) # (month, day)
# BIRTH_DATE = (7,5) # (month, day)


import io
def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False




class Pixel:
 
    def __init__(self, pixel, color=STD_COL) -> None:
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



class ClockController:

    old_pixels = set()
    new_pixels = set()

    old_minute = None


    def __init__(self):


        if is_raspberrypi():
            from rpi_ws281x import Adafruit_NeoPixel
            self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
            self.strip.begin()

        # self.old_pixels = set()
        # self.new_pixels = set()

        self._load_config()
        
        logger.debug("ClockController init() done. Start clocking now.")
        # self.old_minute = None
        self.clock()

    def _load_config(self):
        loaded_config = load_config_from_file()
        self.cfg_birthday = loaded_config[0]

        self.cfg_times = dict(
            early_morning_start = loaded_config[1], 
            early_morning_end = loaded_config[2], 
            early_night_start = loaded_config[3], 
            early_night_end = loaded_config[4], 
            late_morning_start = loaded_config[5], 
            late_morning_end = loaded_config[6], 
            late_night_start = loaded_config[7], 
            late_night_end = loaded_config[8],

        )

    def add_new_pixels(self, pixels, color=STD_COL):
        logger.debug(f"add_new_pixels(); No. pixels = {len(pixels)}")
        for p in pixels:
            self.new_pixels.add(
                Pixel(p, color)
            )
    def add_new_pixel(self, pixel, color=STD_COL):
        logger.debug("add_new_pixel()")
        self.new_pixels.add(
            Pixel(pixel, color)
        )


   
    def _get_time_items(self):
        utc = pytz.timezone('UTC')
        now = utc.localize(datetime.utcnow())

        local_tz = pytz.timezone('Europe/Berlin')
        local_time = now.astimezone(local_tz)

        y = local_time.year
        m = local_time.month
        d = local_time.day

        hour = translate_to_12h_clock_format(local_time.hour)
        min_ = local_time.minute
        return local_time, y, m, d, hour, min_



    def get_pixel_difference(self):
        pixels_to_switch_on = self.new_pixels - self.old_pixels
        pixels_to_switch_off = self.old_pixels - self.new_pixels
        
        # switch values for next round
        self.old_pixels = self.new_pixels
        self.new_pixels = set()

        logger.warning(f"pixels to switch ON:")
        logger.warning(pixels_to_switch_on)

        logger.info(f"pixels to switch off:")
        logger.info(pixels_to_switch_off)

        return pixels_to_switch_on, pixels_to_switch_off


    def _execute_pixel_changes(self):
        if not is_raspberrypi():
            return

        pixels_to_switch_on, pixels_to_switch_off = self.get_pixel_difference()

        for p in pixels_to_switch_on:
            self.strip.setPixelColorRGB(p.pixel,*p.color)


        for p in pixels_to_switch_off:
            self.strip.setPixelColorRGB(p.pixel,0,0,0)

        self.strip.show()

    
    def deactivate_all_pixels(self):
        if not is_raspberrypi():
            return
        all_pixels = self.new_pixels | self.old_pixels
        for p in all_pixels:
            self.strip.setPixelColorRGB(p.pixel,0,0,0)
        self.strip.show()

    
    def _clock_state_normal(self, minutes, hour):
        # minute pixels at the edge of the board
        minute_edge_pixels = MIN_POINTS_DEF.get(minutes % 5)
        logger.info(f"min_pixels = {minute_edge_pixels}")
        self.add_new_pixels(minute_edge_pixels)
        
        # show the word "it is"
        logger.info(f"add word-def 'it is': {WD_IT_IS}")
        self.add_new_pixels(WD_IT_IS)

        #words corresponding to muntes, like 15 min before, half etc.
        minutes_words = clock_words(minutes)
        logger.info(f"minute words: {minutes_words}")
        self.add_new_pixels(minutes_words)

        #hour as word like 1, 2, 3 etc.
        current_hour_word = hour_wording_rep(minutes, hour)
        self.add_new_pixels(current_hour_word)

    def _clock_state_show_good_morning(self):
        if self._is_birthday:
            good_morning_pixels = WD_GOOD_MORNING
        else:
            good_morning_pixels  = WD_GOOD_MORNING +  WD_CHARLY
        self.add_new_pixels(good_morning_pixels, color=(140,240,10))

    
    def _clock_state_show_good_night(self):
        if self._is_birthday:
            good_night_pixels = WD_GOOD_NIGHT
        else:
            good_night_pixels = WD_GOOD_NIGHT + WD_CHARLY
        self.add_new_pixels(good_night_pixels, color=(50,150,250))


    def _activate_birthday_pixels(self, m,d):
        if self._is_birthday:
            self.add_new_pixels(WD_HAPPY_BD + WD_CHARLY, color=(28,217,230))
    
    def _check_birthday(self, m, d):
        month = self.cfg_birthday.get('month')
        day = self.cfg_birthday.get('day')
        return m == month and d == day
        
    
    def clock(self):
        try:
            while True:
                minute = datetime.now().minute
                if self.old_minute != minute:
                    self.old_minute = minute
                    self.update_clock()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt")
            self.deactivate_all_pixels()
        
        except Exception as e:
            logger.error(f"Exception was thrown: {e}")
            self.deactivate_all_pixels()



    def update_clock(self):
        logger.info("Clock()")
        
        local_time, y, m, d, hour, min = self._get_time_items()
        self._is_birthday = self._check_birthday(m,d)


        # params = (self.cfg_early_morning_start, self.cfg_early_morning_end, self.cfg_early_night_start, self.cfgeraly)

        current_clock_state = determineClockState(local_time, **self.cfg_times)

        self._activate_birthday_pixels(m,d)
        
        if current_clock_state == CLOCK_STATE_NORMAL:
            self._clock_state_normal(min,hour)

        elif current_clock_state == CLOCK_STATE_SHOW_GOOD_MORNING:
            self._clock_state_show_good_morning()
        else:
            self._clock_state_show_good_night()

        
        self._execute_pixel_changes()

                
    
        
if __name__ == "__main__":
    controller = ClockController()

