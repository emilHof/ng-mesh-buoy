import asyncio
from inspect import iscoroutinefunction

import config.config as config
from interfaces.database import DBInterface
from interfaces.gps import GPSInterface, get_time_sync


class MessageHandler:
    def __init__(self, in_queue: asyncio.Queue, dep_queue: asyncio.Queue, gps=False):
        self.db = DBInterface()
        self.msg_handling = True
        self.hasGPS = gps
        self.in_queue = in_queue
        self.dep_queue = dep_queue
        self.function_dict = {
            "get_location": self.get_location,
            "get_time": self.get_time,
            "inc_block": self.handle_block
        }

        if gps:
            self.gps = GPSInterface()
        else:
            self.gps = None

        self.temp = None

    """ handle_message takes a message string that started with an @ and performs logic on it """

    def get_location(self):
        # check if there is a gps connected
        if self.hasGPS:
            location = self.gps.get_location()

            # add the return message to the departure queue
            self.dep_queue.put_nowait(("location: { " + location + " }", 0))

    def get_time(self):
        # put the time into the departure queue
        self.dep_queue.put_nowait(("utc time: " + get_time_sync().strftime("%H:%M:%S"), 0))

    def handle_bulk(self, cmd: str, debug: bool = False):
        if debug: print(f'handling bulk request: {cmd}')
        rows = self.get_bulk_data(cmd, debug=debug)  # get the data from the db

        # send back a leading packet indicating a packet block and its size, sleep for 1.5 sec between packets
        self.dep_queue.put_nowait((f'@inc_block', 2))

        for row in reversed(rows):  # send back all the rows in their separate packets
            self.dep_queue.put_nowait((row, .25))  # send back the row, sleep for .2 sec between packets
            if debug: print(f'row put in the dep_queue: {row}')

    """ get_bulk_data fetches a specific set of database data """

    def get_bulk_data(self, message, debug: bool = False):
        size = message.split("_")[0]  # find the index of the first length delimiter

        int_dict = {
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
        }

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
            n_i = msg[:2]

            if msg.startswith("@"):
                await self.handle_cmd(msg, debug=debug)
            else:
                self.dep_queue.put_nowait((msg, 0))

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
