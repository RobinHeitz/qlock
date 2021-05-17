

from datetime import datetime
import pytz
import time

def next_hour(current_h):
    if current_h == 23:
        return 0
    return current_h+1


if __name__ == "__main__":
    while True:

        utc = pytz.timezone('UTC')
        now = utc.localize(datetime.utcnow())

        local_tz = pytz.timezone('Europe/Berlin')
        local_time = now.astimezone(local_tz)

        # hour = 23
        # min = 59
        # local_time = datetime(2021,5,13,hour, min)

        y = local_time.year
        m = local_time.month
        d = local_time.day
        h = local_time.hour
        min = local_time.minute

        if min == 0:
            print(f"Es ist {h} Uhr") 

        elif 0 < min < 5:
            print(f"Es ist {h} Uhr +{min}.")

        elif 5 <= min < 25:
            if min < 10:
                print(f"Es ist 5 min nach {h} + {min-5}")
            elif min < 15:
                print(f"Es ist 10 min nach {h} + {min-10}")
            elif min < 20:
                print(f"Es ist viertel nach {h} + {min-15}")
            elif min < 25:
                print(f"Es ist zwanzig nach {h} + {min-20}")



        elif 25 <= min <= 39:
            if min < 30:
                print(f"Es ist fünf vor halb {next_hour(h)} + {min-25}")
            elif min < 35:
                print(f"Es ist halb {next_hour(h)} + {min-30}")
            else:
                print(f"Es ist fünf nach halb {next_hour(h)} + {min-35}")

        elif 40 <= min :
            if min < 45:
                print(f"Es ist zwanzig vor {next_hour(h)} + {min-40}")
            elif min < 50:
                print(f"Es ist viertel vor {next_hour(h)} + {min-45}")
            elif min < 55:
                print(f"Es ist zehn vor {next_hour(h)} + {min-50}")
            else:
                print(f"Es ist fünf vor {next_hour(h)} + {min-55}")


        print(local_time)
        time.sleep(1)

