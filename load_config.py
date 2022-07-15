import yaml

def load_config_from_file():

    """Returns config loaded from yaml. If no file was found, it provides standard values.
    
    Returns:
    - birthday config
    - early morning config
    - early night config
    - late morning config
    - late night config"""

    
    try:
        with open("config.yaml", "r") as stream:
            loaded_config = yaml.safe_load(stream)
    except Exception as e:
        print(e)
        loaded_config = dict()
    
    finally:
        birthday =  loaded_config.get('birthday', dict(month=6, day=14))
        early_morning = loaded_config.get('early_morning', dict(start_hour=6, start_min=15, end_hour=6, end_min=45))
        early_night = loaded_config.get('early_night', dict(start_hour=21, start_min=15, end_hour=21, end_min=45))
        late_morning = loaded_config.get('late_morning', dict(start_hour=8, start_min=45, end_hour=9, end_min=15))
        late_night = loaded_config.get('late_night', dict(start_hour=22, start_min=30, end_hour=23, end_min=0))

        
        return birthday, early_morning, early_night, late_morning, late_night

if __name__ == "__main__":

    print(load_config_from_file())
