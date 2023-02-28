import pytz
from datetime import datetime
from typing import Tuple


def transform_hours_to_clock_format(hour: int):
    """We need hours within [1,12], therefore transformation might take place."""
    return hour % 12


def shift_hour(hour):
    """For some times (depending on current minutes), we 'add' one hour:
    
    12:20 (20 nach 12) vs. 12.40 (20 vor 1)."""
    return (hour + 1) % 24
    
    
def get_localized_date_segments() -> Tuple[int, int, int, int]:
    """Creates datetime.datetime object with local timezone.
    
    Returns (month, day, hour, min),"""
    utc = pytz.timezone('UTC')
    now = utc.localize(datetime.utcnow())

    local_tz = pytz.timezone('Europe/Berlin')
    local_time = now.astimezone(local_tz)

    y = local_time.year
    m = local_time.month
    d = local_time.day

    hour = transform_hours_to_clock_format(local_time.hour)
    min_ = local_time.minute
    return m, d, hour, min_
