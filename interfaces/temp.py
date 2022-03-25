from interfaces.database import DBInterface
from interfaces.ports import Port
import asyncio


class TempInterface(Port):
    """ __init__ is called on initialization of every new DBHandler """

    def __init__(self):
        super().__init__("temp")
        self.log = True
        self.db = DBInterface()

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
                data = (index, temp)
                err = self.db.write_temp_to_db(data)
                if err is not None:
                    print(err)
                index += 1
                print("committed new "
                      "temp data to the database:", temp)
                await asyncio.sleep(10)
            else:
                await asyncio.sleep(60)