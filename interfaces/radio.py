import digi.xbee.devices as devices
import config.config as config
import asyncio


def hash_time(time: str) -> str:
    hashed_time = str(hash(time))
    return hashed_time[4:8]


def add_time(out_msg: str, time: str) -> str:
    hashed_time = hash_time(time)
    return f'{out_msg},h:{hashed_time}'


class RadioInterface:
    """ __init__ is called on initialization of every new RadioInterface """

    def __init__(self, in_queue: asyncio.Queue, dep_queue: asyncio.Queue):
        radio = config.config["radio"]  # gets the radio parameters from the config file
        self.port, self.rate = radio["port"], radio["rate"]  # initializes them as attributes
        self.xbee = devices.XBeeDevice(self.port, self.rate)  # creates a new xbee device as a RadioInterface attribute
        print("xbee created!")
        self.in_queue = in_queue
        self.dep_queue = dep_queue

    """ print_settings returns a tuple with the parameters of your RadioInterface """

    def get_settings(self) -> tuple:
        return self.port, self.rate

    async def listen(self, sleep: int = .001, debug: bool = False):
        while True:
            xbee = self.xbee

            xbee.open()

            msg = xbee.read_data()

            if msg is not None:
                self.in_queue.put_nowait(msg.data.decode("utf8"))
                if debug: print(msg.data.decode("utf8"))

            xbee.close()

            await asyncio.sleep(sleep)

    async def send(self, debug: bool = False):
        xbee = self.xbee

        while True:
            task = await self.dep_queue.get()  # get task from the dep_queue

            out_msg, sleep_time, time = task[0], task[1], task[2]  # get the msg and sleep time from the task item

            if time is not None:
                out_msg = add_time(out_msg, time)

            if debug: print(f'sent message: {out_msg}')

            xbee.open()
            xbee.send_data_broadcast(out_msg)
            xbee.close()

            self.dep_queue.task_done()

            await asyncio.sleep(sleep_time)
