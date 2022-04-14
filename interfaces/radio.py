import digi.xbee.devices as devices
import config.config as config
import asyncio


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
