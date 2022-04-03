from interfaces.database import DBInterface
from interfaces.ports import Port
from interfaces.gps import get_time_sync
from datetime import datetime
import asyncio


class RFIDInterface(Port):
    """ __init__ is called on initialization of every new RFIDInterface """

    def __init__(self):
        super().__init__("rfid")
        self.check = True
        self.hasGPS = False
        self.gps = None
        self.turbidity = None
        self.db = DBInterface()
        self.index = self.db.rfid_index

    async def check_rfid(self):
        self.index += 1
        index = self.index
        s = self.uart

        while True:
            if self.check:
                """read a line and print."""

                rfid_sig = ""
                turb_data = ""

                msg = s.read().decode()

                while msg != '\n':
                    rfid_sig += msg
                    msg = s.read().decode()

                msg = s.read().decode()

                while msg != '\n':
                    turb_data += msg
                    msg = s.read().decode()

                if self.hasGPS:
                    time = get_time_sync().strftime("%H:%M:%S")
                else:
                    now = datetime.now()
                    time = str(now.hour) + " " + str(now.minute) + " " + str(now.second)

                rfid_entry = (index, rfid_sig, time)
                turb_entry = (index, turb_data, time)

                err = self.db.write_rfid_to_db(rfid_entry)
                err = self.db.write_turb_to_db(turb_entry)

                if err is not None:
                    print(err)

                index += 1

                # print("committed new rfid data to the database:" + rfid_sig)
                # print(time)
                # print("committed new turb data to the database:" + turb_data)
                # print(time)

                await asyncio.sleep(3)
            else:
                await asyncio.sleep(60)
