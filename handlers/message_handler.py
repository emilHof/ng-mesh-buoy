import asyncio

from interfaces.database import DBInterface
from interfaces.radio import RadioInterface
from interfaces.gps import GPSInterface, get_time_sync
from interfaces.temp import TempInterface


class MessageHandler:
    def __init__(self):
        self.radio = None
        self.db = DBInterface()
        self.propagate = True
        self.gps = None
        self.temp = None

    def connect_radio(self):
        self.radio = RadioInterface()

    async def handle_message(self, message: str) -> str:
        return_message = ""
        if message.find("get_location") != -1:
            self.gps = GPSInterface()
            location = self.gps.get_location()
            return_message += " location: { " + location + " }"

        if message.find("get_time") != -1:

            return_message += "utc time: " + get_time_sync().strftime("%H:%M:%S")

        if message.find("_get_bulk_") != -1:

            rows = self.get_bulk_data(message)

            self.radio.send_back("#size_" + str(len(rows)))
            await asyncio.sleep(1.5)
            for row in rows:
                self.radio.send_back(row)
                await asyncio.sleep(1.5)

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

        if len(return_message) != 0:
            self.radio.send_back(return_message)

        return ""

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

        print("size:", size)

        print(message)
        # find the tag of the bulk request (temp, loc,... )
        tag_index = message.index("_get_bulk_") - 4
        tag = message[tag_index:message.index("_get_bulk_")]

        print(tag)
        # check the tag
        if tag == "temp":
            rows = self.db.read_temp_db(size)
        elif tag == "turb":
            rows = self.db.read_turb_db(size)
        elif tag == "loc":
            rows = self.db.read_temp_db(size)
        else:
            rows = self.db.read_loc_db(size)

        return_rows = []

        for row in rows:
            return_rows.append(str(row[0]) + " " + str(int(row[1][:-4])))

        return return_rows

    async def handle_block(self, message):

        print("listening in block")

        self.propagate = False
        rows = []
        length = message[6:]
        length = int(length)
        if length > 50:
            length = 50
        fail_counter = 0

        for i in range(0, length):  # range over the rows
            row = await self.radio.listen_async_timed(1, 10)

            if row == "":  # if too many messages are missed in a row the process is canceled
                # print("failed to find message", fail_counter)
                fail_counter += 1
                if fail_counter > 5:
                    break

                continue

            rows.append(row)  # append row if data was received

        for row in rows:  # print the rows when all are finalized
            print(row)
        self.propagate = True

    async def propagate_message(self) -> bool:
        while True:
            while self.propagate:
                message = await self.radio.listen_async()
                if message.startswith("@"):
                    err = await self.handle_message(message)
                    if err is not None:
                        print(err)
                elif message.startswith("&stop"):
                    self.gps.log = False
                    return True
                elif message.startswith("#size_"):
                    await self.handle_block(message)
                else:
                    print("message was not handled!")
                    print(message)
            await asyncio.sleep(10)
