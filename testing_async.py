import config.config as config
from interfaces.radio import RadioInterface
from interfaces.gps import GPSInterface
from interfaces.database import DBHandler
from handlers.message_handler import MessageHandler
import asyncio

radio_settings = {
    "port": "/dev/ttyUSB2",
    "rate": 9600,
}

gps_settings = {
    "port": "/dev/ttyUSB4",
    "rate": 9600,
}


async def propagate_message(xbee, gps) -> str:
    message_handler = MessageHandler(xbee, gps)
    while True:
        message = await xbee.listen_async()
        if message.startswith("@"):
            err = message_handler.handle_message(message)
            if err is not None:
                print(err)
        elif message.startswith("&stop"):
            return "program exited"
        else:
            print("message was not handled!")
            print(message)


async def main():
    config.set_config(radio_settings, gps_settings)
    xbee = RadioInterface()
    gps = GPSInterface()
    db = DBHandler()

    stopped = await asyncio.gather(propagate_message(xbee, gps), gps.log_location_and_time())

    if stopped == "program exited":
        rows = db.read_loc_db()
        for row in rows:
            print(row)

    return "all async loops exited"

if __name__ == "__main__":
    output = asyncio.run(main())
    print(output)
