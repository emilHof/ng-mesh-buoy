config = {
    "radio": {
        "port": None,
        "rate": None,
    },
    "gps": {
        "port": None,
        "rate": None,
    },
    "db": {
        "file": None,
    }

}


def set_config(radio_dict, gps_dict):
    radio = config["radio"]
    gps = config["gps"]
    radio["port"] = radio_dict["port"]
    radio["rate"] = radio_dict["rate"]
    gps["port"] = gps_dict["port"]
    gps["rate"] = gps_dict["rate"]


def set_specific(target, target_setting, value):
    config[target][target_setting] = value
