import argparse

from qlock.config_loader import load_config
from qlock.controller import QlockController
from qlock.constants import CONFIG_FILE_NAME

from hw_interface.fake_hardware import QlockFakeHardwareInterface
from hw_interface.qlock_hw import QlockLEDMatrix


def main():
    """Gets called in script execution."""

    parser = argparse.ArgumentParser(
        prog = 'ProgramName',
        description = 'What the program does',
        epilog = 'Text at the bottom of help')
    
    parser.add_argument('-f', '--fake', action="store_true", help="Don't try to access hardware, instead, virtualize qlock.")
    args = parser.parse_args() 
    fake = args.fake



    if fake == True:
        hw_interface = QlockFakeHardwareInterface
    else:
        hw_interface = QlockLEDMatrix


    config = load_config(CONFIG_FILE_NAME)
    controller = QlockController(config=config, hw = hw_interface())







if __name__ == "__main__":
    main()