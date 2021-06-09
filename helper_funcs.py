from pixel_definition import (
    WD_5_BEFORE, WD_IT_IS, WD_1, WD_10_1, WD_10_2, WD_10_BEFORE, WD_10_MIN_AFTER, WD_11, WD_12, WD_15_BEFORE, 
    WD_15_MIN_AFTER, WD_1_O_CLOCK, WD_2, WD_20_1, WD_20_BEFORE, WD_20_MIN_AFTER, WD_3_1,WD_4, WD_5_1, WD_5_2, 
    WD_5_MIN_AFTER, WD_5_MIN_AFTER_HALF, WD_5_MIN_BEFORE_HALF, WD_6, WD_7, WD_8, WD_9, WD_after, WD_before, 
    WD_CHARLY, WD_CLOCK, WD_GOOD_MORNING, WD_GOOD_NIGHT, WD_HALF, WD_HAPPY, WD_HAPPY_BD, WD_MIN_1, WD_MIN_4, 
    WD_quarter, WD_three_quarter, WD_3_2, WD_ALL_PIXELS, WD_BIRTHDAY, WD_GOOD, WD_MIN_2, WD_MIN_3, WD_NIGHT,HOUR_DEF
)


def next_hour(current_h):
        if current_h == 23:
            return 0
        return current_h+1


def translate_to_12h_clock_format(h):
    if h > 12:
        return h % 12
    return h


def clock_words(min):
        if 0 <= min < 5:
            return []
            # self.controller.deactivatePixels(WD_5_BEFORE)
        elif 5 <= min < 10:
            return WD_5_MIN_AFTER
            # self.controller.activatePixels(WD_5_MIN_AFTER)
            # self.controller.deactivatePixels(WD_CLOCK)
        elif 10 <= min < 15:
            return WD_10_MIN_AFTER
            # self.controller.activatePixels(WD_10_MIN_AFTER)
            # self.controller.deactivatePixels(WD_5_1)
        elif 15 <= min < 20:
            return WD_15_MIN_AFTER
            # self.controller.activatePixels(WD_15_MIN_AFTER)
            # self.controller.deactivatePixels(WD_10_1)
        elif 20 <= min < 25:
            return WD_20_MIN_AFTER
            # self.controller.activatePixels(WD_20_MIN_AFTER)
            # self.controller.deactivatePixels(WD_quarter)
        elif 25<= min < 30:
            return WD_5_MIN_BEFORE_HALF
            # self.controller.activatePixels(WD_5_MIN_BEFORE_HALF)
            # self.controller.deactivatePixels(WD_20_1)
            # self.controller.deactivatePixels(WD_after)
        elif 30<= min < 35:
            return WD_HALF
            # self.controller.activatePixels(WD_HALF)
            # self.controller.deactivatePixels(WD_5_1+WD_before)
        elif 35<= min < 40:
            return WD_5_MIN_AFTER_HALF
            # self.controller.activatePixels(WD_5_MIN_AFTER_HALF)
        elif 40<= min < 45:
            return WD_20_BEFORE
            # self.controller.activatePixels(WD_20_BEFORE)
            # self.controller.deactivatePixels(WD_5_MIN_AFTER_HALF)
        elif 45<= min < 50:
            return WD_15_BEFORE
            # self.controller.activatePixels(WD_15_BEFORE)
            # self.controller.deactivatePixels(WD_20_1)
        elif 50<= min < 55:
            return WD_10_BEFORE
            # self.controller.activatePixels(WD_10_BEFORE)
            # self.controller.deactivatePixels(WD_quarter)
        elif min >= 55:
            return WD_5_BEFORE
            # self.controller.activatePixels(WD_5_BEFORE)
            # self.controller.deactivatePixels(WD_10_1)



def hour_wording_rep(min,hour):
    returnPixels = []
    
    if min >= 25:
        hour = next_hour(hour)

    if hour == 1 and min < 5:
        # self.controller.activatePixels(WD_1_O_CLOCK)
        returnPixels = returnPixels + WD_1_O_CLOCK
    else:
        returnPixels = returnPixels + HOUR_DEF.get(hour)
    
    # pixels = HOUR_DEF.get(h)
    # print("hour activation: pixels=", pixels)
    # self.controller.activatePixels(pixels)

    if min < 5:
        #display 'UHR' additionally
        returnPixels = returnPixels + WD_CLOCK
        # self.controller.activatePixels(WD_CLOCK)

    return returnPixels

