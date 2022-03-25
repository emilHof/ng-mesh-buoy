import config.config as config
from interfaces.radio import RadioInterface


def run_test():
    print(config.config)


radio_settings = {
    "port": "/dev/ttyUSB3",
    "rate": 9600,
}

gps_settings = {
    "port": "/dev/ttyUSB4",
    "rate": 9600,
}
config.set_config(radio_settings, gps_settings)

xbee = RadioInterface()

xbee.send_test_string("@get_temp")
print("message sent!")

message = xbee.listen()
print(message)

run_test()