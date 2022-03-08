from digi.xbee.devices import XBeeDevice
import config.config as config
from types import MethodType
import handlers.mesh as mesh
import time
import externals.radio.radio_maker as radio_maker


def listen(self):
    print("listening...")
    data = self.read_data()
    message = data
    if message != None:
        print("found a message")
        return message.data.decode("utf8")
    else:
        print("no message found")
        print("sleeping...")
        time.sleep(3)
        return self.listen()


def open_receiver():
    xbee = radio_maker.make_radio()
    # xbee = XBeeDevice(config.port, config.rate)
    xbee.listen = MethodType(listen, xbee)
    xbee.open()
    message = xbee.listen()
    xbee.close()
    mesh.mesh_to_all(message)
