from strenum import StrEnum
from enum import Enum

# LED STRIP CONFIGURATION
LED_COUNT      = 16**2      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 50     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

CONFIG_FILE_NAME = "qlock.yaml"



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


class QlockMode(StrEnum):
    mode_normal = "mode_normal"
    mode_birthday = "mode_birthday"
    mode_morning = "mode_morning"
    mode_night = "mode_night"
    