from interfaces.database import DBInterface
from interfaces.ports import Port
from interfaces.gps import GPSInterface
import asyncio


class RFIDInterface(Port):
    """ __init__ is called on initialization of every new RFIDInterface """

    def __init__(self):
        super().__init__("rfid")
        self.check = True
        self.db = DBInterface()
        self.index = self.db.rfid_index
        self.gps = None
        self.turbidity = None

    async def check_rfid(self):
        self.index += 1
        index = self.index
        s = self.uart
        while True:
            if self.check:
                """read a line and print."""
                rfid_sig = ""
                msg = s.read().decode()
                while msg != '\n':
                    rfid_sig += msg
                    msg = s.read().decode()
                # self.gps = GPSInterface()
                # time = self.gps.get_time()
                time = ""
                signal = (index, rfid_sig, time)
                err = self.db.write_rfid_to_db(signal)
                if err is not None:
                    print(err)
                index += 1
                print("committed new temp data to the database:", rfid_sig)
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(60)
