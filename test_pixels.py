from rpi_ws281x import *
import time
# LED_COUNT      = 16**2      # Number of LED pixels.
LED_COUNT      = 50      # Number of LED pixels.
LED_PIN        = 12      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 50     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


# def colorWipe(strip, color, wait_ms=50):
#     """Wipe color across display a pixel at a time."""
#     for i in range(strip.numPixels()):
#         time.sleep(wait_ms/1000.0)


if __name__ == "__main__":
    
 
    
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    for i in range(16**2):
        strip.setPixelColor(i, Color(255,255,255))
        strip.show()

        time.sleep(.3)


    # try:

    #     while True:
    #         print("color wipe")
    #         colorWipe(strip, Color(255,255,255))

    # except KeyboardInterrupt:
    #     print("KEYBOARD INTERUPT")

    #     for i in range(strip.numPixels()):
    #         strip.setPixelColorRGB(i,0,0,0)
    #     strip.show()




