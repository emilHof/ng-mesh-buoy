from digi.xbee.devices import XBeeDevice
import time



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


xbee = XBeeDevice("/dev/ttyUSB2", 9600)
xbee.open()
xbee.send_data_broadcast("hello world")

msg = xbee.listen()
xbee.close()


print(msg)
