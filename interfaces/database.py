import asyncio
import datetime
import sqlite3

import config.config as config
from pkg.msgs.msg_types import SimpleMessage


class DBInterface:
    """ __init__ is called on initialization of every new DBHandler """

    def __init__(self, dep_queue: asyncio.Queue = None):
        parameters = config.config["db"]
        self.db_file = parameters["file"]
        self.make_tables()
        self.hasGPS = False
        self.gps = None
        self.check_for_entry = True
        self.dep_queue = dep_queue
        indices = self.fetch_indices()
        self.gps_index = indices[0][0]
        self.temp_index = indices[1][0]
        self.turb_index = indices[2][0]
        self.rfid_index = indices[3][0]
        self.accepted_tags = {
            "loca",
            "temp",
            "turb",
            "rfid",
        }

    """ settings returns the current name of the .db file """

    def settings(self) -> str:
        return self.db_file

    """ make all the tables for the database if they don't exist already """

    def make_tables(self):
        con = sqlite3.connect(self.db_file)
        cursor = con.cursor()

        create_gps_data_format = """CREATE TABLE IF NOT EXISTS
                                   loca(id INTEGER, loca TEXT, time TEXT)"""

        create_temp_data_format = """CREATE TABLE IF NOT EXISTS
                                    temp(id INTEGER, temp TEXT, time TEXT)"""

        create_turb_data_format = """CREATE TABLE IF NOT EXISTS
                                    turb(id INTEGER, turb TEXT, time TEXT)"""

        create_rfid_data_format = """CREATE TABLE IF NOT EXISTS
                                    rfid(id INTEGER, rfid TEXT, time TEXT)"""

        # execute all the commands
        cursor.execute(create_gps_data_format)
        cursor.execute(create_temp_data_format)
        cursor.execute(create_turb_data_format)
        cursor.execute(create_rfid_data_format)

        con.commit()
        con.close()

    def fetch_indices(self):
        conn = sqlite3.connect(self.db_file)  # Connecting to sqlite
        cursor = conn.cursor()  # Creating a cursor object using the cursor() method

        cursor.execute('''SELECT id from loca ORDER BY id DESC LIMIT 1''')  # Retrieving data
        gps_index = cursor.fetchone()  # Fetching 1st row from the table

        cursor.execute('''SELECT id from temp ORDER BY id DESC LIMIT 1''')  # Retrieving data
        temp_index = cursor.fetchone()  # Fetching 1st row from the table

        cursor.execute('''SELECT id from turb ORDER BY id DESC LIMIT 1''')  # Retrieving data
        turb_index = cursor.fetchone()  # Fetching 1st row from the table

        cursor.execute('''SELECT id from rfid ORDER BY id DESC LIMIT 1''')  # Retrieving data
        rfid_index = cursor.fetchone()  # Fetching 1st row from the table

        conn.close()  # Closing the connection
        if gps_index is None:
            gps_index = 0, 0
        if temp_index is None:
            temp_index = 0, 0
        if turb_index is None:
            turb_index = 0, 0
        if rfid_index is None:
            rfid_index = 0, 0

        result = [gps_index, temp_index, turb_index, rfid_index]
        return result

    """ write_data_to_db writes the passed tuple to the indicated table in the database"""

    def write_data_to_db(self, table: str, new_entry: tuple):
        con = sqlite3.connect(self.db_file)
        cursor = con.cursor()
        cursor.execute("""INSERT INTO {}(id, {}, time) VALUES(?, ?, ?)""".format(table, table), new_entry)
        con.commit()
        con.close()

    """ read_db returns the specified amount of latest entries of a specified table """

    def read_db(self, table, limit, debug: bool = False) -> (list, str):
        if table in self.accepted_tags:
            con = sqlite3.connect(self.db_file)
            cursor = con.cursor()
            cursor.execute('SELECT * FROM ' + table + ' ORDER BY id DESC LIMIT  ' + str(limit) + "")
            rows = cursor.fetchall()
            if debug:
                for row in rows:
                    print(row)
            return rows, None
        return [], "error: table not in database"

    async def check_latest(self, tables: []):
        conn = sqlite3.connect(self.db_file)  # Connecting to sqlite
        cursor = conn.cursor()  # Creating a cursor object using the cursor() method
        indices = {
            "loc": self.gps_index,
            "turb": self.turb_index,
            "temp": self.temp_index,
            "rfid": self.rfid_index,
        }

        last_indices = {table: indices[table] for table in tables}

        while True:
            while self.check_for_entry:
                for table in tables:
                    cursor.execute('''SELECT id from ''' + table + ''' ORDER BY id DESC LIMIT 1''')  # Retrieving Index
                    index = cursor.fetchone()
                    if index[0] > last_indices[table]:
                        cursor.execute('''SELECT * from ''' + table + ''' ORDER BY id DESC LIMIT 1''')  # Retrieving data
                        data = cursor.fetchone()

                        data_str = ""
                        for d in data:
                            data_str += str(d) + ","

                        time = datetime.datetime.now().strftime("%H:%M:%S")

                        packet = SimpleMessage("00", f't:00,{data_str}', time)
                        self.dep_queue.put_nowait(packet)
                        last_indices[table] += 1

                await asyncio.sleep(5)

            await asyncio.sleep(5)
