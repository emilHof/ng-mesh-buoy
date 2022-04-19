import asyncio
import datetime
from inspect import iscoroutinefunction

from config.config import config
from interfaces.database import DBInterface
from interfaces.gps import GPSInterface, get_time_sync


class MessageHandler:
    def __init__(self, in_queue: asyncio.Queue, dep_queue: asyncio.Queue, print_queue: asyncio.Queue = None, gps=False):
        self.db = DBInterface(dep_queue=dep_queue)
        self.msg_handling = True
        self.hasGPS = gps
        self.ni = config["NI"]["ni"]
        self.msg_cache = {}
        self.in_queue = in_queue
        self.dep_queue = dep_queue
        self.print_queue = print_queue
        self.function_dict = {
            "get_location": self.get_location,
            "get_time": self.send_time,
            "inc_block": self.handle_block
        }

        if gps:
            self.gps = GPSInterface()
        else:
            self.gps = None

        self.temp = None

    """ handle_message takes a message string that started with an @ and performs logic on it """

    def get_time(self):
        if self.hasGPS:  # check if there is a gps connected
            return get_time_sync().strftime("%H:%M:%S")
        else:
            return datetime.datetime.now().strftime("%H:%M:%S")

    def get_location(self):
        # check if there is a gps connected
        if self.hasGPS:
            location = self.gps.get_location()

            # add the return message to the departure queue
            self.dep_queue.put_nowait(("location: { " + location + " }", 0))

    def send_time(self):
        # put the time into the departure queue
        time = self.get_time()
        self.dep_queue.put_nowait((f't:01,utc time: {time}', 0, time))

    def handle_bulk(self, cmd: str, debug: bool = False):
        if debug: print(f'handling bulk request: {cmd}')
        rows = self.get_bulk_data(cmd, debug=debug)  # get the data from the db

        if self.hasGPS:
            time = get_time_sync()
        else:
            time = datetime.datetime.now().strftime("%H:%M:%S")

        # send back a leading packet indicating a packet block and its size, sleep for 1.5 sec between packets
        self.dep_queue.put_nowait((f't:01,@inc_block', 2, time))

        for row in reversed(rows):  # send back all the rows in their separate packets
            self.dep_queue.put_nowait((row, .25, time))  # send back the row, sleep for .2 sec between packets
            if debug: print(f'row put in the dep_queue: {row}')

    """ get_bulk_data fetches a specific set of database data """

    def get_bulk_data(self, message, debug: bool = False):
        size = message.split("_")[0]  # find the index of the first length delimiter

        size = int(size)
        if debug: print(f'size: {size}')

        # find the tag of the bulk request (temp, loc,... )
        tag = message.split("_")[3]
        if debug: print(f'tag: {tag}')

        if tag == "loc":
            tag = "location_and_time"

        # check the tag
        rows = self.db.read_db(tag, size, debug=debug)

        return_rows = []  # create a variable to hold the message strings

        for row in rows:
            return_rows.append(str(row[0]) + " " + row[1] + " " + row[2])

        return return_rows

    """ handle_block takes a block of related messages and stores them in an array """

    async def handle_block(self, debug: bool = False) -> []:

        if debug: print("listening in block")

        # set the message propagation to false while the blocks are being handled
        self.msg_handling = False

        rows = []  # create an empty variable to store the received messages

        fail_counter = 0  # initialize a fail counter to track dropped messages

        while fail_counter < 2:  # range over the rows
            try:
                row = await asyncio.wait_for(self.in_queue.get(), timeout=2)
            except asyncio.TimeoutError:
                fail_counter += 1
                continue

            if debug: print(f'row: {row}')

            if self.print_queue is not None:
                self.print_queue.put_nowait(row)

            if type(row) is not str:  # if too many messages are missed in a row the process is canceled
                fail_counter += 1

                print(f'not string {type(row)}')
                continue

            rows.append(row)  # append row if data was received
            self.in_queue.task_done()

        if debug:
            for row in rows:  # print the rows when all are finalized
                print(row)

        self.msg_handling = True
        return rows

    async def handle_msg(self, debug: bool = False):
        while True and self.msg_handling:

            msg = await self.in_queue.get()

            if debug: print(f'handling message: {msg}')
            inc_ni = msg[2:4]

            if msg not in self.msg_cache:  # check if a message has been received before
                self.msg_cache[msg] = 1  # if not add current message to the cache and handle the message

                if inc_ni == self.ni:  # if the target node is this node, handle the message
                    msg = msg[5:-7]
                    if msg.startswith("@"):  # handle as ui if it is a command
                        await self.handle_cmd(msg, debug=debug)
                    elif self.print_queue is not None:  # otherwise, print the message to the screen
                        self.print_queue.put_nowait(msg)
                else:  # if the target node is not this node, forward the message
                    self.dep_queue.put_nowait((msg, 0, None))

            self.in_queue.task_done()

    async def handle_cmd(self, msg: str, debug: bool = False):

        cmd = msg.split("@")[1]

        if debug: print(f'the command is: {cmd}')

        if cmd in self.function_dict:
            function = self.function_dict[cmd]

            if iscoroutinefunction(function):
                await function(debug)

            else:
                function()

        elif cmd.index("_get_bulk_") != -1:
            if debug: print(f'the command is being handled as a bulk request')
            self.handle_bulk(cmd, debug=debug)
