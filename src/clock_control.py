from datetime import datetime
import pytz
import time
from pixel_definition import (
    HOUR_DEF, MIN_POINTS_DEF, WD_MIN_4, WD_IT_IS,WD_1_O_CLOCK,WD_CLOCK,
    WD_5_MIN_AFTER,WD_10_MIN_AFTER,WD_15_MIN_AFTER,WD_20_MIN_AFTER,WD_5_MIN_BEFORE_HALF,WD_HALF,
    WD_5_MIN_AFTER_HALF, WD_20_BEFORE,WD_15_BEFORE,WD_10_BEFORE,WD_5_BEFORE,
    )
from pixel_controller import PixelController



# BIRTH_DAY = (5,17) #month, day
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





def activate_words(controller, min, h):
    if 5 <= min < 10:
        controller.activatePixels(WD_5_MIN_AFTER)
    elif 10 <= min < 15:
        controller.activatePixels(WD_10_MIN_AFTER)
    elif 15 <= min < 20:
        controller.activatePixels(WD_15_MIN_AFTER)
    elif 20 <= min < 25:
        controller.activatePixels(WD_20_MIN_AFTER)
    elif 25<= min < 30:
        controller.activatePixels(WD_5_MIN_BEFORE_HALF)
    elif 30<= min < 35:
        controller.activatePixels(WD_HALF)
    elif 35<= min < 40:
        controller.activatePixels(WD_5_MIN_AFTER_HALF)
    elif 40<= min < 45:
        controller.activatePixels(WD_20_BEFORE)
    elif 45<= min < 50:
        controller.activatePixels(WD_15_BEFORE)
    elif 50<= min < 55:
        controller.activatePixels(WD_10_BEFORE)
    elif min >= 55:
        controller.activatePixels(WD_5_BEFORE)
    
    
    
    
    # if min == 0:
    #         print("Es ist {} Uhr".format(h)) 

    # elif 0 < min < 5:
    #     print("Es ist {} Uhr +{}.".format(h, min))
    # elif 5 <= min < 25:
    #     if min < 10:
    #         print("Es ist 5 min nach {} + {}".format(h, min-5))
    #     elif min < 15:
    #         print("Es ist 10 min nach {} + {}".format(h, min-10))
    #     elif min < 20:
    #         print("Es ist viertel nach {} + {}".format(h, min-15))
    #     elif min < 25:
    #         print("Es ist zwanzig nach {} + {}".format(h, min-20))



    # elif 25 <= min <= 39:
    #     if min < 30:
    #         print("Es ist fuenf vor halb {} + {}".format(next_hour(h), min-25))
    #     elif min < 35:
    #         print("Es ist halb {} + {}".format(next_hour(h), min-30))
    #     else:
    #         print("Es ist fuenf nach halb {} + {}".format(next_hour(h), min-35))

    # elif 40 <= min :
    #     if min < 45:
    #         print("Es ist zwanzig vor {} + {}".format(next_hour(h), min-40))
    #     elif min < 50:
    #         print("Es ist viertel vor {} + {}".format(next_hour(h), min-45))
    #     elif min < 55:
    #         print("Es ist zehn vor {} + {}".format(next_hour(h), min-50))
    #     else:
    #         print("Es ist fuenf vor {} + {}".format(next_hour(h), min-55))




if __name__ == "__main__":
    

    birthday = False

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
                print("ITS HER BIRTHDAY")
                birthday = True
            

            #settings minute points
            min_points = min % 5
            activate_minute_dots(controller, min_points)

            activate_it_is(controller)

            activate_hour(controller,min, hour)

            activate_words(controller, min, hour)
                


            time.sleep(1)
    
    except KeyboardInterrupt:
        controller.deactivatePixels(list(range(16**2)))

