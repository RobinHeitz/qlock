import pytz
from datetime import datetime
from typing import Tuple
from .constants import QlockMode


def create_dt(year, month, day, hour, minute, **kwargs) -> datetime:
    """Creates a localized datetime and replaces the attributes.
    
    Params (These are actually params of the datetime.datetime.replace function):
    - year (int)
    - month (int)
    - day (int)
    - hour (int)
    - minute (int)
    - second (int)
    
    Returns datetime.datetime object.
    """
    time = localized_dt()
    return time.replace(year=year, month=month, day=day, minute=minute, hour=hour, second=0, **kwargs)


def transform_hours_to_clock_format(hour: int):
    """We need hours within [1,12], therefore transformation might take place."""
    if hour > 12:
        return hour % 12
    return hour


def shift_hour(hour, minute):
    """For some times (depending on current minutes), we 'add' one hour:
    
    12:20 (20 nach 12) vs. 12.40 (20 vor 1)."""
    if minute >= 30:
        return (hour + 1) % 24
    return hour


def localized_dt() -> datetime:
    """Returns a localized datetime.now() object."""
    utc = pytz.timezone('UTC')
    now = utc.localize(datetime.utcnow())

    local_tz = pytz.timezone('Europe/Berlin')
    local_time = now.astimezone(local_tz)
    return local_time
    
def get_localized_date_segments() -> Tuple[datetime, int, int, int, int]:
    """Creates datetime.datetime object with local timezone.
    
    Returns (month, day, hour, min),"""
    local_time = localized_dt()
    y = local_time.year
    m = local_time.month
    d = local_time.day

    hour = transform_hours_to_clock_format(local_time.hour)
    min_ = local_time.minute
    return local_time, m, d, hour, min_


def get_clock_mode(early_day_times:dict, late_day_times:dict, now:datetime) -> QlockMode:
    """Calculates the clock state based on the yaml config and current datetime.datetime object.
    
    Returns the correct QlockMode."""

    # define bounds for morning
    if now.isoweekday() <= 5:
        morning_lower = now.replace(**early_day_times.get("morning").get("start"))
        morning_upper = now.replace(**early_day_times.get("morning").get("end"))
    else:
        morning_lower = now.replace(**late_day_times.get("morning").get("start"))
        morning_upper = now.replace(**late_day_times.get("morning").get("end"))
    

    # define bounds for night
    if 5 <= now.isoweekday() <= 6:
        night_lower = now.replace(**late_day_times.get("night").get("start"))
        night_upper = now.replace(**late_day_times.get("night").get("end"))
    else:
        night_lower = now.replace(**early_day_times.get("night").get("start"))
        night_upper = now.replace(**early_day_times.get("night").get("end"))


    if morning_lower <= now <= morning_upper:
        return QlockMode.mode_morning
    elif night_lower <= now <= night_upper:
        return QlockMode.mode_night
    return QlockMode.mode_normal

