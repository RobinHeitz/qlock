import yaml

def load_config_from_file(filepath):

    """Returns config loaded from yaml as tuples of dicts.
    
    Returns:
    - birthday config
    - early morning start
    - early morning end
    - early night start
    - early night end
    - late morning start
    - late morning end
    - late night start
    - late night end
    """
    
    try:
        with open(filepath, "r") as stream:
            loaded_config = yaml.safe_load(stream)
    except Exception as e:
        print(e)
        loaded_config = dict()
    
    finally:

        keys = [
            "birthday", 
            "early_morning_start","early_morning_end",
            "early_night_start","early_night_end",
            "late_morning_start","late_morning_end",
            "late_night_start","late_night_end",
            ]
        return tuple(loaded_config.get(key) for key in keys)

        # birthday =  loaded_config.get('birthday', dict(month=6, day=14))

        # early_morning_start = loaded_config.get('early_morning_start')
        # early_morning_end = loaded_config.get('early_morning_end')
        
        # early_night_start = loaded_config.get('early_night_start')
        # early_night_end = loaded_config.get('early_night_end')

        # late_morning_start = loaded_config.get('late_morning_start')
        # late_morning_end = loaded_config.get('late_morning_end')
        
        # early_night_start = loaded_config.get('early_night_start')
        # early_night_end = loaded_config.get('early_night_end')


        # early_morning = loaded_config.get('early_morning', dict(start_hour=6, start_min=15, end_hour=6, end_min=45))
        # early_night = loaded_config.get('early_night', dict(start_hour=21, start_min=15, end_hour=21, end_min=45))
        # late_morning = loaded_config.get('late_morning', dict(start_hour=8, start_min=45, end_hour=9, end_min=15))
        # late_night = loaded_config.get('late_night', dict(start_hour=22, start_min=30, end_hour=23, end_min=0))

        
        # return birthday, early_morning, early_night, late_morning, late_night

if __name__ == "__main__":

    print(load_config_from_file())
