import config.config as config
from interfaces.radio import RadioInterface
from interfaces.gps import GPSInterface
from interfaces.database import DBInterface
from handlers.message_handler import propagate_message
import asyncio

radio_settings = {
    "port": "/dev/ttyUSB3",
    "rate": 9600,
}

gps_settings = {
    "port": "/dev/ttyUSB0",
    "rate": 9600,
}

db_setting = {
    "file": "local_data"
}


async def main():
    config.set_config(radio_settings, gps_settings, db_setting)
    xbee = RadioInterface()
    gps = GPSInterface()
    db = DBInterface()

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
