import pytest
from pathlib import Path
from qlock.config_loader import load_config

CONFIG_FILE = Path("qlock.yaml")



def test_load_config():
    config = load_config(str(CONFIG_FILE))

    assert type(config) == dict
    assert config != None
    assert "birthday" in config
    assert "early_day_times" in config
    assert "late_day_times" in config


if __name__ == "__main__":
    test_load_config()
