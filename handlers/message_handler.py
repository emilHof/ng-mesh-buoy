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
        else:
            print("message was not handled!")
            print(message)


class MessageHandler:
    def __init__(self, radio, gps):
        self.radio = radio
        self.gps = gps

    def handle_message(self, message: str) -> str:
        return_message = ""
        if message.find("get_location") != -1:
            location = self.gps.get_location()
            return_message += " location: { " + location + " }"

        if message.find("get_time") != -1:
            time_utc = self.gps.get_time()
            return_message += " utc time: { " + time_utc + " }"
        if len(return_message) == 0:
            err = "no known commands found!"
            self.radio.send_back(err)
            return err

        self.radio.send_back(return_message)
