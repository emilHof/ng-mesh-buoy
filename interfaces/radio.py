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


async def listening_async_timed(xbee, sleep, tries):
    print("listening...")
    data = xbee.read_data()
    message = data

    while tries >= 0:
        if message is not None:
            print("found a message")
            return message.data.decode("utf8")
        else:
            tries -= 1
            await asyncio.sleep(sleep)
            return xbee.listening()

    return None


class RadioInterface:

    """ __init__ is called on initialization of every new RadioInterface """
    def __init__(self):
        radio = config.config["radio"]  # gets the radio parameters from the config file
        self.port, self.rate = radio["port"], radio["rate"]  # initializes them as attributes
        self.xbee = devices.XBeeDevice(self.port, self.rate)  # creates a new xbee device as a RadioInterface attribute

    """ print_settings returns a tuple with the parameters of your RadioInterface """
    def get_settings(self) -> tuple:
        return self.port, self.rate

    """ 
    a blocking loop that continues until the xbee receives a message
    returns a string
    """
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

    """ 
    listen_async opens the xbee connection and awaits listening_async until a message is received
    returns a string of data
     """
    async def listen_async(self) -> str:
        xbee = self.xbee
        xbee.open()
        message = await self.listening_async()
        xbee.close()
        return message

    async def listen_async_timed(self, sleep, tries) -> str:
        xbee = self.xbee
        xbee.open()
        message = await self.listening_async_limited(sleep, tries)
        xbee.close()
        return message

    """
    listening_async listens for an incoming radio signal with a non-blocking loop
    returns a string of the data 
    """
    async def listening_async(self) -> str:
        xbee = self.xbee

        message = xbee.read_data()
        print("listening")

        while message is None:
            print("no message found")
            await asyncio.sleep(3)
            message = xbee.read_data()

        print("message found")
        return message.data.decode("utf8")

    async def listening_async_limited(self, timeout, tries) -> str:
        xbee = self.xbee

        message = xbee.read_data()
        print("listening")

        while message is None:
            if tries < 1:
                return ""
            print("no message found")
            await asyncio.sleep(timeout)
            message = xbee.read_data()
            tries -= 1

        print("message found")
        return message.data.decode("utf8")

