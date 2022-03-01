from digi.xbee.devices import XBeeDevice
import config.config as config
from types import MethodType
import handlers.mesh as mesh
import time
# import radio_maker as radio_maker


def listen(self):
    print("listening...")
    data = self.read_data()
    message = data
    if message != None:
        print("found a message")
        return message.data.decode
    else:
        print("no message found")
        print("sleeping...")
        time.sleep(3)
        return self.listen()

# def message_received(self, message):
#     message_body = message.data.decode("utf8")
#     self.close()
#     mesh.mesh_to_all(message_body)
#     print("received a message!")


def open_receiver():
    # xbee = radio_maker.make_radio()
    xbee = XBeeDevice(config.port, config.rate)
    xbee.listen = MethodType(listen, xbee)
    xbee.open()
    message = xbee.listen()
    xbee.close()
    # xbee.add_data_received_callback(message_received)
    mesh.mesh_to_all(message)

