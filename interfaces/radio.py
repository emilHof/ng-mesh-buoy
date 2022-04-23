import asyncio
import json

import digi.xbee.devices as devices
import digi.xbee.exception

import config.config as config
from pkg.msgs.msg_types import SimpleMessage


def middle_of_hash(time: str) -> str:
    """ middle_of_hash returns the middle four characters of a hashed passed string """
    hashed_time = str(hash(time))
    return hashed_time[4:8]


class RadioInterface:
    """ __init__ is called on initialization of every new RadioInterface """

    def __init__(
            self, in_queue: asyncio.Queue,
            dep_queue: asyncio.Queue,
            close_chan: asyncio.Queue,
            debug: bool = False,
            test: bool = False
    ):
        if not test:
            radio = config.config["radio"]  # gets the radio parameters from the config file
            self.port, self.rate = radio["port"], radio["rate"]  # initializes them as attributes
            self.xbee = devices.XBeeDevice(self.port,
                                           self.rate)  # creates a new xbee device as a RadioInterface attribute
        self.in_queue = in_queue
        self.dep_queue = dep_queue
        self.close_chan = close_chan
        self.debug = debug
        if debug:
            print("xbee created!")

    def get_settings(self) -> tuple:
        """ get_settings returns a tuple with the parameters of your RadioInterface """
        return self.port, self.rate

    def __receive_callback(self, m):
        """ __receive_callback is registered to the xbee object and puts received messages in the in_queue """
        if self.debug: print(f'msg received: {m.data.decode("utf8")}')

        msg_decoded = json.loads(m.data.decode("utf8"))

        try:
            msg_obj = SimpleMessage(**msg_decoded)
            self.in_queue.put_nowait(msg_obj)
        except TypeError as error:
            print(f"packet body malformed! error:{error}")
            self.in_queue.put_nowait(SimpleMessage("00", f"packet body malformed! error:{error}", "4385"))

    def test_receive_callback(self, message: SimpleMessage):
        """ test_receive_callback is a function that allows for testing of the __receive_callback function """
        marshaled = json.dumps(message.__dict__, indent=4)
        packet = MockPacket(marshaled)

        self.__receive_callback(packet)

    async def radio_open(self):
        """
        radio_open opens the serial port connection with the xbee, registers a data_received_callback and waits for a
        message from the close_channel, after which it unregisters the callback and closes the port connection
        """
        self.xbee.open()

        self.xbee.add_data_received_callback(self.__receive_callback)

        await self.close_chan.get()

        self.xbee.del_data_received_callback(self.__receive_callback)

        self.xbee.close()

    async def sender(self):
        """
        sender is an asynchronous loop that listens to the RadioInterface's departure queue and sends any task it
        receives
        """

        while True:
            task = await self.dep_queue.get()

            time_hash = task.time_hash

            if len(time_hash) > 4:
                task.time_hash = middle_of_hash(time_hash)

            out_msg = self.__encode_packet(task)

            if self.debug: print(f'sent message: {out_msg}')

            try:
                self.xbee.send_data_broadcast(out_msg)  # broadcast the msg
            except digi.xbee.exception.TransmitException as error:
                print(error)

            self.dep_queue.task_done()  # mark the msg as sent

    def __encode_packet(self, message: SimpleMessage) -> str:
        """ __encode_packet takes a SimpleMessage object and returns a json string version of it """
        marshaled = json.dumps(message.__dict__, indent=4)

        return marshaled


class MockPacket:
    """ MockPacket is an object that mimics the packet returned by an xbee devices. it is used for testing purposes """
    def __init__(self, data: str):
        self.data = bytes(data, "utf-8")

    def decode(self, encoding: str) -> str:
        return str(self.data)
