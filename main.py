# import externals.radio.radio_receiver as radio_receiver
#
# radio_receiver.open_receiver()

import config.config as config
from interfaces.radio import RadioInterface
from interfaces.gps import GPSInterface

radio_settings = {
    "port": "/dev/ttyUSB2",
    "rate": 9600,
}

gps_settings = {
    "port": "/dev/ttyUSB3",
    "rate": 9600,
}
config.set_config(radio_settings, gps_settings)

xbee = RadioInterface()
gps = GPSInterface("gps")

xbee.print_settings()
xbee.make_radio()
# gps.print_settings()
# gps.print_basics()

xbee.listen()
