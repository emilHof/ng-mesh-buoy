import asyncio

from interfaces.database import DBInterface
from interfaces.radio import RadioInterface
from interfaces.gps import GPSInterface, get_time_sync
from interfaces.temp import TempInterface


class MessageHandler:
    def __init__(self, gps, radio):
        self.db = DBInterface()
        self.propagate = True
        self.hasGPS = gps

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
    async def handle_message(self, message: str) -> str:
        return_message = ""
        if message.find("get_location") != -1:
            self.gps = GPSInterface()
            location = self.gps.get_location()
            return_message += " location: { " + location + " }"

        if message.find("get_time") != -1:  # adds the time to the return message
            return_message += "utc time: " + get_time_sync().strftime("%H:%M:%S")

        if message.find("_get_bulk_") != -1:  # handles a call for bulk data
            rows = self.get_bulk_data(message)  # get the data from the db

            # send back a leading packet indicating a packet block and its size
            self.radio.send_back("#size_" + str(len(rows)))
            await asyncio.sleep(1.5)  # 1.5 sec sleep allows other node to receive leading packet

            for row in rows:  # send back all the rows in their separate packets
                self.radio.send_back(row)  # send back the row
                await asyncio.sleep(1)  # sleep for 1 sec between packets

        # if message.find("ping") != -1:
        #     print("found message:", message)
        #     print("sent message:", "pong")
        #     return_message = "@pong"
        #
        # if message.find("pong") != -1:
        #     print("found message:", message)
        #     print("sent message:", "ping")
        #     return_message = "@ping"

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

        # print("size:", size)
        # print(message)

        # find the tag of the bulk request (temp, loc,... )
        tag_index = message.index("_get_bulk_") - 4
        tag = message[tag_index:message.index("_get_bulk_")]

        # print(tag)

        # check the tag
        if tag == "temp":
            rows = self.db.read_temp_db(size)
        elif tag == "turb":
            rows = self.db.read_turb_db(size)
        elif tag == "loc":
            rows = self.db.read_temp_db(size)
        else:
            rows = self.db.read_loc_db(size)

        return_rows = []  # create a variable to hold the message strings

        for row in rows:
            return_rows.append(str(row[0]) + " " + row[1][:-4] + " " + row[0])

        return return_rows

    """ handle_block takes a block of related messages and stores them in an array """
    async def handle_block(self, message):

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
            row = await self.radio.listen_async_timed(sleep=.5, tries=10)

            if row == "":  # if too many messages are missed in a row the process is canceled
                fail_counter += 1
                if fail_counter > 5:
                    break

                continue

            rows.append(row)  # append row if data was received

        for row in rows:  # print the rows when all are finalized
            print(row)
        self.propagate = True

    """ propagate_message is a loop function that listens for incoming message """
    async def propagate_message(self):
        while True:
            while self.propagate:  # set self.propagate to false, to pause listening
                message = await self.radio.listen_async()

                if message.startswith("@"):
                    err = await self.handle_message(message)

                    if err is not None:
                        print(err)

                elif message.startswith("#size_"):
                    await self.handle_block(message)

                else:
                    print("message was not handled!")
                    print(message)

            await asyncio.sleep(10)
