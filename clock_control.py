from datetime import datetime
import pytz
import time
from pixel_definition import (
    HOUR_DEF, MIN_POINTS_DEF, WD_10_1, WD_2, WD_20_1, WD_5_1, WD_MIN_4, WD_IT_IS,WD_1_O_CLOCK,WD_CLOCK,
    WD_5_MIN_AFTER,WD_10_MIN_AFTER,WD_15_MIN_AFTER,WD_20_MIN_AFTER,WD_5_MIN_BEFORE_HALF,WD_HALF,
    WD_5_MIN_AFTER_HALF, WD_20_BEFORE,WD_15_BEFORE,WD_10_BEFORE,WD_5_BEFORE, WD_before, WD_quarter,
    WD_HAPPY, WD_HAPPY_BD,WD_BIRTHDAY,WD_CHARLY,WD_GOOD_NIGHT,WD_GOOD_MORNING,WD_ALL_PIXELS, WD_GOOD, WD_NIGHT,
    )
from pixel_controller import PixelController

class ClockControl:

    def __init__(self):
        self.BIRTH_DAY = (6,14) #month, day
        # self.BIRTH_DAY = (6,9) #month, day
        
        self.isBirthdayActivated = False
        self.birthday = False
        
        self.isGoodMorningActivated = False
        self.isGoodNightActivated = False

        self.isShowingClock = True

        self.controller = PixelController()

        self.start_clock()

    
    def start_clock(self):
        try:
            while True:
                utc = pytz.timezone('UTC')
                now = utc.localize(datetime.utcnow())

                local_tz = pytz.timezone('Europe/Berlin')
                local_time = now.astimezone(local_tz)

                y = local_time.year
                m = local_time.month
                d = local_time.day
                hour_pre_transform = local_time.hour
                min = local_time.minute
                hour = self.translate_to_12h_clock(hour_pre_transform)

                if m == self.BIRTH_DAY[0] and d == self.BIRTH_DAY[1]:
                    self.birthday = True
                    self.isBirthdayActivated = True
                else: 
                    self.birthday= False

                

                #check whether its time to say good morning:
                if local_time.isoweekday() <= 5:
                    morning_time_start = local_time.replace(hour=11, minute=28, second=0, microsecond=0)
                    morning_time_end = local_time.replace(hour=11, minute=43, second=30, microsecond=0)
                    night_time_start = local_time.replace(hour=19, minute=44, second=0, microsecond=0)
                    night_time_end = local_time.replace(hour=19, minute=45, second=0, microsecond=0)
                else:
                    morning_time_start = local_time.replace(hour=9, minute=30, second=0, microsecond=0)
                    morning_time_end = local_time.replace(hour=10, minute=30, second=0, microsecond=0)
                    night_time_start = local_time.replace(hour=22, minute=0, second=0, microsecond=0)
                    night_time_end = local_time.replace(hour=22, minute=30, second=0, microsecond=0)

                
                if morning_time_start <= local_time < morning_time_end and self.birthday is False:
                    #show morning routine
                    
                    if self.isShowingClock:
                        #deactivate all pixels first
                        self.controller.deactivatePixels(WD_ALL_PIXELS)
                        self.isShowingClock = False
                    
                    
                    self.isGoodMorningActivated = True
                    self.controller.activatePixelsRGB(WD_GOOD_MORNING,0,255,128)
                    self.controller.activatePixelsRGB(WD_CHARLY,255,51,51)
                
                elif night_time_start <= local_time < night_time_end and self.birthday is False:
                    #show good night routine

                    if self.isShowingClock:
                        #deactivate all pixels first
                        self.controller.deactivatePixels(WD_ALL_PIXELS)
                        self.isShowingClock = False

                    self.isGoodNightActivated = True
                    self.controller.activatePixelsRGB(WD_GOOD,255,128,0)
                    self.controller.activatePixelsRGB(WD_NIGHT,0,255,128)
                    self.controller.activatePixelsRGB(WD_CHARLY,255,51,51)
                
                
                
                else:
                    self.isShowingClock = True
                    
                    #Outside of morning/night
                    if self.isGoodMorningActivated:
                        self.controller.deactivatePixels(WD_GOOD_MORNING)
                        self.controller.deactivatePixels(WD_CHARLY)
                        self.isGoodMorningActivated = False
                    
                    elif self.isGoodNightActivated:
                        self.controller.deactivatePixels(WD_GOOD_NIGHT)
                        self.controller.deactivatePixels(WD_CHARLY)
                        self.isGoodNightActivated = False
                        


                    self.activate_minute_dots(min % 5)

                    self.activate_it_is()

                    self.activate_hour(min, hour)

                    self.activate_clock_words( min, hour)

                    self.handle_birthday()

                    
            time.sleep(1)
    
        except KeyboardInterrupt:
            self.controller.deactivatePixels(list(range(16**2)))




    def next_hour(self,current_h):
        if current_h == 23:
            return 0
        return current_h+1

    def translate_to_12h_clock(self,h):
        if h > 12:
            return h % 12
        return h

    def activate_minute_dots(self,min_points):
        min_pixels = MIN_POINTS_DEF.get(min_points)

        if min_points == 0:
            self.controller.deactivatePixels(WD_MIN_4)
        else:
            self.controller.activatePixels(min_pixels)


    def activate_it_is(self):
        self.controller.activatePixels(WD_IT_IS)



    def activate_hour(self,min,hour):
        h = hour
        if min >= 25:
            h = self.next_hour(hour)

        if h == 1:
            self.controller.activatePixels(WD_1_O_CLOCK)
            return
        
        pixels = HOUR_DEF.get(h)
        # print("hour activation: pixels=", pixels)
        self.controller.activatePixels(pixels)

        if min < 5:
            #display 'UHR' additionally
            self.controller.activatePixels(WD_CLOCK)



    def activate_clock_words(self,min, h):
        if 0 <= min < 5:
            self.controller.deactivatePixels(WD_5_BEFORE)
        elif 5 <= min < 10:
            self.controller.activatePixels(WD_5_MIN_AFTER)
            self.controller.deactivatePixels(WD_CLOCK)
        elif 10 <= min < 15:
            self.controller.activatePixels(WD_10_MIN_AFTER)
            self.controller.deactivatePixels(WD_5_1)
        elif 15 <= min < 20:
            self.controller.activatePixels(WD_15_MIN_AFTER)
            self.controller.deactivatePixels(WD_10_1)
        elif 20 <= min < 25:
            self.controller.activatePixels(WD_20_MIN_AFTER)
            self.controller.deactivatePixels(WD_quarter)
        elif 25<= min < 30:
            self.controller.activatePixels(WD_5_MIN_BEFORE_HALF)
            self.controller.deactivatePixels(WD_20_1)
        elif 30<= min < 35:
            self.controller.activatePixels(WD_HALF)
            self.controller.deactivatePixels(WD_5_1+WD_before)
        elif 35<= min < 40:
            self.controller.activatePixels(WD_5_MIN_AFTER_HALF)
        elif 40<= min < 45:
            self.controller.activatePixels(WD_20_BEFORE)
            self.controller.deactivatePixels(WD_5_MIN_AFTER_HALF)
        elif 45<= min < 50:
            self.controller.activatePixels(WD_15_BEFORE)
            self.controller.deactivatePixels(WD_20_1)
        elif 50<= min < 55:
            self.controller.activatePixels(WD_10_BEFORE)
            self.controller.deactivatePixels(WD_quarter)
        elif min >= 55:
            self.controller.activatePixels(WD_5_BEFORE)
            self.controller.deactivatePixels(WD_10_1)


    def handle_birthday(self):
        if self.birthday:
            self.controller.activatePixelsRGB(WD_HAPPY,28,217,230)
            self.controller.activatePixelsRGB(WD_BIRTHDAY,242,8,148)
            self.controller.activatePixelsRGB(WD_CHARLY,255,255,51)
        else:
            if self.isBirthdayActivated:
                self.controller.deactivatePixels(WD_HAPPY_BD)
                self.controller.deactivatePixels(WD_CHARLY)
                self.isBirthdayActivated = False





if __name__ == "__main__":
    controller = ClockControl()