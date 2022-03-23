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


async def main():
    config.set_config(radio_settings, gps_settings)
    config.set_specific("db", "file", "gps.db")
    xbee = RadioInterface()
    gps = GPSInterface()
    db = DBHandler()

    gps.setup_gps()

    stopped = await asyncio.gather(propagate_message(xbee, gps), gps.log_location_and_time())

    print(stopped)

    if stopped[0]:
        print("hey")
        rows = db.read_loc_db()
        for row in rows:
            print(row)

    return "all async loops exited"

if __name__ == "__main__":
    output = asyncio.run(main())
    print(output)
