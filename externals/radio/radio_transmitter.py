from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice
import config.config as config
import configparser

# config_obj = configparser.ConfigParser()
# config_obj.read("../config/config.ini")
# radio = config_obj["radio"]


# broadcast_all sends the passed message to all listening devices
def broadcast_all(message):
    # port = radio["port"]
    # rate = radio["rate"]
    xbee = XBeeDevice(config.port, config.rate)
    xbee.open()
    xbee.send_data_broadcast(message)
