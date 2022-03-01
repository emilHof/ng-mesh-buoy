from digi.xbee.devices import XBeeDevice
xbee = XBeeDevice("/dev/ttyUSB2", 9600)

xbee.open()
xbee.send_data_broadcast("hello world")
xbee.close()
