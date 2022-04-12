import asyncio
import time

import config.config as config
from interfaces.database import DBInterface
from interfaces.radio import RadioInterface
from interfaces.gps import GPSInterface, get_time_sync


def check_dep_queue():
    messages = []

    while len(config.config["dep_queue"]) > 0:
        messages.append(config.pop_dep_queue())

    return messages


class MessageHandler:
    def __init__(self, in_queue: asyncio.Queue, dep_queue: asyncio.Queue, gps=False, radio=False):
        self.db = DBInterface()
        self.propagate = True
        self.hasGPS = gps
        self.hasRadio = radio
        self.in_queue = in_queue
        self.dep_queue = dep_queue
        self.function_dict = {
            "get_location": self.get_location,
            "get_time": self.get_time,
        }

        if radio:
            self.radio = RadioInterface()
        else:
            self.radio = None

        if gps:
            self.gps = GPSInterface()
        else:
            self.gps = None

        self.temp = None

    def connect_radio(self):
        self.radio = RadioInterface()

    """ handle_message takes a message string that started with an @ and performs logic on it """

    def get_location(self):
        # check if there is a gps connected
        if self.hasGPS:
            location = self.gps.get_location()

            # add the return message to the departure queue
            self.dep_queue.put(("location: { " + location + " }", 0))

    def get_time(self):
        # put the time into the departure queue
        self.dep_queue.put(("utc time: " + get_time_sync().strftime("%H:%M:%S"), 0))

    def handle_bulk(self, cmd: str):
        rows = self.get_bulk_data(cmd)  # get the data from the db

        # send back a leading packet indicating a packet block and its size, sleep for 1.5 sec between packets
        self.dep_queue.put(("#size_" + str(len(rows)), 1.5))

        for row in reversed(rows):  # send back all the rows in their separate packets
            self.dep_queue.put((row, .2))  # send back the row, sleep for .2 sec between packets

    async def handle_message(self, message: str) -> str:
        return_message = ""
        if message.find("get_location") != -1:
            self.gps = GPSInterface()
            location = self.gps.get_location()
            return_message += "location: { " + location + " }"

        if message.find("get_time") != -1:  # adds the time to the return message
            return_message += "utc time: " + get_time_sync().strftime("%H:%M:%S")

        if message.find("_get_bulk_") != -1:  # handles a call for bulk data
            rows = self.get_bulk_data(message)  # get the data from the db

            # send back a leading packet indicating a packet block and its size
            self.radio.send_back("#size_" + str(len(rows)))
            time.sleep(1.5)  # 1.5 sec sleep allows other node to receive leading packet

            for row in reversed(rows):  # send back all the rows in their separate packets
                self.radio.send_back(row)  # send back the row
                time.sleep(.2)  # sleep for 1 sec between packets

        if len(return_message) == 0:
            err = "no known commands found!"
            self.radio.send_back(err)
            return err

        # if the message length is not 0 send back the message
        if len(return_message) != 0:
            self.radio.send_back(return_message)

        return ""

    """ get_bulk_data fetches a specific set of database data """

    def get_bulk_data(self, message):
        # find the index of the first length delimiter
        size_index = message.index("get_bulk_") + len("get_bulk_")
        size = ""

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

        # get the requested array size
        while message[size_index] in int_dict:
            print(size)
            size += message[size_index]
            size_index += 1
        size = int(size)

        # find the tag of the bulk request (temp, loc,... )
        tag_index = message.index("_get_bulk_") - 4
        tag = message[tag_index:message.index("_get_bulk_")]

        # print(tag)
        if tag == "loc":
            tag = "location_and_time"

        # check the tag
        rows = self.db.read_db(tag, size)

        return_rows = []  # create a variable to hold the message strings

        for row in rows:
            return_rows.append(str(row[0]) + " " + row[1] + " " + row[2])

        return return_rows

    """ handle_block takes a block of related messages and stores them in an array """

    async def handle_block(self, message, debug: bool) -> []:

        print("listening in block")

        # set the message propagation to false while the blocks are being handled
        self.propagate = False

        rows = []  # create an empty variable to store the received messages
        length = message[6:]  # size is always indicated at the end of the leading message
        length = int(length)
        if length > 50:  # if a block is larger than 50 read only 50 of the messages
            length = 50
        fail_counter = 0  # initialize a fail counter to track dropped messages

        for i in range(0, length):  # range over the rows
            # listen for the next row with a sleep break of .5 sec with 10 tries permitted
            row = await self.radio.listen_async_timed(sleep=.1, tries=10)

            if row == "":  # if too many messages are missed in a row the process is canceled
                fail_counter += 1
                if fail_counter > 5:
                    break

                continue

            rows.append(row)  # append row if data was received

        # if debug:
        #     for row in rows:  # print the rows when all are finalized
        #         print(row)

        self.propagate = True

        return rows

    """ propagate_message is a loop function that listens for incoming message """

    async def propagate_message(self, debug: bool):
        while True:
            while self.propagate:  # set self.propagate to false, to pause listening

                rows = check_dep_queue()  # first check if there is any new entries to the departure queue
                for row in rows:
                    self.radio.send_back(row)

                message = await self.radio.listen_async_timed(sleep=1, tries=5)  # listen for new messages

                if message != "":  # check if a message was received
                    if message.startswith("@"):  # if a message starts with an @ it is a command
                        err = await self.handle_message(message)
                        if err is not None:
                            print(err)
                    elif message.startswith("#size_"):  # if a message starts with a #size_ it is an incoming block
                        rows = await self.handle_block(message, debug)
                        if debug:
                            return rows
                    else:
                        print("message was not handled!")
                        print(message)

            await asyncio.sleep(10)

    async def handle_msg(self):
        while True:

            msg = await self.in_queue.get()

            if msg.startswith("@"):
                self.handle_cmd(msg)

    def handle_cmd(self, msg: str):

        cmd = msg.split("@")[1]

        if cmd in self.function_dict:
            function = self.function_dict[cmd]
            function()

        elif cmd.index("_get_bulk_") != 1:
            self.handle_bulk(cmd)
