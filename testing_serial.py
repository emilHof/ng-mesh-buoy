import serial
import config.config as config
from interfaces.radio import RadioInterface
from interfaces.gps import GPSInterface
from interfaces.database import DBInterface
from interfaces.rfid import RFIDInterface
from handlers.message_handler import MessageHandler
import asyncio

s = serial.Serial('/dev/ttyACM0', 9600)


# def test_serial():
#     """
#     read a line and print.
#     """
#     text = ""
#     msg = s.read().decode()
#     while msg != '\n':
#         text += msg
#         msg = s.read().decode()
#     print(text)
#     loop.call_soon(s.write, "ok\n".encode())
#
#
# loop = asyncio.get_event_loop()
# loop.add_reader(s, test_serial)
# try:
#     loop.run_forever()
# except KeyboardInterrupt:
#     pass
# finally:
#     loop.close()

# radio_settings = {
#     "port": "/dev/ttyUSB3",
#     "rate": 9600,
# }
#
# gps_settings = {
#     "port": "/dev/ttyUSB0",
#     "rate": 9600,
# }
#
# temp_settings = {
#     "port": "/dev/ttyACM0",
#     "rate": 9600,
# }

db_setting = {
    "file": "local_data.db"
}


async def main():
    # config.set_specific("radio", "port", "/dev/ttyUSB2")
    # config.set_specific("radio", "rate", 9600)
    config.set_specific("rfid", "port", "/dev/ttyACM0")
    config.set_specific("rfid", "rate", 9600)
    config.set_specific("db", "file", "local_data.db")

    rfid = RFIDInterface()

    # xbee = RadioInterface()
    # xbee.send_test_string("@ping xbee online")

    # msg_handler = MessageHandler()

    # xbee.send_test_string("@get_all_temp")

    # stopped = await asyncio.gather(msg_handler.propagate_message(), gps.log_location_and_time())
    # stopped = await msg_handler.propagate_message()

    stopped = await rfid.check_rfid()

    print(stopped)

    return "all async loops exited"


if __name__ == "__main__":
    output = asyncio.run(main())
    print(output)
