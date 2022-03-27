import config.config as config
import sqlite3


class DBInterface:
    """ __init__ is called on initialization of every new DBHandler """

    def __init__(self):
        parameters = config.config["db"]
        self.db_file = parameters["file"]
        self.make_tables()
        self.gps_index = self.fetch_indices()[0][0]
        self.temp_index = self.fetch_indices()[1][0]
        self.rfid_index = self.fetch_indices()[2][0]

    """ settings returns the current name of the .db file """

    def settings(self) -> str:
        return self.db_file

    def make_tables(self):
        con = sqlite3.connect(self.db_file)
        cursor = con.cursor()
        create_gps_data_format = """CREATE TABLE IF NOT EXISTS
                                   location_and_time(id INTEGER, location TEXT, time TEXT)"""
        create_temp_data_format = """CREATE TABLE IF NOT EXISTS
                                    temp(id INTEGER, temp TEXT)"""

        create_rfid_data_format = """CREATE TABLE IF NOT EXISTS
                                    rfid(id INTEGER, rfid TEXT, time TEXT)"""
        cursor.execute(create_gps_data_format)
        cursor.execute(create_temp_data_format)
        cursor.execute(create_rfid_data_format)
        con.commit()
        con.close()

    def fetch_indices(self):
        conn = sqlite3.connect(self.db_file)  # Connecting to sqlite
        cursor = conn.cursor()  # Creating a cursor object using the cursor() method
        cursor.execute('''SELECT id from location_and_time ORDER BY id DESC LIMIT 1''')  # Retrieving data
        gps_index = cursor.fetchone()  # Fetching 1st row from the table
        cursor.execute('''SELECT id from temp ORDER BY id DESC LIMIT 1''')  # Retrieving data
        temp_index = cursor.fetchone()  # Fetching 1st row from the table
        cursor.execute('''SELECT id from rfid ORDER BY id DESC LIMIT 1''')  # Retrieving data
        rfid_index = cursor.fetchone()  # Fetching 1st row from the table
        conn.close()  # Closing the connection
        if gps_index is None:
            gps_index = 0, 0
        if temp_index is None:
            temp_index = 0, 0
        if rfid_index is None:
            rfid_index = 0, 0
        result = [gps_index, temp_index, rfid_index]
        return result

    """ write_loc_to_db writes the passed tuple to the location and time table in the database"""

    def write_loc_to_db(self, new_entry: tuple):
        con = sqlite3.connect(self.db_file)
        cursor = con.cursor()
        cursor.execute("""INSERT INTO location_and_time(id, location, time) VALUES(?, ?, ?)""", new_entry)
        con.commit()
        con.close()

    """ write_temp_to_db writes the passed tuple to the temp table in the database"""

    def write_temp_to_db(self, new_entry: tuple):
        con = sqlite3.connect(self.db_file)
        cursor = con.cursor()
        cursor.execute("""INSERT INTO temp(id, temp) VALUES(?, ?)""", new_entry)
        con.commit()
        con.close()

    """ write_rfid_to_db writes the passed tuple to the rfid table in the database"""

    def write_rfid_to_db(self, new_entry: tuple):
        con = sqlite3.connect(self.db_file)
        cursor = con.cursor()
        cursor.execute("""INSERT INTO rfid(id, rfid, time) VALUES(?, ?, ?)""", new_entry)
        con.commit()
        con.close()

    """ read_loc_db returns all of the entries in the location and time table of the database """

    def read_loc_db(self) -> list:
        con = sqlite3.connect(self.db_file)
        cursor = con.cursor()
        cursor.execute('SELECT * FROM location_and_time')
        print("trying to fetch entries")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        return rows

    """ read_temp_db returns all of the entries in the temp table of the database """

    def read_temp_db(self) -> list:
        con = sqlite3.connect(self.db_file)
        cursor = con.cursor()
        cursor.execute('SELECT * FROM temp')
        print("trying to fetch entries")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        return rows
