#!/usr/bin/env python3
# rpi_ws281x library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

import time
from rpi_ws281x import *
import argparse
import random

from pixel_definition import WD_ALL

# LED strip configuration:
LED_COUNT      = 16**2      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 100     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53




def activatePixel(strip, index, color):
    strip.setPixelColor(index, color)
    strip.show()

def deactivatePixel(strip, index):
    strip.setPixelColor(index, Color(0,0,0))
    strip.show()



def activatePixels(strip, pixel_numbers, sleep_sec=2):
    color = randomColor()
    for i in pixel_numbers:
        activatePixel(strip, i, color)
    time.sleep(sleep_sec)

    #clear
    for i in pixel_numbers:
        deactivatePixel(strip, i)


def deactivePixel(strip, pixel_number):
    strip.setPixelColor(pixel_number, Color(0,0,0))
    strip.show()

def randomColor():
    # return tuple(random.randint(0,255) for _ in range(3))
    r,g,b = tuple(random.randint(0,255) for _ in range(3))
    return Color(r,g,b)

    


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()


    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print("Random color:")
    print(randomColor())

    try:

        for word in WD_ALL:
            activatePixels(strip, word)

    except KeyboardInterrupt:

        for i in range(LED_COUNT):
            deactivePixel(strip, i)
            

    
    # if not args.clear:
    #     print('Use "-c" argument to clear LEDs on exit')
    # else:
    #     strip.setPixelColor(PIXEL_NO, Color(0,0,0))
    #     strip.show()




