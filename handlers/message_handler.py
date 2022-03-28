import asyncio

from interfaces.database import DBInterface
from interfaces.radio import RadioInterface
from interfaces.gps import GPSInterface
from interfaces.temp import TempInterface


# async def propagate_message(xbee, gps) -> bool:
#     message_handler = MessageHandler()
#     while True:
#         message = await xbee.listen_async()
#         if message.startswith("@"):
#             err = message_handler.handle_message(message)
#             if err is not None:
#                 print(err)
#         elif message.startswith("&stop"):
#             gps.log = False
#             return True
#         elif message.startswith("#size_"):
#             await message_handler.handle_block(message)
#         else:
#             print("message was not handled!")
#             print(message)


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

        if message.find("get_all_temp") != -1:
            rows = self.db.read_temp_db()
            length = len(rows)
            print(length)
            self.radio.send_back("#size_" + str(length))
            for row in rows:
                print("sent row of", row[1])
                self.radio.send_back(row[1])

        if message.find("ping") != -1:
            self.radio.send_back("pong")

        if message.find("pong") != -1:
            print("found message:", message)
            print("sent message:", "ping")
            self.radio.send_back("ping")

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
