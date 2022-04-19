from interfaces.database import DBInterface
from interfaces.ports import Port
from interfaces.gps import get_time_sync
from datetime import datetime
import asyncio


class RFIDInterface(Port):
    """ __init__ is called on initialization of every new RFIDInterface """

    def __init__(self, gps):
        super().__init__("rfid")
        self.check = True
        self.hasGPS = gps
        self.turbidity = None
        self.db = DBInterface()
        self.index = self.db.rfid_index

    async def check_rfid(self, sensor):  # the sensor parameter lets you specify the stacked sensor
        self.index += 1
        index = self.index
        s = self.uart

        while True:
            if self.check and s.inWaiting() > 0:
                """read a line and print."""

                rfid_sig = ""
                sensor_data = ""

                msg = s.read().decode()

                while msg != '\n':
                    rfid_sig += msg
                    msg = s.read().decode()

                msg = s.read().decode()

                while msg != '\n':
                    sensor_data += msg
                    msg = s.read().decode()

                if self.hasGPS:
                    time = get_time_sync().strftime("%H:%M:%S")
                else:
                    now = datetime.now()
                    time = str(now.hour) + " " + str(now.minute) + " " + str(now.second)

                rfid_entry = (index, rfid_sig[:-2], time)
                sensor_entry = (index, sensor_data[:-2], time)

                self.db.write_data_to_db("rfid", rfid_entry)
                self.db.write_data_to_db(sensor, sensor_entry)
                print("committed new rfid data to the database: {}, at {}".format(rfid_sig[:-2], time))
                print("committed new {} data to the database: {}, at {}".format(sensor, sensor_data[:-2], time))

                index += 1

                await asyncio.sleep(3)
            else:
                await asyncio.sleep(5)
