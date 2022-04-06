config = {
    "radio": {
        "port": None,
        "rate": None,
    },
    "gps": {
        "port": None,
        "rate": None,
    },
    "rfid": {
        "port": None,
        "rate": None,
    },
    "temp": {
        "port": None,
        "rate": None,
    },
    "db": {
        "file": None,
    },
    "time": {
        "time_stamp": None,
        "time_last": None
    }

}


def set_config(radio_dict, gps_dict, db_dict):
    radio = config["radio"]
    gps = config["gps"]
    db = config["db"]
    radio["port"] = radio_dict["port"]
    radio["rate"] = radio_dict["rate"]
    gps["port"] = gps_dict["port"]
    gps["rate"] = gps_dict["rate"]
    db["file"] = db_dict["file"]


def set_specific(target, target_setting, value):
    config[target][target_setting] = value
