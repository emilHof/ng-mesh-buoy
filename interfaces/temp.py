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
