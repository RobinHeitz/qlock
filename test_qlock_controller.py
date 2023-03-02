import pytest
# from datetime import datetime

from qlock.constants import QlockMode
from qlock.controller import QlockController
from qlock.config_loader import load_config
from qlock.constants import CONFIG_FILE_NAME
from hw_interface.fake_hardware import QlockFakeHardwareInterface
# from qlock.time_helpers import create_dt

# Helper functions

def setup_controller():
    config = load_config(CONFIG_FILE_NAME)
    return QlockController(config, QlockFakeHardwareInterface())




def _testing_modes(time, expected_mode):
    c = setup_controller()

    modes = c.specify_clock_mode(time, False)
    assert len(modes) == 1
    assert expected_mode in modes

    modes = c.specify_clock_mode(time, True)
    assert QlockMode.mode_birthday in modes
    assert len(modes) == 2
    


# Tests
@pytest.mark.parametrize("month, day, is_bd", [
    (1,1, False),
    (10,10, False),
    (6,10, False),
    (6,14, True),
    (7,14, False),

])
def test_check_birthday(month, day, is_bd):
    c = setup_controller()
    assert is_bd == c.check_birthday(month, day)
