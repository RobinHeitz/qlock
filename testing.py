# %%


CLOCK_STATE_SHOW_CLOCK_TIME = "CLOCK_STATE_SHOW_CLOCK_TIME"
CLOCK_STATE_SHOW_GOOD_MORNING = "CLOCK_STATE_SHOW_GOOD_MORNING"
CLOCK_STATE_SHOW_GOOD_NIGHT = "CLOCK_STATE_SHOW_GOOD_NIGHT"

WEEKDAY_MORNING_START = (6,20) #hour, min
WEEKDAY_MORNING_END = (6,45)
WEEKDAY_NIGHT_START = (22,15)
WEEKDAY_NIGHT_END = (22,30)

WEEKEND_MORNING_START = (9,0)
WEEKEND_MORNING_END = (10,0)
WEEKEND_NIGHT_START = (22,30)
WEEKEND_NIGHT_END = (23,0)

# %%
def determineClockState(local_time):
        newState = None

        # trying stuff out for bugfixing

        # return CLOCK_STATE_SHOW_CLOCK_TIME

        if local_time.isoweekday() <= 5:
            morning_time_start = local_time.replace(hour=WEEKDAY_MORNING_START[0], minute=WEEKDAY_MORNING_START[1], second=0, microsecond=0)
            morning_time_end = local_time.replace(hour=WEEKDAY_MORNING_END[0], minute=WEEKDAY_MORNING_END[1], second=0, microsecond=0)
            night_time_start = local_time.replace(hour=WEEKDAY_NIGHT_START[0], minute=WEEKDAY_NIGHT_START[1], second=0, microsecond=0)
            night_time_end = local_time.replace(hour=WEEKDAY_NIGHT_END[0], minute=WEEKDAY_NIGHT_END[1], second=0, microsecond=0)
        else:
            morning_time_start = local_time.replace(hour=WEEKEND_MORNING_START[0], minute=WEEKDAY_MORNING_START[1], second=0, microsecond=0)
            morning_time_end = local_time.replace(hour=WEEKEND_MORNING_END[0], minute=WEEKEND_MORNING_END[1], second=0, microsecond=0)
            night_time_start = local_time.replace(hour=WEEKEND_NIGHT_START[0], minute=WEEKEND_NIGHT_START[1], second=0, microsecond=0)
            night_time_end = local_time.replace(hour=WEEKEND_NIGHT_END[0], minute=WEEKEND_NIGHT_END[1], second=0, microsecond=0)
        
        if morning_time_start <= local_time < morning_time_end:
            newState = CLOCK_STATE_SHOW_GOOD_MORNING
        elif night_time_start <= local_time < night_time_end:
            newState = CLOCK_STATE_SHOW_GOOD_NIGHT
        else:
            newState = CLOCK_STATE_SHOW_CLOCK_TIME
        
        return newState

# %%

import pytz
import datetime
from datetime import time

utc = pytz.timezone('UTC')
now = utc.localize(datetime.datetime.utcnow())

local_tz = pytz.timezone('Europe/Berlin')
local_time = now.astimezone(local_tz)

# %%

from datetime import timedelta

delta = timedelta(hours=1)

local_time = datetime.datetime.now() + delta

print(local_time)

determineClockState(local_time)