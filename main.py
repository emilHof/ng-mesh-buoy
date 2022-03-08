# import externals.radio.radio_receiver as radio_receiver
#
# radio_receiver.open_receiver()

import config.config as config
from interfaces.radio import RadioInterface
from interfaces.gps import GPSInterface
from handlers.message_handler import MessageHandler

radio_settings = {
    "port": "/dev/ttyUSB2",
    "rate": 9600,
}

gps_settings = {
    "port": "/dev/ttyUSB4",
    "rate": 9600,
}
config.set_config(radio_settings, gps_settings)

xbee = RadioInterface()
gps = GPSInterface()
message_handler = MessageHandler(xbee, gps)

xbee.print_settings()
# gps.print_settings()
# gps.print_basics()

message = xbee.listen()
if message.startswith("@"):
    err = message_handler.handle_message(message)
    if err is not None:
        print(err)
else:
    print("message was not handled!")
    location = gps.get_location()
    print("location:", location)
    print("message:", message)
    xbee.send_back(message + location)


