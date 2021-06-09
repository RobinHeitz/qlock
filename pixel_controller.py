import time
from rpi_ws281x import *
import argparse



LED_COUNT      = 16**2      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 50     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53





class PixelController(object):
    def __init__(self, brightness=LED_BRIGHTNESS, std_color=(255,255,255)):
        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        self.strip.begin()
        self.color = (255,255,255)

    def activatePixelRGB(self, pixel, *color):
        self.strip.setPixelColorRGB(pixel, *color)

    
    def activatePixels(self, pixels):
        self.activatePixelsRGB(pixels, *self.color)

    def activatePixelsRGB(self, pixels, *args):
        for p in pixels:
            self.activatePixelRGB(p, *args)
        
        self.strip.show()


    def deactivatePixels(self, pixels):
        for p in pixels:
            self.strip.setPixelColorRGB(p,0,0,0)
        self.strip.show()
    
    def showPixels(self):
        self.strip.show()