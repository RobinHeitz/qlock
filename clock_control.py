from datetime import datetime
import pytz
import time
from pixel_definition import (
    HOUR_DEF, MIN_POINTS_DEF, WD_10_1, WD_2, WD_20_1, WD_5_1, WD_MIN_4, WD_IT_IS,WD_1_O_CLOCK,WD_CLOCK,
    WD_5_MIN_AFTER,WD_10_MIN_AFTER,WD_15_MIN_AFTER,WD_20_MIN_AFTER,WD_5_MIN_BEFORE_HALF,WD_HALF,
    WD_5_MIN_AFTER_HALF, WD_20_BEFORE,WD_15_BEFORE,WD_10_BEFORE,WD_5_BEFORE, WD_before, WD_quarter,
    WD_HAPPY, WD_HAPPY_BD,WD_BIRTHDAY,WD_CHARLY,WD_GOOD_NIGHT,WD_GOOD_MORNING
    )
from pixel_controller import PixelController

ACTIVATE_WORD_CHARLY = False

# BIRTH_DAY = (6,8) #month, day
BIRTH_DAY = (6,14) #month, day

def next_hour(current_h):
    if current_h == 23:
        return 0
    return current_h+1

def translate_to_12h_clock(h):
    if h > 12:
        return h % 12
    return h

def activate_minute_dots(controller, min_points):
    min_pixels = MIN_POINTS_DEF.get(min_points)

    if min_points == 0:
        controller.deactivatePixels(WD_MIN_4)
    else:
        controller.activatePixels(min_pixels)


def activate_it_is(controller):
    controller.activatePixels(WD_IT_IS)



def activate_hour(controller,min,hour):
    h = hour
    if min >= 25:
        h = next_hour(hour)

    if h == 1:
        controller.activatePixels(WD_1_O_CLOCK)
        return
    
    pixels = HOUR_DEF.get(h)
    # print("hour activation: pixels=", pixels)
    controller.activatePixels(pixels)

    if min < 5:
        #display 'UHR' additionally
        controller.activatePixels(WD_CLOCK)



def activate_clock_words(controller, min, h):
    if 0 <= min < 5:
        controller.deactivatePixels(WD_5_BEFORE)
    elif 5 <= min < 10:
        controller.activatePixels(WD_5_MIN_AFTER)
        controller.deactivatePixels(WD_CLOCK)
    elif 10 <= min < 15:
        controller.activatePixels(WD_10_MIN_AFTER)
        controller.deactivatePixels(WD_5_1)
    elif 15 <= min < 20:
        controller.activatePixels(WD_15_MIN_AFTER)
        controller.deactivatePixels(WD_10_1)
    elif 20 <= min < 25:
        controller.activatePixels(WD_20_MIN_AFTER)
        controller.deactivatePixels(WD_quarter)
    elif 25<= min < 30:
        controller.activatePixels(WD_5_MIN_BEFORE_HALF)
        controller.deactivatePixels(WD_20_1)
    elif 30<= min < 35:
        controller.activatePixels(WD_HALF)
        controller.deactivatePixels(WD_5_1+WD_before)
    elif 35<= min < 40:
        controller.activatePixels(WD_5_MIN_AFTER_HALF)
    elif 40<= min < 45:
        controller.activatePixels(WD_20_BEFORE)
        controller.deactivatePixels(WD_5_MIN_AFTER_HALF)
    elif 45<= min < 50:
        controller.activatePixels(WD_15_BEFORE)
        controller.deactivatePixels(WD_20_1)
    elif 50<= min < 55:
        controller.activatePixels(WD_10_BEFORE)
        controller.deactivatePixels(WD_quarter)
    elif min >= 55:
        controller.activatePixels(WD_5_BEFORE)
        controller.deactivatePixels(WD_10_1)


def handle_birthday(controller, isBirthday=False):
    if isBirthday:
        controller.activatePixelsRGB(WD_HAPPY,28,217,230)
        controller.activatePixelsRGB(WD_BIRTHDAY,242,8,148)
        controller.activatePixelsRGB(WD_CHARLY,255,255,51)
    else:
        controller.deactivatePixels(WD_HAPPY_BD)
        controller.deactivatePixels(WD_CHARLY)
        # controller.activatePixelsRGB(WD_HAPPY,255,0,0)


if __name__ == "__main__":
    

    birthday = False
    isGoodMorningActivated = False
    isGoodNightActivated = False

    isShowingClock = True

    controller = PixelController()
    
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
            hour = translate_to_12h_clock(hour_pre_transform)

            if m == BIRTH_DAY[0] and d == BIRTH_DAY[1]:
                birthday = True
            

            #check whether its time to say good morning:
            if local_time.isoweekday() <= 5:
                morning_time_start = local_time.replace(hour=10, minute=16, second=0, microsecond=0)
                morning_time_end = local_time.replace(hour=10, minute=16, second=30, microsecond=0)
                night_time_start = local_time.replace(hour=19, minute=44, second=0, microsecond=0)
                night_time_end = local_time.replace(hour=19, minute=50, second=0, microsecond=0)
            else:
                morning_time_start = local_time.replace(hour=9, minute=30, second=0, microsecond=0)
                morning_time_end = local_time.replace(hour=10, minute=30, second=0, microsecond=0)
                night_time_start = local_time.replace(hour=22, minute=0, second=0, microsecond=0)
                night_time_end = local_time.replace(hour=22, minute=30, second=0, microsecond=0)

            if morning_time_start <= local_time < morning_time_end:
                #show morning routine
                
                if isShowingClock:
                    #deactivate all pixels first

                    isShowingClock = False
                
                
                isGoodMorningActivated = True
                controller.activatePixels(WD_GOOD_MORNING)
                controller.activatePixels(WD_CHARLY)
            
            elif night_time_start <= local_time < night_time_end:
                isGoodNightActivated = True
                controller.activatePixels(WD_GOOD_NIGHT)
                controller.activatePixels(WD_CHARLY)
            
            
            
            else:
                isShowingClock = True
                
                #Outside of morning/night
                if isGoodMorningActivated:
                    controller.deactivatePixels(WD_GOOD_MORNING)
                    controller.deactivatePixels(WD_CHARLY)
                    isGoodMorningActivated = False
                
                elif isGoodNightActivated:
                    controller.deactivatePixels(WD_GOOD_NIGHT)
                    controller.deactivatePixels(WD_CHARLY)
                    isGoodNightActivated = False
                    


                activate_minute_dots(controller, min % 5)

                activate_it_is(controller)

                activate_hour(controller,min, hour)

                activate_clock_words(controller, min, hour)

                handle_birthday(controller, birthday)

                
            time.sleep(1)
    
    except KeyboardInterrupt:
        controller.deactivatePixels(list(range(16**2)))

