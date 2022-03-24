import config.config as config
from interfaces.radio import RadioInterface
from interfaces.gps import GPSInterface


def run_test():
    print(config.config)


radio_settings = {
    "port": "/dev/ttyUSB3",
    "rate": 9600,
}

gps_settings = {
    "port": "/dev/ttyUSB0",
    "rate": 9600,
}

db = {
    "file": "local_data.db"
}

config.set_config(radio_settings, gps_settings, db)
#
# xbee = RadioInterface()
#
# xbee.send_test_string("&stop")
# print("message sent!")
#
# message = xbee.listen()
# print(message)
#
# run_test()

gps = GPSInterface()

gps.print_basics()
