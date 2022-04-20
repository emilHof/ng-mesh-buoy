import digi.xbee.devices as devices
import digi.xbee.exception

import config.config as config
import asyncio


def middle_of_hash(time: str) -> str:
    """ middle_of_hash returns the middle four characters of a hashed passed string """
    hashed_time = str(hash(time))
    return hashed_time[4:8]


def add_hash(out_msg: str, time: str) -> str:
    """ add_hash takes two strings, concatenating the second's hash to the first """
    hashed_time = middle_of_hash(time)
    return f'{out_msg},h:{hashed_time}'


class RadioInterface:
    """ __init__ is called on initialization of every new RadioInterface """

    def __init__(
            self, in_queue: asyncio.Queue,
            dep_queue: asyncio.Queue,
            close_chan: asyncio.Queue,
            debug: bool = False
    ):
        radio = config.config["radio"]  # gets the radio parameters from the config file
        self.port, self.rate = radio["port"], radio["rate"]  # initializes them as attributes
        self.xbee = devices.XBeeDevice(self.port, self.rate)  # creates a new xbee device as a RadioInterface attribute
        self.in_queue = in_queue
        self.dep_queue = dep_queue
        self.close_chan = close_chan
        if debug:
            print("xbee created!")

    """ get_settings returns a tuple with the parameters of your RadioInterface """

    def get_settings(self) -> tuple:
        return self.port, self.rate

    async def listen(self, sleep: int = .01, debug: bool = False):
        """ listen sets the radio to listen in an infinite, asynchronous loop, adding received messages to a queue """
        while True:
            xbee = self.xbee

            xbee.open()

            msg = xbee.read_data()  # read the data if there is any

            if msg is not None:  # check if data was received
                self.in_queue.put_nowait(msg.data.decode("utf8"))  # put message in the queue if data was received
                if debug: print(msg.data.decode("utf8"))

            xbee.close()

            await asyncio.sleep(sleep)

    async def send(self, debug: bool = False):
        """ send is an async loop that takes items from a departure queue and sends them via the xbee radio """
        xbee = self.xbee

        while True:
            task = await self.dep_queue.get()  # get task from the dep_queue

            out_msg, sleep_time, time = task[0], task[1], task[2]  # get the msg and sleep time from the task item

            if time is not None:  # check if there was any time passed with the msg
                out_msg = add_hash(out_msg, time)

            if debug: print(f'sent message: {out_msg}')

            xbee.open()
            xbee.send_data_broadcast(out_msg)  # broadcast the msg
            xbee.close()

            self.dep_queue.task_done()  # mark the msg as sent

            await asyncio.sleep(sleep_time)  # sleep for the indicated time

    def __send_callback(self, msg):
        self.in_queue.put_nowait(msg.data.decode("utf8"))

    def __register_callback(self):
        self.xbee.add_data_received_callback(self.__send_callback)

    def __deregister_callback(self):
        self.xbee.del_data_received_callback(self.__send_callback)

    async def radio_open(self):
        self.xbee.open()

        self.__register_callback()

        await self.close_chan.get()

        self.__deregister_callback()

        self.xbee.close()

    async def sender(self, debug: bool = False):

        while True:
            task = await self.dep_queue.get()  # get task from the dep_queue

            out_msg, sleep_time, time = task[0], task[1], task[2]  # get the msg and sleep time from the task item

            if time is not None:  # check if there was any time passed with the msg
                out_msg = add_hash(out_msg, time)

            if debug: print(f'sent message: {out_msg}')

            try:
                self.xbee.send_data_broadcast(out_msg)  # broadcast the msg
            except digi.xbee.exception.TransmitException as error:
                print(error)

            self.dep_queue.task_done()  # mark the msg as sent

            await asyncio.sleep(sleep_time)  # sleep for the indicated time
