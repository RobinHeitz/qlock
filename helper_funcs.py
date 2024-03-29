from pixel_definition import (
    WD_5_BEFORE, WD_IT_IS, WD_1, WD_10_1, WD_10_2, WD_10_BEFORE, WD_10_MIN_AFTER, WD_11, WD_12, WD_15_BEFORE, 
    WD_15_MIN_AFTER, WD_1_O_CLOCK, WD_2, WD_20_1, WD_20_BEFORE, WD_20_MIN_AFTER, WD_3_1,WD_4, WD_5_1, WD_5_2, 
    WD_5_MIN_AFTER, WD_5_MIN_AFTER_HALF, WD_5_MIN_BEFORE_HALF, WD_6, WD_7, WD_8, WD_9, WD_after, WD_before, 
    WD_CHARLY, WD_CLOCK, WD_GOOD_MORNING, WD_GOOD_NIGHT, WD_HALF, WD_HAPPY, WD_HAPPY_BD, WD_MIN_1, WD_MIN_4, 
    WD_quarter, WD_three_quarter, WD_3_2, WD_ALL_PIXELS, WD_BIRTHDAY, WD_GOOD, WD_MIN_2, WD_MIN_3, WD_NIGHT,HOUR_DEF
)

CLOCK_STATE_NORMAL = "CLOCK_STATE_NORMAL"
CLOCK_STATE_SHOW_GOOD_MORNING = "CLOCK_STATE_SHOW_GOOD_MORNING"
CLOCK_STATE_SHOW_GOOD_NIGHT = "CLOCK_STATE_SHOW_GOOD_NIGHT"




import io
def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False



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
        elif 5 <= min < 10:
            return WD_5_MIN_AFTER
        elif 10 <= min < 15:
            return WD_10_MIN_AFTER
        elif 15 <= min < 20:
            return WD_15_MIN_AFTER
        elif 20 <= min < 25:
            return WD_20_MIN_AFTER
        elif 25<= min < 30:
            return WD_5_MIN_BEFORE_HALF
        elif 30<= min < 35:
            return WD_HALF
        elif 35<= min < 40:
            return WD_5_MIN_AFTER_HALF
        elif 40<= min < 45:
            return WD_20_BEFORE
        elif 45<= min < 50:
            return WD_15_BEFORE
        elif 50<= min < 55:
            return WD_10_BEFORE
        elif min >= 55:
            return WD_5_BEFORE


def hour_wording_rep(min,hour):
    
    returnPixels = []
    
    if min >= 25:
        hour = translate_to_12h_clock_format(next_hour(hour))

    if hour == 1 and min < 5:
        returnPixels = returnPixels + WD_1_O_CLOCK
    else:
        returnPixels = returnPixels + HOUR_DEF.get(hour,[])
    
    if min < 5:
        #display 'UHR' additionally
        returnPixels = returnPixels + WD_CLOCK
    return returnPixels



def determineClockState(
    local_time, 
    early_morning_start, 
    early_morning_end, 
    early_night_start, 
    early_night_end, 
    late_morning_start, 
    late_morning_end, 
    late_night_start, 
    late_night_end
    ):
    
        newState = None

        # morning routine:
        if local_time.isoweekday() <= 5:
            morning_time_start = local_time.replace(**early_morning_start)
            morning_time_end = local_time.replace(**early_morning_end)
        else:
            morning_time_start = local_time.replace(**late_morning_start)
            morning_time_end = local_time.replace(**late_morning_end)
        
        # night routine
        if 5 <= local_time.isoweekday() <= 6:
            night_time_start = local_time.replace(**late_night_start)
            night_time_end = local_time.replace(**late_night_end)

        else:
            night_time_start = local_time.replace(**early_night_start)
            night_time_end = local_time.replace(**early_night_end)



        if morning_time_start <= local_time < morning_time_end:
            newState = CLOCK_STATE_SHOW_GOOD_MORNING
            print("CLOCKSTATE = CLOCKSTATE GOOD MORNING")
        elif night_time_start <= local_time < night_time_end:
            newState = CLOCK_STATE_SHOW_GOOD_NIGHT
            print("CLOCKSTATE = CLOCKSTATE GOOD NIGHT")
        else:
            newState = CLOCK_STATE_NORMAL
            print("CLOCKSTATE = NORMAL")

        
        return newState
        