from interfaces.database import DBInterface
from interfaces.ports import Port
from interfaces.gps import get_time_sync
from datetime import datetime
import asyncio


class TempInterface(Port):
    """ __init__ is called on initialization of every new TempInterface """

    def __init__(self):
        super().__init__("temp")
        self.log = True  # set this to turn on or off to toggle logging
        self.hasGPS = False  # set this to True when there is a GPS connected
        self.db = DBInterface()
        self.gps = None

    def get_temp(self) -> str:
        s = self.uart
        """
            read a line and print.
            """
        text = ""
        msg = s.read().decode()
        while msg != '\n':
            text += msg
            msg = s.read().decode()
        return text

    async def log_temp(self):
        s = self.uart
        self.db.temp_index += 1
        index = self.db.temp_index

        while True:
            if self.log:
                """read a line and print."""
                temp = ""
                msg = s.read().decode()
                while msg != '\n':
                    temp += msg
                    msg = s.read().decode()

                # check if there is a GPS connected
                if self.hasGPS:
                    time = get_time_sync().strftime("%H:%M:%S")  # if yes then use the GPS time
                else:
                    time = datetime.now().strftime("%H:%M:%S")  # if no use built-in time

                data = (index, temp, time)
                err = self.db.write_temp_to_db(data)
                if err is not None:
                    print(err)
                index += 1
                print("committed new temp data to the database:", temp)
                await asyncio.sleep(10)
            else:
                await asyncio.sleep(60)
