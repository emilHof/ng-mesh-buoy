import digi.xbee.devices as devices
import config.config as config
import time
from types import MethodType


def listening(self):
    print("listening...")
    data = self.read_data()
    message = data
    if message is not None:
        print("found a message")
        return message.data.decode("utf8")
    else:
        print("no message found")
        print("sleeping...")
        time.sleep(3)
        return self.listening()


class RadioInterface:
    def __init__(self):
        radio = config.config["radio"]
        self.port = radio["port"]
        self.rate = radio["rate"]
        self.xbee = devices.XBeeDevice(self.port, self.rate)
        self.xbee.open()
        # self.xbee.set_parameter("AP", 1, True)
        # self.xbee.write_changes()
        self.xbee.close()
        print("new radio made with", self.port, self.rate)

    def print_settings(self):
        print(self.port, self.rate)


    # def listening(self):
    #     print("listening...")
    #     data = self.xbee.read_data()
    #     message = data
    #     if message is not None:
    #         print("found a message")
    #         return message.data.decode("utf8")
    #     else:
    #         print("no message found")
    #         print("sleeping...")
    #         time.sleep(3)
    #         return self.xbee.listening()

    def listen(self):
        # self.xbee.listening
        self.xbee.listening = MethodType(listening, self.xbee)
        self.xbee.open()
        message = self.xbee.listening()
        self.xbee.close()
        # self.send_back(message)
        return message

    def send_back(self, message):
        self.xbee.open()
        self.xbee.send_data_broadcast(message)
        self.xbee.close()

    def send_test_string(self, message):
        self.xbee.open()
        self.xbee.send_data_broadcast(message)
        self.xbee.close()
