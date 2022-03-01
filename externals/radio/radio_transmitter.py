from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice
import config.config as config


# broadcast_all sends the passed message to all listening devices
def broadcast_all(message):
    xbee = XBeeDevice(config.port, config.rate)
    xbee.open()
    xbee.send_data_broadcast(message)
