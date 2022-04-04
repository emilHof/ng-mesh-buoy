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
            if self.check:
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

                err = self.db.write_rfid_to_db(rfid_entry)
                print("committed new rfid data to the database:" + rfid_sig[:-2] + time)

                # checks which secondary sensor is stacked on top of the rfid sensor
                if sensor == "turb":
                    err = self.db.write_turb_to_db(sensor_entry)
                    print("committed new turb data to the database:" + sensor_data[:-2] + time)
                elif sensor == "temp":
                    err = self.db.write_temp_to_db(sensor_entry)
                    print("committed new temp data to the database:" + sensor_data[:-2] + time)

                if err is not None:
                    print(err)

                index += 1

                await asyncio.sleep(3)
            else:
                await asyncio.sleep(60)
