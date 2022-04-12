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
    def __init__(self, in_queue: asyncio.Queue, dep_queue: asyncio.Queue):
        radio = config.config["radio"]  # gets the radio parameters from the config file
        self.port, self.rate = radio["port"], radio["rate"]  # initializes them as attributes
        self.xbee = devices.XBeeDevice(self.port, self.rate)  # creates a new xbee device as a RadioInterface attribute
        self.in_queue = in_queue
        self.dep_queue = dep_queue

    """ print_settings returns a tuple with the parameters of your RadioInterface """
    def get_settings(self) -> tuple:
        return self.port, self.rate

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

    async def listen(self, sleep: int = 1):
        while True:
            xbee = self.xbee

            xbee.open()

            msg = xbee.read_data()

            if msg is not None:
                self.in_queue.put_nowait(msg.data.decode("utf8"))

            xbee.close()

            await asyncio.sleep(sleep)

    async def send(self):
        xbee = self.xbee

        while True:
            task = await self.dep_queue.get()  # get task from the dep_queue

            out_msg, sleep_time = task[0], task[1]  # get the msg and sleep time from the task item

            xbee.open()
            xbee.send_data_broadcast(out_msg)
            xbee.close()

            self.dep_queue.task_done()

            await asyncio.sleep(sleep_time)
