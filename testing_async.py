import config.config as config
from interfaces.radio import RadioInterface
from interfaces.gps import GPSInterface
from interfaces.database import DBInterface
from handlers.message_handler import MessageHandler
from interfaces.rfid import RFIDInterface
import asyncio

radio_settings = {
    "port": "/dev/ttyUSB3",
    "rate": 9600,
}

gps_settings = {
    "port": "/dev/ttyUSB0",
    "rate": 9600,
}

temp_settings = {
    "port": "/dev/ttyACM0",
    "rate": 9600,
}

db_setting = {
    "file": "local_data.db"
}


async def main():
    config.set_specific("radio", "port", "/dev/ttyUSB2")
    config.set_specific("radio", "rate", 9600)
    config.set_specific("rfid", "port", "/dev/ttyACM0")
    config.set_specific("rfid", "rate", 9600)
    config.set_specific("db", "file", "local_data.db")

    xbee = RadioInterface()
    xbee.send_test_string("xbee online")

    msg_handler = MessageHandler()

    rfid = RFIDInterface()


    # xbee.send_test_string("@get_all_temp")

    stopped = await asyncio.gather(msg_handler.propagate_message(), rfid.check_rfid())

    # stopped = await msg_handler.propagate_message()

    print(stopped)

    return "all async loops exited"


if __name__ == "__main__":
    output = asyncio.run(main())
    print(output)
