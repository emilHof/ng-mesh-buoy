import digi.xbee.devices as devices
import config.config as config


def make_radio():
    xbee = devices.XBeeDevice(config.port, config.rate)
    return xbee
