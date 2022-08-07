import time
from threading import Thread, Lock

from random import randint

from helper_funcs import is_raspberrypi

######################################################
# ADS1115 chip, each value will be 16 bit int solution
######################################################



class PotentiometerSampling:
    __GAIN = 1
    __poti_brightness = 200

    def __init__(self) -> None:
        
        self.__is_raspberry = is_raspberrypi()

        if self.__is_raspberry == True:
            import Adafruit_ADS1x15
            self.__adc = Adafruit_ADS1x15.ADS1115()

        self.__lock = Lock()
        __t = Thread(target=self.__sample_potentiometer_thread, daemon=True)
        __t.start() 


    def get_poti_brightness(self):
        return self.__poti_brightness
    
    def __read_poti_val(self):
        if self.__is_raspberry:
            return self.__adc.read_adc(0, gain=self.__GAIN, data_rate = 128)
        else:
            return randint(3,32558) 

    def __get_poti_brightness(self, current_value):
        ...
        min_value = 3
        max_value = 32558

        val_percent = (current_value - min_value) / (max_value - min_value)

        if val_percent > 1:
            val_percent = 1
        
        if val_percent < 0:
            val_percent = 0

        brightnes = int(round(255 * val_percent, 0))
        return brightnes
        

    def __sample_potentiometer_thread(self):
        ...

        while True:
            # value = self.adc.read_adc(0, gain=self.GAIN, data_rate = 128)
            value = self.__read_poti_val()
            # print("reading poti val:", value)
            brightness = self.__get_poti_brightness(value)

            with self.__lock:
                self.__poti_brightness = brightness
            time.sleep(0.2)
            

if __name__ == "__main__":
        ...

        poti = PotentiometerSampling()

        while True:

            # print("Poti val = ", poti.get_poti_brightness())

            time.sleep(1)


