import asyncio

import config.config as config
from interfaces.rfid import RFIDInterface
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

    rfid = RFIDInterface(gps=True)
    msg_handler = MessageHandler(gps=True, radio=True)

    # set up an asynchronous loop to propagate messages and listen for rfid signals
    await asyncio.gather(
        msg_handler.propagate_message(False),
        rfid.check_rfid("turb"),
    )

    return "all async loops exited"


if __name__ == "__main__":
    output = asyncio.run(main())
    print(output)
