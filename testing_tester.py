import config.config as config
from interfaces.radio import RadioInterface
# from interfaces.temp import TempInterface
from handlers.message_handler import MessageHandler
from interfaces.rfid import RFIDInterface
import asyncio


radio_settings = {
    "port": "/dev/ttyUSB2",
    "rate": 9600,
}

# gps_settings = {
#     "port": "/dev/ttyUSB4",
#     "rate": 9600,
# }

# config.set_config(radio_settings)

async def main():
    # config.set_specific("radio", "port", radio_settings["port"])
    # config.set_specific("radio", "rate", radio_settings["rate"])
    config.set_specific("db", "file", "local_data.db")

    config.set_specific("rfid", "port", "/dev/ttyACM0")
    config.set_specific("rfid", "rate", 9600)

    # xbee = RadioInterface()
    # msg_handler = MessageHandler()

    rfid = RFIDInterface()

    # xbee.send_test_string("@get_all_location")
    #
    # print("sent test string")

    # stopped = await asyncio.gather(msg_handler.propagate_message())
    stopped = await rfid.check_rfid()

    print(stopped)


if __name__ == "__main__":
    output = asyncio.run(main())
    print(output)
