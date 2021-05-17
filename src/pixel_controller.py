import time
from rpi_ws281x import *
import argparse



LED_COUNT      = 16**2      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 100     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53





class PixelController(object):
    def __init__(self):
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.strip.begin()
        self.color_std = Color(150,150,150)


    def testaction(self):
        self.strip.setPixelColor(80, self.color_std)
        self.strip.show()

    def activatePixels(self, pixels):
        for p in pixels:
            self.strip.setPixelColor(p, self.color_std)
        self.strip.show()


# if __name__ == '__main__':
#     pc = PixelController()
#     pc.testaction()
#     print("testaction done")