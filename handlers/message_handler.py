import asyncio

from interfaces.database import DBInterface
from interfaces.radio import RadioInterface
from interfaces.gps import GPSInterface
from interfaces.temp import TempInterface

# def get_bulk_data:


class MessageHandler:
    def __init__(self):
        self.radio = RadioInterface()
        self.db = DBInterface()
        self.propagate = True
        self.gps = None
        self.temp = None

    def handle_message(self, message: str) -> str:
        return_message = ""
        if message.find("get_location") != -1:
            self.gps = GPSInterface()
            location = self.gps.get_location()
            return_message += " location: { " + location + " }"

        if message.find("get_time") != -1:
            self.gps = GPSInterface()
            time_utc = self.gps.get_time()
            return_message += " utc time: { " + time_utc + " }"

        if message.find("get_all_location") != -1:
            rows = self.db.read_loc_db()
            length = len(rows)
            print(length)
            self.radio.send_back("#size_" + str(length))
            for row in rows:
                print("sent row of" + row[1] + row[2])
                self.radio.send_back(row[1] + row[2])

        if message.find("get_temp") != -1:
            self.temp = TempInterface()
            result = self.temp.get_temp()
            self.radio.send_back(result)

        if message.find("get_bulk_temp") != -1:

            # find the index of the first length delimiter
            size_index = message.index("get_bulk_temp")+len("get_bulk_temp")
            size = ""

            while int(message[size_index]) >= 0:
                size += message[size_index]

            size = int(size)

            rows = self.db.read_temp_db(size)
            length = len(rows)
            print(length)
            self.radio.send_back("#size_" + str(length))
            for row in rows:
                print("sent row of", row[0], row[1], row[2])
                return_row = row[0] + " " + row[1] + " " + row[2]
                self.radio.send_back(return_row)

        if message.find("get_bulk_turb") != -1:

            # find the index of the first length delimiter
            size_index = message.index("get_bulk_turb") + len("get_bulk_turb")

            size = ""

            while message[size_index] != "_":
                size += message[size_index]
                size_index += 1

            print("size:", size)

            size = int(size)

            print("size:", type(size))

            rows = self.db.read_turb_db(size)
            length = len(rows)
            print(length)
            self.radio.send_back("#size_" + str(length))
            for row in rows:
                print("sent row of", row[0], row[1])
                return_row = str(row[0]) + " " + row[1]
                self.radio.send_back(return_row)
            return ""

        if message.find("ping") != -1:
            print("found message:", message)
            print("sent message:", "pong")
            return_message = "@pong"

        if message.find("pong") != -1:
            print("found message:", message)
            print("sent message:", "ping")
            return_message = "@ping"

        if len(return_message) == 0:
            err = "no known commands found!"
            self.radio.send_back(err)
            return err

        if len(return_message) != 0:
            self.radio.send_back(return_message)

        return ""

    async def handle_block(self, message):
        self.propagate = False
        rows = []
        length = message[6:]
        length = int(length)
        if length > 50:
            length = 50
        fail_counter = 0
        for i in range(0, length):
            row = await self.radio.listen_async_timed(1, 5)
            print(i, "found message:", row)
            if row == "":
                print("failed to find message", fail_counter)
                fail_counter += 1
                if fail_counter > 5:
                    break
            rows.append(row)
        for row in rows:
            print(row)
        self.propagate = True

    async def propagate_message(self) -> bool:
        while True:
            while self.propagate:
                message = await self.radio.listen_async()
                if message.startswith("@"):
                    err = self.handle_message(message)
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
