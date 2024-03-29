import serial
import config.config as config
from interfaces.rfid import RFIDInterface
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
    config.set_specific("rfid", "port", "/dev/ttyACM0")
    config.set_specific("rfid", "rate", 9600)
    config.set_specific("db", "file", "local_data.db")

    rfid = RFIDInterface(False)

    stopped = await rfid.check_rfid("turb")

    print(stopped)

    return "all async loops exited"


if __name__ == "__main__":
    output = asyncio.run(main())
    print(output)
