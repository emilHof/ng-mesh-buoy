import asyncio
import datetime
from inspect import iscoroutinefunction

from config.config import config
from interfaces.database import DBInterface
from interfaces.gps import GPSInterface, get_time_sync
from pkg.msgs.msg_types import SimpleMessage


class MessageHandler:
    def __init__(self, in_queue: asyncio.Queue, dep_queue: asyncio.Queue, print_queue: asyncio.Queue = None, db=None,
                 gps=False):
        if db is not None:
            self.db = db
        else:
            self.db = DBInterface(dep_queue=dep_queue)
        self.msg_handling = True
        self.hasGPS = gps
        self.ni = config["NI"]["ni"]
        self.msg_cache = {}
        self.in_queue = in_queue
        self.dep_queue = dep_queue
        self.print_queue = print_queue
        self.function_dict = {
            "get_location": self.__get_location,
            "get_time": self.__send_time,
            "inc_block": self.__handle_block
        }

        if gps:
            self.gps = GPSInterface()
        else:
            self.gps = None

        self.temp = None

    """ handle_message takes a message string that started with an @ and performs logic on it """

    def __get_time(self):
        """ get_time reads the local time, either from the gps or the internal clock """
        if self.hasGPS:  # check if there is a gps connected
            return get_time_sync().strftime("%H:%M:%S")
        else:
            return datetime.datetime.now().strftime("%H:%M:%S")

    def __get_location(self):
        """ get_location reads the location from the gps if a gps is connected """
        # check if there is a gps connected
        if self.hasGPS:
            location = self.gps.get_location()
            time = self.__get_time()
            # add the return message to the departure queue
            packet = SimpleMessage("00", f"location: {location}", time)
            self.dep_queue.put_nowait(packet)

    def __send_time(self):
        """ send_time puts the local time in the dep_queue """
        # put the time into the departure queue
        time = self.__get_time()
        packet = SimpleMessage("00", f't:00,utc time: {time}', time)
        self.dep_queue.put_nowait(packet)

    def __handle_bulk(self, cmd: str, debug: bool = False):
        """ handle_bulk is triggered when a request for bulk data is received """
        if debug: print(f'handling bulk request: {cmd}')
        rows = self.__get_bulk_data(cmd, debug=debug)  # get the data from the db

        if self.hasGPS:
            time = get_time_sync()
        else:
            time = datetime.datetime.now().strftime("%H:%M:%S")

        self.db.check_for_entry = False

        # send back a leading packet indicating a packet block and its size, sleep for 1.5 sec between packets
        lead_packet = SimpleMessage("00", "@inc_block", time)
        self.dep_queue.put_nowait(lead_packet)

        for row in reversed(rows):  # send back all the rows in their separate packets
            row_packet = SimpleMessage("00", row, time)
            self.dep_queue.put_nowait(row_packet)  # send back the row, sleep for .2 sec between packets
            if debug: print(f'row put in the dep_queue: {row}')

        self.db.check_for_entry = True

    def __get_bulk_data(self, message, debug: bool = False):
        """ __get_bulk_data parses a message to fetch data entries from the database """
        try:
            size = message.split("_")[0]  # find the index of the first length delimiter
        except IndexError:
            print(IndexError)
            return

        try:
            size = int(size)
            if debug: print(f'size: {size}')
        except (ValueError, TypeError) as error:
            print(error)
            return

        # find the tag of the bulk request (temp, loc,... )
        try:
            tag = message.split("_")[3]
            if debug: print(f'tag: {tag}')
        except (ValueError, IndexError, TypeError) as error:
            print(error)
            return

        if tag == "loc":
            tag = "loca"

        # check the tag
        rows, error = self.db.read_db(tag, size, debug=debug)

        if error is not None:  # check for a db error
            print(error)
            return []

        return_rows = []  # create a variable to hold the message strings

        for row in rows:
            return_rows.append(str(row[0]) + " " + row[1] + " " + row[2])

        return return_rows

    async def __handle_block(self, debug: bool = False) -> []:
        """ __handle_block takes a block of related messages and stores them in an array """
        if debug: print("listening in block")

        # set the message propagation to false while the blocks are being handled
        self.msg_handling = False

        rows = []  # create an empty variable to store the received messages

        fail_counter = 0  # initialize a fail counter to track dropped messages

        while fail_counter < 2:  # range over the rows
            try:
                row_packet: SimpleMessage = await asyncio.wait_for(self.in_queue.get(), timeout=2)
            except asyncio.TimeoutError:
                fail_counter += 1
                continue

            if row_packet.ni == self.ni:
                row = row_packet.msg
            else:
                self.in_queue.task_done()
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
        """ handle_msg is an async loop that reads from the input queue and handles the incoming messages """
        while True and self.msg_handling:

            msg_obj: SimpleMessage = await self.in_queue.get()  # wait for a message to be put into the queue

            if debug: print(f'handling message: {msg_obj.msg}')

            if msg_obj not in self.msg_cache:  # check if a message has been received before
                self.msg_cache[msg_obj] = 1  # if not add current message to the cache and handle the message

                inc_ni = msg_obj.ni  # get the target node id of the incoming message

                if inc_ni == self.ni:  # if the target node is this node, handle the message

                    msg = msg_obj.msg

                    if msg.startswith("@"):  # handle as ui if it is a command
                        await self.__handle_cmd(msg, debug=debug)
                    elif self.print_queue is not None:  # otherwise, print the message to the screen
                        self.print_queue.put_nowait(msg)

                else:  # if the target node is not this node, forward the message
                    self.dep_queue.put_nowait(msg_obj)

            self.in_queue.task_done()

    async def __handle_cmd(self, msg: str, debug: bool = False):

        cmd = msg.split("@")[1]

        if debug: print(f't he command is: {cmd}')

        try:
            if not await self.__find_func(cmd):
                if cmd.index("_get_bulk_") != -1:
                    if debug: print(f'the command is being handled as a bulk request')
                    self.__handle_bulk(cmd, debug=debug)

        except (IndexError, ValueError) as error:
            print(error)

    async def __find_func(self, func: str) -> bool:
        if func in self.function_dict:
            func = self.function_dict[func]

            if iscoroutinefunction(func):
                await func()

            else:
                func()
            return True
        return False
