# from digi.xbee.devices import XBeeDevice
# import time
# from types import MethodType
#
#
# def listen(self):
#     print("listening...")
#     data = self.read_data()
#     message = data
#     if message != None:
#         print("found a message")
#         return message.data.decode("utf8")
#     else:
#         print("no message found")
#         print("sleeping...")
#         time.sleep(3)
#         return self.listen()
#
#
# xbee = XBeeDevice("/dev/ttyUSB2", 9600)
# xbee.open()
# xbee.send_data_broadcast("hello world")
# xbee.listen = MethodType(listen, xbee)
# msg = xbee.listen()
# xbee.close()
#
# print(msg)

import config.config as config


def run_test():
    print(config.config)


radio_settings = {
    "port": "/dev/ttyUSB2",
    "rate": 9600,
}

gps_settings = {
    "port": "/dev/ttyUSB2",
    "rate": 9600,
}
config.set_config(radio_settings, gps_settings)

run_test()
