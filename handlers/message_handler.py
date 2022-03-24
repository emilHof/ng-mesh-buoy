import config.config as config
from interfaces.database import DBInterface
from interfaces.radio import RadioInterface
import asyncio


async def propagate_message(xbee, gps) -> bool:
    message_handler = MessageHandler(xbee, gps)
    while True:
        message = await xbee.listen_async()
        if message.startswith("@"):
            err = message_handler.handle_message(message)
            if err is not None:
                print(err)
        elif message.startswith("&stop"):
            gps.log = False
            return True
        elif message.startswith("#size_"):
            message_handler.handle_block(message)
        else:
            print("message was not handled!")
            print(message)


class MessageHandler:
    def __init__(self, radio, gps):
        self.radio = RadioInterface()
        self.gps = gps
        self.db = DBInterface()

    def handle_message(self, message: str) -> str:
        return_message = ""
        if message.find("get_location") != -1:
            location = self.gps.get_location()
            return_message += " location: { " + location + " }"

        if message.find("get_time") != -1:
            time_utc = self.gps.get_time()
            return_message += " utc time: { " + time_utc + " }"

        if message.find("get_all_location") != -1:
            print("asked to get all locations")
            rows = self.db.read_loc_db()
            length = len(rows)
            self.radio.send_back("#size_"+str(length))
            for row in rows:
                self.radio.send_back(row[1]+row[2])

        if len(return_message) == 0:
            err = "no known commands found!"
            self.radio.send_back(err)
            return err

        if len(return_message) != 0:
            self.radio.send_back(return_message)

        return ""


    def handle_block(self, message):
        rows = []
        length = message[:6]
        length = int(length)
        for i in range (0, length):
            row = await self.radio.listen_async()
            rows.append(row)
        for row in rows:
            print(row)

