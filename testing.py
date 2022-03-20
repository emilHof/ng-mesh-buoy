
import config.config as config
from interfaces.radio import RadioInterface
from interfaces.gps import GPSInterface


def run_test():
    print(config.config)


radio_settings = {
    "port": "/dev/ttyUSB2",
    "rate": 9600,
}

gps_settings = {
    "port": "/dev/ttyUSB4",
    "rate": 9600,
}
config.set_config(radio_settings, gps_settings)


gps = GPSInterface()

gps.print_basics()

run_test()
