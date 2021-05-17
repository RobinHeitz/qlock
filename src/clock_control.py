from datetime import datetime
import pytz
import time
from pixel_definition import *
from pixel_controller import PixelController

# import pixel_definition
# import pixel_controller




# BIRTH_DAY = (5,17) #month, day
BIRTH_DAY = (6,14) #month, day

def next_hour(current_h):
    if current_h == 23:
        return 0
    return current_h+1


if __name__ == "__main__":
    

    birthday = False

    controller = PixelController()
    
    while True:
        utc = pytz.timezone('UTC')
        now = utc.localize(datetime.utcnow())

        local_tz = pytz.timezone('Europe/Berlin')
        local_time = now.astimezone(local_tz)

        y = local_time.year
        m = local_time.month
        d = local_time.day
        h = local_time.hour
        min = local_time.minute

        if m == BIRTH_DAY[0] and d == BIRTH_DAY[1]:
            print("ITS HER BIRTHDAY")
            birthday = True
        

        #setting the clock


        #settings minute points
        min_points = min % 5
            
        if min_points == 1:
            print("1")
            controller.activatePixels(WD_MIN_1)
        elif min_points == 2:
            controller.activatePixels(WD_MIN_2)
            print("2")
        elif min_points == 3:
            controller.activatePixels(WD_MIN_3)
            print("3")
        elif min_points == 4:
            controller.activatePixels(WD_MIN_4)
            print("4")




        




        time.sleep(1)


    








        # if min == 0:
        #     print(f"Es ist {h} Uhr") 

        # elif 0 < min < 5:
        #     print(f"Es ist {h} Uhr +{min}.")

        # elif 5 <= min < 25:
        #     if min < 10:
        #         print(f"Es ist 5 min nach {h} + {min-5}")
        #     elif min < 15:
        #         print(f"Es ist 10 min nach {h} + {min-10}")
        #     elif min < 20:
        #         print(f"Es ist viertel nach {h} + {min-15}")
        #     elif min < 25:
        #         print(f"Es ist zwanzig nach {h} + {min-20}")



        # elif 25 <= min <= 39:
        #     if min < 30:
        #         print(f"Es ist fuenf vor halb {next_hour(h)} + {min-25}")
        #     elif min < 35:
        #         print(f"Es ist halb {next_hour(h)} + {min-30}")
        #     else:
        #         print(f"Es ist fuenf nach halb {next_hour(h)} + {min-35}")

        # elif 40 <= min :
        #     if min < 45:
        #         print(f"Es ist zwanzig vor {next_hour(h)} + {min-40}")
        #     elif min < 50:
        #         print(f"Es ist viertel vor {next_hour(h)} + {min-45}")
        #     elif min < 55:
        #         print(f"Es ist zehn vor {next_hour(h)} + {min-50}")
        #     else:
        #         print(f"Es ist fuenf vor {next_hour(h)} + {min-55}")

