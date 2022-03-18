import digi.xbee.devices as devices
import config.config as config
import time
from types import MethodType
import asyncio


# listening listens for an incoming radio signal with a blocking loop and call to .read_data()
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


# listening listens for an incoming radio signal with a non-blocking loop and call to .read_data()
async def listening_async(xbee):
    print("listening...")
    data = xbee.read_data()
    message = data
    if message is not None:
        print("found a message")
        return message.data.decode("utf8")
    else:
        print("no message found")
        print("sleeping...")
        await asyncio.sleep(3)
        return xbee.listening()


class RadioInterface:
    """ __init__ is called on initialization of every new RadioInterface """

    def __init__(self):
        # gets the radio parameters from the config file
        # initializes them as attributes
        # creates a new xbee device as a RadioInterface attribute
        radio = config.config["radio"]
        self.port = radio["port"]
        self.rate = radio["rate"]
        self.xbee = devices.XBeeDevice(self.port, self.rate)
        self.xbee.open()
        # self.xbee.set_parameter("AP", 1, True)
        # self.xbee.write_changes()
        self.xbee.close()
        print("new radio made with", self.port, self.rate)

    """ print_settings lets you print out the parameters of your RadioInterface """

    def get_settings(self) -> tuple:
        return self.port, self.rate

    """"""

    def listen(self) -> str:
        xbee = self.xbee
        xbee.listening = MethodType(listening, xbee)
        xbee.open()
        message = xbee.listening()
        xbee.close()
        return message

    def send_back(self, message: str):
        xbee = self.xbee
        xbee.open()
        xbee.send_data_broadcast(message)
        xbee.close()

    def send_test_string(self, message: str):
        xbee = self.xbee
        xbee.open()
        xbee.send_data_broadcast(message)
        xbee.close()

    async def listen_async(self) -> str:
        xbee = self.xbee
        xbee.open()
        message = await self.listening_async()
        return message

    # listening listens for an incoming radio signal with a non-blocking loop and call to .read_data()
    async def listening_async(self):
        xbee = self.xbee
        print("listening...")
        data = xbee.read_data()
        message = data
        if message is not None:
            print("found a message")
            return message.data.decode("utf8")
        else:
            print("no message found")
            print("sleeping...")
            await asyncio.sleep(3)
            message = await self.listening_async()
            return message
