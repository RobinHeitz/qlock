import pytest
from datetime import datetime

from qlock.time_helpers import shift_hour, transform_hours_to_clock_format, get_clock_mode, create_dt, localized_dt
from qlock.constants import QlockMode


### SETUP

def day_times_mockup():
    """Returns a config (yaml parsed) configuration of times."""

    early_day_times = {
        "morning": {
            "start":dict(
                hour=6, minute=15, second=0
            ),
            "end":dict(
                hour=6, minute=45, second=0
            )
        },
        "night": {
            "start":dict(
                hour=21, minute=0, second=0
            ),
            "end":dict(
                hour=22, minute=15, second=0
            )
        },
    }

    late_day_times = {
        "morning": {
            "start":dict(
                hour=9, minute=0, second=0
            ),
            "end":dict(
                hour=10, minute=30, second=0
            )
        },
        "night": {
            "start":dict(
                hour=22, minute=30, second=0
            ),
            "end":dict(
                hour=23, minute=45, second=0
            )
        },
    }

    return early_day_times, late_day_times
    




### TESTS

def test_localized_dt():
    dt = localized_dt()
    assert type(dt) == datetime

    now = datetime.now()
    assert now.year == dt.year
    assert now.month == dt.month
    assert now.day == dt.day



@pytest.mark.parametrize("hour, expected_hour", [
    *[(i, i) for i in range(1,13)],
    *[(i,i-12) for i in range(13,24)]
])
def test_transform_clock_format(hour, expected_hour):
    assert expected_hour == transform_hours_to_clock_format(hour)


@pytest.mark.parametrize("hour, min, expected_hour", [
    (1,29,1),
    (1,30,2),
    (1,59,2),
    (2,0,2),
])
def test_shift_hour(hour, min, expected_hour):
    assert expected_hour == shift_hour(hour, min)


def test_shif_tranform_combination():
    hour = 12
    minute = 40

    hour = shift_hour(hour, minute)
    hour = transform_hours_to_clock_format(hour)
    assert hour == 1


@pytest.mark.parametrize("hour, minute, expected_clock_mode", [
    (6,14, QlockMode.mode_normal),
    (6,15, QlockMode.mode_morning),
    (6,45, QlockMode.mode_morning),
    (6,46, QlockMode.mode_normal),
])
def test_get_clock_mode_early_morning(hour, minute, expected_clock_mode:QlockMode):
    early_times, late_times = day_times_mockup()
    # time represents a thursday morning
    time = create_dt(year=2023, month=3, day=2, hour=hour, minute=minute)
    mode = get_clock_mode(early_times, late_times, time)
    assert mode == expected_clock_mode

    

@pytest.mark.parametrize("hour, minute, expected_clock_mode", [
    (8,59, QlockMode.mode_normal),
    (9,0, QlockMode.mode_morning),
    (10,30, QlockMode.mode_morning), (10,31, QlockMode.mode_normal),
])
def test_get_clock_mode_late_morning(hour, minute, expected_clock_mode:QlockMode):
    early_times, late_times = day_times_mockup()
    # time represents a saturday morning
    time = create_dt(year=2023, month=3, day=4, hour=hour, minute=minute)
    mode = get_clock_mode(early_times, late_times, time)
    assert mode == expected_clock_mode




@pytest.mark.parametrize("hour, minute, expected_clock_mode", [
    (20,59, QlockMode.mode_normal),
    (21,0, QlockMode.mode_night),
    (22,15, QlockMode.mode_night),
    (22,16, QlockMode.mode_normal),
])
def test_get_clock_mode_early_night(hour, minute, expected_clock_mode:QlockMode):
    early_times, late_times = day_times_mockup()
    # time represents a thursday night
    time = create_dt(year=2023, month=3, day=2, hour=hour, minute=minute)
    mode = get_clock_mode(early_times, late_times, time)
    assert mode == expected_clock_mode


    
@pytest.mark.parametrize("hour, minute, expected_clock_mode", [
    (22,29, QlockMode.mode_normal),
    (22,30, QlockMode.mode_night),
    (23,45, QlockMode.mode_night),
    (23,46, QlockMode.mode_normal),
])
def test_get_clock_mode_late_night(hour, minute, expected_clock_mode:QlockMode):
    early_times, late_times = day_times_mockup()
    # time represents a friday night
    time = create_dt(year=2023, month=3, day=3, hour=hour, minute=minute)
    mode = get_clock_mode(early_times, late_times, time)
    assert mode == expected_clock_mode


