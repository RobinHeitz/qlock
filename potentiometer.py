import time
import Adafruit_ADS1x15

######################################################
# ADS1115 chip, each value will be 16 bit int solution
######################################################


adc = Adafruit_ADS1x15.ADS1115()

GAIN = 1
# GAIN = 2



def get_poti_brightness(current_value):
    ...
    min_value = 3
    max_value = 32558

    val_percent = (current_value - min_value) / (max_value - min_value)

    return int(round(255 * val_percent, 0))



while True:
    # Read all the ADC channel values in a list.
    value = 0
    for i in range(4):
        # Read the specified ADC channel using the previously set gain value.
        value = adc.read_adc(0, gain=GAIN, data_rate = 128)
        # values[4] = poti_brightness(values[0])
        # Note you can also pass in an optional data_rate parameter that controls
        # the ADC conversion time (in samples/second). Each chip has a different
        # set of allowed data rate values, see datasheet Table 9 config register
        # DR bit values.
        #values[i] = adc.read_adc(i, gain=GAIN, data_rate=128)
        # Each value will be a 12 or 16 bit signed integer value depending on the
        # ADC (ADS1015 = 12-bit, ADS1115 = 16-bit).
    # Print the ADC values.
    # print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} | {4:>6} '.format(*values))
    print("Value = ", value, "brightness factor = ", get_poti_brightness(value))
    # Pause for half a second.
    time.sleep(0.2)