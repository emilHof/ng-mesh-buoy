import asyncio

import config.config as config
from interfaces.rfid import RFIDInterface
from interfaces.radio import RadioInterface
from handlers.message_handler import MessageHandler

radio_settings = {
    "port": "/dev/ttyUSB3",
    "rate": 9600,
}

gps_settings = {
    "port": "/dev/ttyUSB0",
    "rate": 9600,
}

db_setting = {
    "file": "local_data.db"
}


async def main():
    config.set_config(radio_dict=radio_settings, gps_dict=gps_settings, db_dict=db_setting)
    config.set_specific("rfid", "port", "/dev/ttyACM0")
    config.set_specific("rfid", "rate", 9600)

    in_queue = asyncio.Queue()
    dep_queue = asyncio.Queue()

    radio = RadioInterface(in_queue, dep_queue)
    rfid = RFIDInterface(gps=True)
    msg_handler = MessageHandler(in_queue, dep_queue, gps=True, radio=True)

    # set up an asynchronous loop to propagate messages and listen for rfid signals
    await asyncio.gather(
        msg_handler.handle_msg(),
        radio.listen(),
        rfid.check_rfid("turb"),
    )

    return "all async loops exited"


if __name__ == "__main__":
    output = asyncio.run(main())
    print(output)
